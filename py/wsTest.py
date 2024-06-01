#!/usr/bin/env python3

TIMEOUT=10

try:
    import asyncio, websockets,json
except ImportError as e:
    print(f"Import Error: {e}\nPlease re-Install the Extension.\nPress Enter to exit.")
    input()
    exit(1)

async def timelyTask(ws):

    try:
        for i in range(100, -1, -1):
            await sendMsg(ws,'{"ctrl":"msg","data":"'+str(i)+'"}')
            if (i==80):
                await sendMsg(ws,'{"ctrl":"msg","data":"done"}')
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        await sendMsg(ws,'{"ctrl":"msg","data":"timelyTask was cancelled"}')

task = None

async def sendMsg(ws,msg):
    if ws.open:
        try:
            await asyncio.wait_for(ws.send(msg),TIMEOUT)
        except websockets.exceptions.ConnectionClosedOK:
            print("Connection Closed: connection lost to client")
            if task:
                    task.cancel
            print(f"running task canceled")
        except asyncio.TimeoutError:  # Catch the timeout error
            print(f"Send Message: No connection for over {TIMEOUT} seconds, stopping server")
            loop.stop()  # Stop the event loop
        except Exception as e:
            print(f"Unexpected error: {e}")

async def handle_message(ws):
    global task
    while True:
        if ws.open:
            try:
                print("Waiting for message")
                message = await asyncio.wait_for(ws.recv(), TIMEOUT)
                ms=f"Received message"
                await sendMsg(ws,'{"ctrl":"msg","data":"'+ms+'"}') # receives string like {ctrl:"msg",data:"start Processing"}
                try:
                    data = json.loads(message)
                    # Process the data here
                    match data['ctrl']:
                        case 'msg':
                            ms=f"message received"
                            await sendMsg(ws,'{"ctrl":"msg","data":"'+ms+'"}')
                            if task:
                                task.cancel()
                            task = asyncio.create_task(timelyTask(ws))
                        case 'ctrl':
                            match data['data']:
                                case 'stop':
                                    if task:
                                        task.cancel()
                                case 'restart':
                                    #restart task
                                    if task:
                                        task.cancel()
                                    task = asyncio.create_task(timelyTask(ws))
                        case _:
                            await sendMsg(ws,'{"ctrl":"msg","data":"unknown message received"}')

                except json.JSONDecodeError as e:
                    ms=f"Error decoding JSON: {e}"
                    await sendMsg(ws,'{"ctrl":"msg","data":"'+ms+'"}')
            except websockets.exceptions.ConnectionClosedOK:
                print("Connection closed normally")
                if task:
                    task.cancel
                print(f"Connection Closed: connection lost to client\nrunning task canceled")
                break
            except asyncio.TimeoutError:  # Catch the timeout error
                print(f"No connection for over {TIMEOUT} seconds, stopping server")
                loop.stop()  # Stop the event loop
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

            if task and not task.done():  # Check if the previous task is still running
                    print("Previous task is still running, waiting for it to finish")
                    await task  # Wait for the previous task to finish








start_server = websockets.serve(handle_message, "localhost", 11616)


# Create and set an event loop
loop = asyncio.get_event_loop()
# Run the server
try:
    loop.run_until_complete(start_server)
    loop.run_forever()
finally:
    # Cancel all tasks and stop the event loop when the server is stopped
    for task in asyncio.all_tasks(loop):
        task.cancel()
    loop.stop()
