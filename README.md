![logo](static/apple-touch-icon.png)
# 🗓️ Deta Event Queue
> 🏄  **You can deploy this api completely free for any purpose and without limits on Deta.Sh** Just click the link below 🛠️  
>   
[![Deploy](https://button.deta.dev/1/svg)](https://go.deta.dev/deploy?repo=https://github.com/mehmetcanfarsak/DetaEventQueue)

> Simple, reliable and free Event Queue Api. 
> 
> 🔍 Check it on [https://DetaEventQueue.deta.dev](https://DetaEventQueue.deta.dev "https://DetaEventQueue.deta.dev")  **without any limits 😈**
> 
> ⏩ Example Usage:  [https://detaeventqueue.deta.dev/docs#/Send%20Your%20Event/receive_event_receive_event_post](https://detaeventqueue.deta.dev/docs#/Send%20Your%20Event/receive_event_receive_event_post)


## Features and Advantages
* ✅ Simple and powerfull for any type of app
* 🐳 Capable of handling over 2 000 000 events per day.
* ⏳️ Delaying execution time.
* 👌 You don't have to use DetaEventQueue for just apps in Deta. You can use it in anywhere you want such as in Docker Container, an instance in Aws, DigitalOcean etc.
* 🕐 Don't make your visitor wait for long-running processes.
* 🏎️ Increase your page speed easily.
* 🔁 Automatic retry if fails.
* 💻 Serverless so yo don't have to hassle with servers.
* 🏷️ Tagging events.
* 🏁 Get result of the event after execution.

[![Demo Image](static/img.png)](https://DetaEventQueue.deta.dev)

## For Demo:

* Go to: [https://DetaEventQueue.deta.dev](https://DetaEventQueue.deta.dev)
* **Password:** demo

### [📝Test It Now With a Simple Request](https://DetaEventQueue.deta.dev)

## Use Cases
- Sending an email after signup that takes about 3 seconds
- Background jobs based on events such as ``ticket created``, ``order received``, ``order shipped`` etc.
- Process data of the customer that takes time.
- Creating reports to users.
- Creating big files.

## How It Works
1. Send your events details to ``/receive_event`` endpoint.
   1. ``url_to_send_request`` parameter will be called when execution the event. (Which can be something like``https://example.com/url-to-call-for-the-event``)
   2. _Optional Parameters:_
      1. ``event_tags``: **Default: []** Send tags of the event. (Example: ``["my-first-tag","My Second Tag"]``)
      2. ``call_url_after``: **Default: 0** Delay the execution of the event.   (For example send parameter as ``300`` if you want to delay 5 minutes)
      3. ``timeout_for_request``: **Default: 5** Change how many seconds to wait before timeout. (Can be from 1 to 6)
      4. ``max_try_count``: **Default: 3** Change how many times to try. (Must be bigger or equal to 1)
2. A cron which runs every minute will get events that has status of ``waiting_execution``.
3. Try to send get request to the url.
4. If url responds ``within the timeout limits and a status code less then 300.``  such as ``200`` or ``201``
   1. It will change  event as ``success``
   2. Otherwise: it will retry after a minute
5. Status and details of any event can be checked at ``/get-event`` endpoint
6. **Note:** events with status of ``success`` and ``max_try_count_reached`` is deleted after 24 hours.

## Deployment
* It's not rocket science. Just click the button below  ⬇️
[![Deploy](https://button.deta.dev/1/svg)](https://go.deta.dev/deploy?repo=https://github.com/mehmetcanfarsak/DetaEventQueue)

## How Event Key is Given?
* First Deta Base sorts data in key field from small to largest.
* So in order to get events in right sorting
* We subtract 100000000000 from the timestamp (when the event should be executed) 
* Then we add uuid4 to the result (in order to prevent conflict of 2 events)

### Check Api Documantation below: ⬇️

> **_Swagger UI:_**  [https://DetaEventQueue.deta.dev/docs](https://DetaEventQueue.deta.dev/docs "https://DetaEventQueue.deta.dev/docs")

> **_ReDoc:_** [https://DetaEventQueue.deta.dev/redoc](https://DetaEventQueue.deta.dev/redoc "https://DetaEventQueue.deta.dev/redoc")

## 💁 **Example Projects** Using with Deta Event Queue :
* [https://FormToEmailService.deta.dev](https://FormToEmailService.deta.dev)
* [https://github.com/mehmetcanfarsak/FormToEmailService](https://github.com/mehmetcanfarsak/FormToEmailService)

## Contributing  

> Feel Free to contribute and add anything you want 😊  
> I'm checking pull requests daily. 




