#!/usr/bin/env python3

try:
    import os,tempfile,json,librosa,matplotlib.pyplot as plt,numpy as np
except ImportError as e:
    print(f"Import Error: {e}\nPlease re-Install the Extension.\nPress Enter to exit.")
    input()
    exit(1)

cname=""
sr=22050    # default sample rate

tempPath= tempfile.gettempdir()+"\\Adobe\\Premiere Pro\\extensions\\SmartCut\\"
lockfile = open(tempPath+"lockfile.lck", "w")
lockfile.write("lock")
print(f"Starting Processing Audio\nTarget Directory: {tempPath}\n")

# Defining Functions

def preprocess_audio(y_stereo):
    print(f"starting Pre-Processing Audio.\n.\n.\n.\n")
    y_harm, y_perc = librosa.effects.hpss(y_stereo)
    plt.figure( dpi=100,figsize=(18.5/2, 10.5/2) )
    librosa.display.waveshow(y_harm, sr=sr, color="blue",alpha=0.25)
    librosa.display.waveshow(y_perc, sr=sr, color="red", alpha=0.5)
    plt.title('Signal Separation')
    plt.savefig(tempPath+cname+" - preProcess - Signal-Separation.png")
    plt.close()
    y=reduce_Average(y_perc, sr, 'preProcess')
    return y

def reduce_Threshold(y_stereo, threshold):
    print(f"\tstarting Threshold Reduction.\n\t.\n\t.\n\t.\n")
    max = np.max(y_stereo)
    threshold =max* ( threshold/100 )
    y_stereo_trimmed = np.where(y_stereo <= max-threshold, 0, y_stereo)
    plt.figure(dpi=100, figsize=(18.5/2, 10.5/2))
    librosa.display.waveshow(y_stereo, sr=sr, color="blue", alpha=0.25)
    librosa.display.waveshow(y_stereo_trimmed, sr=sr, color="red", alpha=0.5)
    plt.title("Trimmed Signal")
    plt.savefig(tempPath +cname+" - trimSignal.png")
    plt.close()
    return y_stereo_trimmed


def reduce_Average(y, sr, process):
    print(f"\tstarting Average-Threshold Reduction.\n\t.\n\t.\n\t.\n")
    avg = np.mean(y)*1.25
    y_trimmed = np.where(y <= avg, 0, y)
    plt.figure(dpi=100, figsize=(18.5/2, 10.5/2))
    librosa.display.waveshow(y, sr=sr, color="blue", alpha=0.25)
    librosa.display.waveshow(y_trimmed, sr=sr, color="red", alpha=0.5)
    plt.title("Average Threshold-reduced Signal")
    plt.savefig(tempPath +cname+" - " + process + " - AverageThreshold.png")
    plt.close()
    return y_trimmed

def reduce_TempF(y_stereo,threshold):
    print(f"\tstarting Temporal-Feature Reduction.\n\t.\n\t.\n\t.\n")
    # Calculate first-order difference
    coef=(threshold/100)
    y_preemph = librosa.effects.preemphasis(y_stereo,coef=coef)
    # Square the differences
    result = y_preemph ** 2

    plt.figure( dpi=100,figsize=(18.5/2, 10.5/2) )
    librosa.display.waveshow(y_stereo, sr=sr, color="blue",alpha=0.25)
    librosa.display.waveshow(result, sr=sr, color="red",alpha=0.5)
    plt.title("Temporal Feature Reduction")
    plt.savefig(tempPath+cname+" - Reduction - TemporalFeature.png")
    plt.close()
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
    plt.figure( dpi=100,figsize=(18.5/2, 10.5/2) )
    librosa.display.waveshow(onset_env, sr=sr, color="red")
    plt.title("Onset Strength")
    plt.savefig(tempPath+cname+" - OnsetStrength.png")
    plt.close()
    times = librosa.times_like(onset_env, sr=sr)
    onset_env = librosa.to_mono(onset_env)
    onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
    plt.figure( dpi=100,figsize=(18.5/2, 10.5/2) )
    plt.plot(times, onset_env, label='Onset strength')
    plt.vlines(times[onset_frames], 0, onset_env.max(), color='r', alpha=0.9,linestyle='--', label='Onsets')
    plt.title("Onset Strength and Onsets")
    plt.savefig(tempPath+cname+" - OnsetStrengthOnsets.png")
    plt.close()

    return onset_frames

def peak_detection(y_reduced, threshold):
    print(f"starting Onset Detection Process.\n\t.\n\t.\n\t.\n")
    y_reduced_post=postprocess_audio(y_reduced,threshold)
    peaks = select_peaks(y_reduced_post)
    return peaks

arg=""

if os.path.exists(tempPath+"arg.json"):
    argfile = open(tempPath+"arg.json", "r")
    arg = argfile.read()
    argfile.close()


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
    #cconvert audio-frames to seconds
    peaks = librosa.frames_to_time(peaks, sr=sr)
    peaks=peaks.tolist()
    clip_processed={"name":cname,"peaks":peaks,"start":clip["start"],"indelay":clip["indelay"],"end":clip["end"]}
    clips_processed.append(clip_processed)

# export peaks to json
jsn_processed={"clipdata":clips_processed,"track":track}
jsn_processed=json.dumps(jsn_processed)

# write jsn_processed to tempPath
processedfile = open(tempPath+"onsets.json", "w")
processedfile.write(jsn_processed)
processedfile.close()

print(f"\nProcessing finished.\nPress Enter to exit.")
ex=input()

lockfile.close()
os.remove(tempPath+"lockfile.lck")
exit(0)