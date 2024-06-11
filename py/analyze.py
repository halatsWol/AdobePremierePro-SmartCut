#!/usr/bin/env python3


import os,datetime


CRITICAL = 0
ERROR = 1
STATUS = 2
DEBUG = 3
loglvl=STATUS	# default log level
logPath=str(os.getenv('APPDATA'))+"\\Marflow Software\\SmartCut\\logs\\"
logfile = logPath + "Log_Analyse_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"


def log(msg,lvl=1):
    if lvl<CRITICAL & lvl>DEBUG: lvl=1
    logType=""
    if lvl<=int(loglvl):
        match lvl:
            case 0: logType="CRITICAL ERROR"
            case 1: logType="ERROR"
            case 2: logType="STATUS"
            case 3: logType="DEBUG"
        msg=f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\t{logType}\n{msg}\n"
        if not os.path.exists(logPath):
            try:
                os.makedirs(logPath)
            except Exception as e:
                print(f"Error creating log directory:\n{e}\n\ncausing Log-Message:\n{msg}\nPress Enter to exit.")
                input()
                exit(1)
        with open(logfile, 'a') as f:
            f.write(msg + '\n')

try:
    import json,librosa,matplotlib.pyplot as plt,numpy as np,asyncio, websockets
    from numpy import mat
except ImportError as e:
    log(f"Import Error: {e}",CRITICAL)
    exit(1)


cname=""
sr=22050    # default sample rate
port=11616  # default port
TIMEOUT=60  # default timeout

ws=None
task = None

## Read Config

def readConfig():
    global sr,port,loglvl
    configPath=str(os.getenv('APPDATA'))+"\\Marflow Software\\SmartCut\\config\\config.conf"
    if os.path.exists(configPath):
        try:
            with open(configPath) as f:
                data = json.load(f)
                port=data["port"]
                loglvl=data["loglvl"]
                log(f"Config file read successfully",DEBUG)
        except Exception as e:
            log(f"Error reading config file: {e}\nWorking with defaults.",ERROR)
    else:
        log(f"Config file not found at: {configPath}\nWorking with defaults.",ERROR)








async def preprocess_audio(y_stereo,ws):
    await sendMsg("status",f"starting Pre-Processing Audio.\n.\n.\n.\n",ws)
    y_harm, y_perc = librosa.effects.hpss(y_stereo)
    # plt.figure( dpi=100,figsize=(18.5/2, 10.5/2) )
    # librosa.display.waveshow(y_harm, sr=sr, color="blue",alpha=0.25)
    # librosa.display.waveshow(y_perc, sr=sr, color="red", alpha=0.5)
    # plt.title('Signal Separation')
    # plt.savefig(tempPath+cname+" - preProcess - Signal-Separation.png")
    # plt.close()
    y=await reduce_Average(y_perc, sr, 'preProcess',ws)
    return y

async def reduce_Threshold(y_stereo, threshold,ws):
    await sendMsg("status",f"\tstarting Threshold Reduction.\n\t.\n\t.\n\t.\n",ws)
    max = np.max(y_stereo)
    threshold =max* ( threshold/100 )
    y_stereo_trimmed = np.where(y_stereo <= max-threshold, 0, y_stereo)
    # plt.figure(dpi=100, figsize=(18.5/2, 10.5/2))
    # librosa.display.waveshow(y_stereo, sr=sr, color="blue", alpha=0.25)
    # librosa.display.waveshow(y_stereo_trimmed, sr=sr, color="red", alpha=0.5)
    # plt.title("Trimmed Signal")
    # plt.savefig(tempPath +cname+" - trimSignal.png")
    # plt.close()
    return y_stereo_trimmed


async def reduce_Average(y, sr, process,ws):
    await sendMsg("status",f"\tstarting Average-Threshold Reduction.\n\t.\n\t.\n\t.\n",ws)
    avg = np.mean(y)*1.25
    y_trimmed = np.where(y <= avg, 0, y)
    # plt.figure(dpi=100, figsize=(18.5/2, 10.5/2))
    # librosa.display.waveshow(y, sr=sr, color="blue", alpha=0.25)
    # librosa.display.waveshow(y_trimmed, sr=sr, color="red", alpha=0.5)
    # plt.title("Average Threshold-reduced Signal")
    # plt.savefig(tempPath +cname+" - " + process + " - AverageThreshold.png")
    # plt.close()
    return y_trimmed

