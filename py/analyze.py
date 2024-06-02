#!/usr/bin/env python3


import os,datetime

CRITICAL = 0
ERROR = 1
STATUS = 2
INFO = 3
loglvl=STATUS	# default log level
logPath=str(os.getenv('LOCALAPPDATA'))+"\\MarflowSoftware\\SmartCut\\logs\\"
logfile = logPath + "Log_Analyse_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"

def log(msg,lvl=1):
    if lvl<CRITICAL or lvl>INFO: lvl=1
    logType=""

    if lvl<=loglvl:
        match lvl:
            case 0: logType="CRITICAL ERROR"
            case 1: logType="ERROR"
            case 2: logType="STATUS"
            case 3: logType="INFO"
        msg=f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\t{logType}\n{msg}\n"
        if not os.path.exists(logPath):
            try: os.makedirs(logPath)
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
    configPath=str(os.getenv('LOCALAPPDATA'))+"\\MarflowSoftware\\SmartCut\\config\\config.json"
    if os.path.exists(configPath):
        try:
            with open(configPath) as f:
                data = json.load(f)
                sr=data["sr"]
                port=data["port"]
                loglvl=data["loglvl"]
                log(f"Config file read successfully",INFO)
        except Exception as e:
            log(f"Error reading config file: {e}\nWorking with defaults.",ERROR)
    else:
        log(f"Config file not found at: {configPath}\nWorking with defaults.",ERROR)








def preprocess_audio(y_stereo):
    print(f"starting Pre-Processing Audio.\n.\n.\n.\n")
    y_harm, y_perc = librosa.effects.hpss(y_stereo)
    # plt.figure( dpi=100,figsize=(18.5/2, 10.5/2) )
    # librosa.display.waveshow(y_harm, sr=sr, color="blue",alpha=0.25)
    # librosa.display.waveshow(y_perc, sr=sr, color="red", alpha=0.5)
    # plt.title('Signal Separation')
    # plt.savefig(tempPath+cname+" - preProcess - Signal-Separation.png")
    # plt.close()
    y=reduce_Average(y_perc, sr, 'preProcess')
    return y

def reduce_Threshold(y_stereo, threshold):
    print(f"\tstarting Threshold Reduction.\n\t.\n\t.\n\t.\n")
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


def reduce_Average(y, sr, process):
    print(f"\tstarting Average-Threshold Reduction.\n\t.\n\t.\n\t.\n")
    avg = np.mean(y)*1.25
    y_trimmed = np.where(y <= avg, 0, y)
    # plt.figure(dpi=100, figsize=(18.5/2, 10.5/2))
    # librosa.display.waveshow(y, sr=sr, color="blue", alpha=0.25)
    # librosa.display.waveshow(y_trimmed, sr=sr, color="red", alpha=0.5)
    # plt.title("Average Threshold-reduced Signal")
    # plt.savefig(tempPath +cname+" - " + process + " - AverageThreshold.png")
    # plt.close()
    return y_trimmed

def reduce_TempF(y_stereo,threshold):
    print(f"\tstarting Temporal-Feature Reduction.\n\t.\n\t.\n\t.\n")
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


def reduction_process(y_stereo, method, threshold):
    print("starting Audio-Reduction:\n")
    match method:
        case "thB":           # Threshold-based
            return reduce_Threshold(y_stereo, threshold)
        case "sig_tempF":     # Signal-time-based
            return reduce_TempF(y_stereo,threshold)


def postprocess_audio(y_reduced, threshold):
    print(f"\tstarting postprocessing.\n\n")
    y_reduced=reduce_Average(y_reduced, sr, 'postProcess')
    return y_reduced

def select_peaks(data):
    print(f"\tstarting Detecting Onset-Times.\n\n")
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

def peak_detection(y_reduced, threshold):
    print(f"starting Onset Detection Process.\n\t.\n\t.\n\t.\n")
    y_reduced_post=postprocess_audio(y_reduced,threshold)
    peaks = select_peaks(y_reduced_post)
    return peaks

async def process_data(ws,arg):
    arg=""

    # if os.path.exists(tempPath+"arg.json"):
    #     argfile = open(tempPath+"arg.json", "r")
    #     arg = argfile.read()
    #     argfile.close()


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
            y_stereo = preprocess_audio(y_stereo)

        y_reduced = reduction_process(y_stereo, method, threshold)
        peaks = peak_detection(y_reduced, threshold)
        #convert audio-frames to seconds
        peaks = librosa.frames_to_time(peaks, sr=sr)
        peaks=peaks.tolist()
        clip_processed={"name":cname,"peaks":peaks,"start":clip["start"],"indelay":clip["indelay"],"end":clip["end"]}
        clips_processed.append(clip_processed)

    # export peaks to json
    jsn_processed={"clipdata":clips_processed,"track":track}
    jsn_processed=json.dumps(jsn_processed)
    await sendMsg('data',jsn_processed,ws)
    # # write jsn_processed to tempPath
    # processedfile = open(tempPath+"onsets.json", "w")
    # processedfile.write(jsn_processed)
    # processedfile.close()

    # print(f"\nProcessing finished.\nPress Enter to exit.")
    # ex=input()

    # lockfile.close()
    # os.remove(tempPath+"lockfile.lck")







async def sendMsg(ctrl,msg,ws):
    msg='{"ctrl":"'+ctrl+'","data":"'+msg+'"}'
    if ws.open:
        try:
            await asyncio.wait_for(ws.send(msg),TIMEOUT)
        except websockets.exceptions.ConnectionClosedOK:
            log("Connection Closed: connection lost to client",ERROR)
            if task:
                    task.cancel
            log(f"running task canceled",STATUS)
        except asyncio.TimeoutError:  # Catch the timeout error
            log(f"Send Message: No connection for over {TIMEOUT} seconds, stopping server",STATUS)
            loop.stop()  # Stop the event loop
        except Exception as e:
            log(f"Unexpected error: {e}",ERROR)

        log(f"Sent message: {msg}",INFO)
    else:
        log("Connection Closed: no open Connections to client",ERROR)
        if task:
            task.cancel
        log(f"running task canceled",STATUS)

async def handle_message(ws):
    global task

    while True:
        if ws.open:
            try:
                log("Waiting for message",INFO)
                message = await asyncio.wait_for(ws.recv(), TIMEOUT)
                ms=f"Received message"
                await sendMsg("msg",ms,ws) # receives string like {ctrl:"msg",data:"start Processing"}
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
                                    break
                        case _:
                            await sendMsg("msg","unknown message received",ws)

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
                    log("Previous task is still running, waiting for it to finish",INFO)
                    message = await ws.recv()
                    ms=f"Received message"
                    await sendMsg("msg",ms,ws) # receives string like {ctrl:"msg",data:"start Processing"}
                    try:
                        pmsg= json.loads(message)
                        # Process the data here
                        match pmsg['data']:
                            case 'stop':
                                if task:
                                    task.cancel()
                            case _:
                                await sendMsg("msg","unknown message received",ws)
                    except json.JSONDecodeError as e:
                        ms=f"Error decoding JSON: {e}"
                        await sendMsg("msg",ms,ws)
                    await task  # Wait for the previous task to finish



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
        # Cancel all tasks and stop the event loop when the server is stopped
        for task in asyncio.all_tasks(loop):
            task.cancel()
        loop.stop()
        log("Server stopped",STATUS)

    exit(0)