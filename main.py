from deta import App, Deta
from fastapi import FastAPI, BackgroundTasks, HTTPException, status, Query
from fastapi.responses import RedirectResponse, FileResponse
from dotenv import load_dotenv
from time import sleep
import requests
from typing import Union
import datetime
from pydantic import BaseModel, AnyUrl, Field
from enum import Enum

from uuid import uuid4

from os import getenv

load_dotenv()
queue_name = getenv("QUEUE_NAME", '')
event_queue_db = Deta().Base(f'DetaEvent{queue_name}Queue')
finished_event_queue_db = Deta().Base(f'DetaFinishedEvent{queue_name}Queue')
ADMIN_PASSWORD=getenv("PASSWORD", "demo")

demo_credentials_part = ""
if (ADMIN_PASSWORD == "demo"):
    demo_credentials_part = """
### Demo Credentials    
* **Password:** demo

    """
description_of_fastapi = f"""

## Simple, reliable and free Event Queue Api.

{demo_credentials_part}



**ADMIN_PASSWORD** (which is asked on deployment) is used as password. 




## 💻 Deployment  
You can deploy your own instance of DetaEventQueue using the button below. You will need a [Deta](https://www.deta.sh/) account.  
[![Click Here To Deploy Your Own FreeEmailValidationApi  💻️](https://button.deta.dev/1/svg)](https://go.deta.dev/deploy?repo=https://github.com/mehmetcanfarsak/DetaEventQueue)

### ⌨️ Github Page:

> [https://github.com/mehmetcanfarsak/DetaEventQueue](https://github.com/mehmetcanfarsak/DetaEventQueue "https://github.com/mehmetcanfarsak/DetaEventQueue")


"""


app = App(FastAPI(title="🗓️ Deta Event Queue",description=description_of_fastapi,contact={"url": "https://github.com/mehmetcanfarsak", "Name": "Mehmet Can Farsak"}))


class ReceiveEventModel(BaseModel):
    url_to_send_request: AnyUrl = "https://example.com/url-to-call-for-the-event"
    call_url_after: int = Field(default=0,
                                description="This field can be set if you want to delay execution of the event. For example: you can set this field to 300 if you want to delay it 5 minutes.")
    max_try_count: int = Field(default=3,
                               description="This field determines how many times failed request should be repeated.",ge=1)
    timeout_for_request: int = Field(default=5, gt=0, le=6)
    event_tags: list = []


class EventStatus(str, Enum):
    waiting_execution = "waiting_execution"
    success = "success"
    max_try_count_reached = "max_try_count_reached"


class EventModel(BaseModel):
    key: str
    status: EventStatus
    created_at_utc: str
    try_count: int
    timestamp_for_execution_to_start: int
    url_to_send_request: AnyUrl = "https://example.com/url-to-call-for-the-event"
    call_url_after: int = Field(default=0,
                                description="This field can be set if you want to delay execution of the event. For example: you can set this field to 300 if you want to delay it 5 minutes.",
                                ge=0)
    max_try_count: int = Field(default=3,
                               description="This field determines how many times failed request should be repeated.",
                               gt=0, le=120)
    timeout_for_request: int = Field(default=5, gt=0, le=6)
    event_tags: list
    request_response_status_code: Union[int, None] = None
    request_response_body: Union[str, None] = None
    request_response_headers: Union[dict, None] = None


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/docs")


@app.post("/receive-event", response_model=EventModel, tags=["Send Your Event"])
def receive_event(event: ReceiveEventModel, password: str = Query("demo")):
    if (password != ADMIN_PASSWORD):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is wrong")
    current_datetime = datetime.datetime.now()
    event = event.__dict__

    event['status'] = "waiting_execution"
    event['try_count'] = 0
    event['created_at_utc'] = str(current_datetime)
    event['timestamp_for_execution_to_start'] = int(current_datetime.timestamp()) + event['call_url_after']
    key_integer_part = 100000000000 - (event['timestamp_for_execution_to_start'])
    # when we request deta base sorts from small to big
    event['key'] = str(key_integer_part) + " " + str(uuid4())

    event_queue_db.put(event)
    return EventModel(**event)


@app.get("/get-event", response_model=EventModel, tags=["Get Details of Event"])
def get_event(event_key: str = Query("Key of event which is returned in ")):
    event = event_queue_db.get(event_key)
    if (event == None):
        finished_event = finished_event_queue_db.get(event_key)
        if (finished_event == None):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=
            """Event Not Found. The can be 2 reason for this.
            1) Event can be successfully be dispatched and 24 hours has passed.
            2) Event key is wrong so there isn't any event with this key. """)
        return finished_event
    return event


@app.get("/get-count-of-events", tags=["Learn how many events waiting execution"])
def get_count_of_evets_in_queue(max_count_of_fetch_requests: int = Query(10, le=10, gt=0),
                                password: str = Query("demo")):
    if (password != ADMIN_PASSWORD):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is wrong")

    count_of_events = 0
    count_of_fetch_requests = 0
    while True:
        count_of_fetch_requests += 1
        fetch_response = event_queue_db.fetch()
        count_of_events += len(fetch_response.items)
        if (fetch_response.last == None):
            break
        if (count_of_fetch_requests > max_count_of_fetch_requests):
            return count_of_events
    return count_of_events


def execute_event(event):
    if (event['try_count'] >= event['max_try_count']):
        event_queue_db.delete(event['key'])
        event['status'] = "max_try_count_reached"  # todo bunuda düzgün yap
        finished_event_queue_db.put(event)
        return
    event['try_count'] += 1
    event_queue_db.put(event)
    try:
        print(event['url_to_send_request'])
        event_response = requests.get(event['url_to_send_request'], timeout=event['timeout_for_request'],
                                      allow_redirects=False)
        if (event_response.status_code < 300):
            event_queue_db.delete(event['key'])
            event['request_response_status_code'] = event_response.status_code
            event['request_response_body'] = event_response.text
            event['request_response_headers'] = dict(event_response.headers)
            finished_event_queue_db.put(event, expire_in=(24 * 60 * 60))
    except:
        pass
    return


@app.get("/dispatch-events", include_in_schema=False)
async def dispatch_events(password: str, last_key: str, concurrent_dispatch_count: int,
                          background_tasks: BackgroundTasks):
    if (password != ADMIN_PASSWORD):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is wrong")

    fetch_response = event_queue_db.fetch(limit=30, last=last_key)
    if (fetch_response.last != None and concurrent_dispatch_count < 50):
        background_tasks.add_task(requests.get,
                                  f"https://{getenv('DETA_PATH', 'demo')}.deta.dev/dispatch-events?concurrent_dispatch_count={(concurrent_dispatch_count + 1)}&last_key={fetch_response.last}&password={ADMIN_PASSWORD}")

    events = fetch_response.items
    for event in events:
        background_tasks.add_task(execute_event, event)

    return "OK"


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


@app.lib.cron()
def cron_job(event):
    last_key = str(100000000000 - int(datetime.datetime.now().timestamp()))
    requests.get(
        f"https://{getenv('DETA_PATH')}.deta.dev/dispatch-events?concurrent_dispatch_count=1&last_key={last_key}&password={ADMIN_PASSWORD}",
        timeout=9)
    return "Cron job run"