async def reduce_TempF(y_stereo,threshold,ws):
    await sendMsg("status",f"\tstarting Temporal-Feature Reduction.\n\t.\n\t.\n\t.\n",ws)
    # Calculate first-order difference
    coef=(threshold/100)
    y_preemph = librosa.effects.preemphasis(y_stereo,coef=coef)
    # Square the differences
    result = y_preemph ** 2

    # plt.figure( dpi=100,figsize=(18.5/2, 10.5/2) )
    # librosa.display.waveshow(y_stereo, sr=sr, color="blue",alpha=0.25)
    # librosa.display.waveshow(result, sr=sr, color="red",alpha=0.5)
    # plt.title("Temporal Feature Reduction")
    # plt.savefig(tempPath+cname+" - Reduction - TemporalFeature.png")
    # plt.close()
    return result


async def reduction_process(y_stereo, method, threshold,ws):
    await sendMsg("status","starting Audio-Reduction:\n",ws)
    match method:
        case "thB":           # Threshold-based
            return await reduce_Threshold(y_stereo, threshold,ws)
        case "sig_tempF":     # Signal-time-based
            return await reduce_TempF(y_stereo,threshold,ws)


async def postprocess_audio(y_reduced, threshold,ws):
    await sendMsg("status",f"\tstarting postprocessing.\n\n",ws)
    y_reduced=await reduce_Average(y_reduced, sr, 'postProcess',ws)
    return y_reduced

async def select_peaks(data,ws):
    await sendMsg("status",f"\tstarting Detecting Onset-Times.\n\n",ws)
    onset_env = librosa.onset.onset_strength(y=data, sr=sr, aggregate=np.median, fmax=8000, n_mels=256)
    # plt.figure( dpi=100,figsize=(18.5/2, 10.5/2) )
    # librosa.display.waveshow(onset_env, sr=sr, color="red")
    # plt.title("Onset Strength")
    # plt.savefig(tempPath+cname+" - OnsetStrength.png")
    # plt.close()
    times = librosa.times_like(onset_env, sr=sr)
    onset_env = librosa.to_mono(onset_env)
    onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
    # plt.figure( dpi=100,figsize=(18.5/2, 10.5/2) )
    # plt.plot(times, onset_env, label='Onset strength')
    # plt.vlines(times[onset_frames], 0, onset_env.max(), color='r', alpha=0.9,linestyle='--', label='Onsets')
    # plt.title("Onset Strength and Onsets")
    # plt.savefig(tempPath+cname+" - OnsetStrengthOnsets.png")
    # plt.close()

    return onset_frames

async def peak_detection(y_reduced, threshold,ws):
    await sendMsg("status",f"starting Onset Detection Process.\n\t.\n\t.\n\t.\n",ws)
    y_reduced_post=await postprocess_audio(y_reduced,threshold,ws)
    peaks = await select_peaks(y_reduced_post,ws)
    return peaks

async def process_data(ws,arg):


    # if os.path.exists(tempPath+"arg.json"):
    #     argfile = open(tempPath+"arg.json", "r")
    #     arg = argfile.read()
    #     argfile.close()

    log(f"start processing: {arg}",DEBUG)

    arg=arg.replace("\\", "\\\\")
    sr = int(json.loads(arg)["sr"])
    clipdata = json.loads(arg)["clipdata"]
    track=json.loads(arg)["track"]
    threshold=(float(json.loads(arg)["threshold"]))

    method=json.loads(arg)["method"]
    preprocess=json.loads(arg)["preprocess"]
    clips_processed=[]
    for clip in clipdata:
        cname=clip["name"].rsplit( ".", 1 )[ 0 ]
        audio_path=clip["path"]
        audio_path=audio_path.replace("\\", "\\\\")
        y_stereo, sr = librosa.load(clip["path"], mono=False, offset=float(clip["indelay"]), sr = sr, duration=float(clip["end"])-float(clip["indelay"]))
        if preprocess:
            y_stereo = await preprocess_audio(y_stereo,ws)

        y_reduced = await reduction_process(y_stereo, method, threshold,ws)
        peaks = await peak_detection(y_reduced, threshold,ws)
        #convert audio-frames to seconds
        peaks = librosa.frames_to_time(peaks, sr=sr)
        peaks=peaks.tolist()
        clip_processed={"name":cname,"peaks":peaks,"start":clip["start"],"indelay":clip["indelay"],"end":clip["end"]}
        clips_processed.append(clip_processed)

    # export peaks to json
    jsn_processed={"clipdata":clips_processed,"track":track}
    jsn_processed=json.dumps(jsn_processed)
    await sendMsg("data",jsn_processed,ws)
    # # write jsn_processed to tempPath
    # processedfile = open(tempPath+"onsets.json", "w")
    # processedfile.write(jsn_processed)
    # processedfile.close()

    # print(f"\nProcessing finished.\nPress Enter to exit.")
    # ex=input()

    # lockfile.close()
    # os.remove(tempPath+"lockfile.lck")



