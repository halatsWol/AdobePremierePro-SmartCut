#!/usr/bin/env python3
try:
    import os
    import tempfile
    import json
    import librosa
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError as e:
    print(f"Import Error: {e}\n")
    print("Please re-Install the Extension.\n")
    print("Press Enter to exit.")
    input()
    exit(1)

cname=""

tempPath= tempfile.gettempdir()+"\\Adobe\\Premiere Pro\\extensions\\SmartCut\\"
lockfile = open(tempPath+"lockfile.lck", "w")
lockfile.write("lock")
print(f"Starting Processing Audio\nTarget Directory: {tempPath}\n")

def preprocess_audio(y_stereo):
    print(f"starting Pre-Processing Audio.\n.\n.\n.\n")
    y_harm, y_perc = librosa.effects.hpss(y_stereo)
    plt.figure( dpi=200,figsize=(18.5, 10.5) )
    librosa.display.waveshow(y_harm, sr=sr, color="blue",alpha=0.25)
    librosa.display.waveshow(y_perc, sr=sr, color="red", alpha=0.5)
    plt.title('Harmonic + Percussive')
    plt.savefig(tempPath+cname+" - preProcess.png")
    plt.close()
    y=reduce_Average(y_perc, sr)
    return y

def reduce_Threshold(y_stereo, threshold_db, sr):
    print(f"starting Threshold Reduction.\n.\n.\n.\n")
    max = np.max(y_stereo)
    threshold =max* ( threshold_db/100 )
    y_stereo_trimmed = np.where(y_stereo <= max-threshold, 0, y_stereo)
    plt.figure(dpi=200, figsize=(18.5, 10.5))
    librosa.display.waveshow(y_stereo, sr=sr, color="blue", alpha=0.25)
    librosa.display.waveshow(y_stereo_trimmed, sr=sr, color="red", alpha=0.5)
    plt.title("Trimmed Signal")
    plt.savefig(tempPath +cname+" - trimSignal.png")
    plt.close()
    return y_stereo_trimmed


def reduce_Average(y_stereo, sr):
    print(f"starting Average-Threshold Reduction.\n.\n.\n.\n")
    avg = np.mean(y_stereo)*1.25
    y_stereo_trimmed = np.where(y_stereo <= avg, 0, y_stereo)
    plt.figure(dpi=200, figsize=(18.5, 10.5))
    librosa.display.waveshow(y_stereo, sr=sr, color="blue", alpha=0.25)
    librosa.display.waveshow(y_stereo_trimmed, sr=sr, color="red", alpha=0.5)
    plt.title("Average Trimmed Signal")
    plt.savefig(tempPath +cname+" - AveTrimSignal.png")
    plt.close()
    return y_stereo_trimmed

def reduce_SignalTime(y_stereo):
    print(f"starting Signal-Time Reduction.\n.\n.\n.\n")
    plt.figure( dpi=200,figsize=(18.5, 10.5) )
    librosa.display.waveshow(y_stereo, sr=sr, color="red")
    plt.title("SignalTimed Signal")
    plt.savefig(tempPath+cname+" - SignalTime.png")
    plt.close()
    return y_stereo

def reduce_SignalSpectrum(y_stereo,threshold):
    print(f"starting Signal-Spectrum Reduction.\n.\n.\n.\n")
    coef=(threshold/100)
    y_stereo_reduced = librosa.effects.preemphasis(y_stereo,coef=coef)
    plt.figure( dpi=200,figsize=(18.5, 10.5) )
    librosa.display.waveshow(y_stereo, sr=sr, color="blue",alpha=0.25)
    librosa.display.waveshow(y_stereo_reduced, sr=sr, color="red", alpha=0.5)
    plt.title("Preemphasized Signal (Red)\nand Original Signal (Blue)")
    plt.savefig(tempPath+cname+" - preemphasizedSignal.png")
    plt.close()

    return y_stereo

def reduce_SignalTimeFrequency(y_stereo):
    print(f"starting Signal-Time-Frequency Reduction.\n.\n.\n.\n")
    librosa.display.waveshow(y_stereo, sr=sr, color="blue")
    plt.title("SignalTimeFrequency Signal")
    plt.savefig(tempPath+cname+" - reduce_SignalTimeFrequency.png")
    plt.close()
    return y_stereo

def reduction_process(y_stereo, method, threshold,sr):
    print("starting Audio-Reduction:\n")
    match method:
        case "thB":           # Threshold-based
            return reduce_Threshold(y_stereo, threshold,sr)
        case "sig_timeB":     # Signal-time-based
            return reduce_SignalTime(y_stereo)
        case "sig_specB":     # Signal-spectrum-based
            return reduce_SignalSpectrum(y_stereo,threshold)
        case "sig_timeFreqB": # Signal-time-frequency-based
            return reduce_SignalTimeFrequency(y_stereo)

def postprocess_audio(y_stereo, threshold):
    print(f"starting postprocess.\n.\n.\n.\n")
    return y_stereo

def thresholding(data, threshold):
    print(f"starting thresholding cycle.\n.\n.\n.\n")
    return data

def select_peaks(data):
    print(f"starting Detecting Onset-Times.\n.\n.\n.\n")
    onset_env = librosa.onset.onset_strength(y=data, sr=sr, aggregate=np.median, fmax=8000, n_mels=256)
    plt.figure( dpi=200,figsize=(18.5, 10.5) )
    librosa.display.waveshow(onset_env, sr=sr, color="red")
    plt.title("Onset Strength")
    plt.savefig(tempPath+cname+" - OnsetStrength.png")
    plt.close()
    times = librosa.times_like(onset_env, sr=sr)
    onset_env = librosa.to_mono(onset_env)
    onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
    plt.figure( dpi=200,figsize=(18.5, 10.5) )
    plt.plot(times, onset_env, label='Onset strength')
    plt.vlines(times[onset_frames], 0, onset_env.max(), color='r', alpha=0.9,linestyle='--', label='Onsets')
    plt.title("Onset Strength and Onsets")
    plt.savefig(tempPath+cname+" - OnsetStrengthOnsets.png")
    plt.close()

    return onset_frames

def peak_detection(y_stereo, threshold):
    print(f"starting Onset Detection Process.\n.\n.\n.\n")
    data=postprocess_audio(y_stereo,threshold)
    data=thresholding(data,threshold)
    peaks = select_peaks(data)
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
threshold=(100-float(json.loads(arg)["threshold"])) # threshold is given in dB below peak (max value)

method=json.loads(arg)["method"]
preprocess=json.loads(arg)["preprocess"]
clips_processed=[]
for clip in clipdata:
    cname=clip["name"].rsplit( ".", 1 )[ 0 ]
    audio_path=clip["path"]
    audio_path=audio_path.replace("\\", "\\\\")
    y_stereo, sr = librosa.load(clip["path"], mono=False, offset=clip["indelay"], sr = sr, duration=clip["end"]-clip["indelay"])
    if preprocess:
        y_stereo = preprocess_audio(y_stereo)
    else:
        y_stereo = y_stereo

    y_stereo = reduction_process(y_stereo, method, threshold,sr)
    peaks = peak_detection(y_stereo, threshold)
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