def is_json_string(str):
    try:
        json.loads(str)
        return True
    except json.JSONDecodeError:
        return False




async def sendMsg(ctrl,msg,ws):
    msg = msg.replace('\n', '<br>').replace('\t', '&emsp;')
    if is_json_string(msg):
        msg = msg.replace('"', '\\"')
    msg='{"ctrl":"'+ctrl+'","data":"'+msg+'"}'
    if loglvl==DEBUG:
        print(msg)
    if ws is not None and ws.open:
        try:
            # msg=json.loads(msg)
            await asyncio.wait_for(ws.send(msg),TIMEOUT)
            log(f"Sent message: {msg}",DEBUG)
        except websockets.exceptions.ConnectionClosedOK:
            log("Connection Closed: connection lost to client",ERROR)
            if task:
                    task.cancel
            log(f"running task canceled",STATUS)
        except asyncio.TimeoutError:  # Catch the timeout error
            log(f"Send Message: No connection for over {TIMEOUT} seconds, stopping server",STATUS)
            loop.stop()  # Stop the event loop
        except Exception as e:
            log(f"Unexpected error: {e}\n\n\tat: Send Message of Type\n\t\'{ctrl}'\n\twith content:\n\t\t'{msg}'\n",ERROR)


    else:
        log("Connection Closed: no open Connections to client",ERROR)
        if task:
            task.cancel
        log(f"running task canceled",STATUS)

async def handle_message(ws):
    global task

    while True:
        if ws is not None and ws.open:
            try:
                log("Waiting for message",DEBUG)
                message = await asyncio.wait_for(ws.recv(), TIMEOUT)
                log(f"received message: {message}",DEBUG)
                try:
                    data = json.loads(message)
                    # Process the data here
                    match data['ctrl']:
                        case 'msg':
                            match data['data']:
                                case 'start':
                                    await sendMsg("msg","started",ws)
                                case 'Data Received':
                                    await sendMsg("ctrl","done",ws)
                        case 'data':
                            if task:
                                task.cancel()
                            task = asyncio.create_task(process_data(ws,data['data']))
                        case 'ctrl':
                            match data['data']:
                                case 'stop':
                                    if task:
                                        task.cancel()
                                    loop.stop()
                        case _:
                            await sendMsg("msg","1 unknown message received",ws)
                except json.JSONDecodeError as e:
                    ms=f"Error decoding JSON: {e}"
                    await sendMsg("msg",ms,ws)
            except websockets.exceptions.ConnectionClosedOK:
                log("Connection closed normally",STATUS)
                if task:
                    task.cancel
                break
            except asyncio.TimeoutError:  # Catch the timeout error
                log(f"No connection for over {TIMEOUT} seconds, stopping server",STATUS)
                loop.stop()  # Stop the event loop
                break
            except Exception as e:
                log(f"Unexpected error: {e}",ERROR)
                break
            if task and not task.done():  # Check if the previous task is still running
                    log("Previous task is still running, waiting for it to finish",DEBUG)
                    message = await ws.recv()
                    log(f"Received message\nmessage\n\t{message.replace('"', '\\"')}",DEBUG) # receives string like {ctrl:"msg",data:"start Processing"}
                    try:
                        pmsg= json.loads(message)
                        # Process the data here
                        match pmsg['data']:
                            case 'stop':
                                if task:
                                    task.cancel()
                                loop.stop()
                            case 'Data Received':
                                    await sendMsg("ctrl","done",ws)
                            case _:
                                await sendMsg("msg","Previous received message is of unknown content",ws)
                    except json.JSONDecodeError as e:
                        ms=f"Error decoding JSON: {e}"
                        await sendMsg("msg",ms,ws)
                    await task  # Wait for the previous task to finish
            elif task and task.done():
                log("Task finished",DEBUG)
            # else:
            #     await sendMsg("status","No task running, no task finished\n\tPlease stop and restart the Process.",ws)
        else:
            log("Connection Closed: no open Connections to client",ERROR)
            if task:
                task.cancel


if __name__ == "__main__":
    readConfig()
    start_server = websockets.serve(handle_message, "localhost", port)
    # Create and set an event loop
    loop = asyncio.get_event_loop()
    # Run the server
    try:
        loop.run_until_complete(start_server)
        loop.run_forever()
    except Exception as e:
        log(f"Error running server: {e}",CRITICAL)
        exit(1)
    finally:
        # Cancel all tasks if any remains and stop the event loop when the server is stopped
        for task in asyncio.all_tasks(loop):
            task.cancel()
        loop.stop()
        log("Server stopped",STATUS)
        exit(0)