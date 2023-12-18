

// Function to find timestamps of onset events in audio channel data
function findOnsetTimestamps(channelData, threshold, audioClipTime) {
    var onsetTimestamps = [];

    for (var i = 1; i < channelData.length; i++) {
        // Check for onset event (amplitude exceeds threshold)
        if (Math.abs(channelData[i]) > threshold && Math.abs(channelData[i - 1]) <= threshold) {
            // Calculate timestamp based on sample index
            var timestamp = i / audioClip.sampleRate;
            onsetTimestamps.push(audioClipTime+timestamp);
        }
    }
    if (onsetTimestamps.length > 0) {
        for (var i = 0; i < onsetTimestamps.length; i++) {
            var newMarker = new MarkerValue("");
            markerIndexValue++;
            newMarker.label = smartCutColorBttnsSelection;
            newMarker.comment = ["", markerIndexValue, i][smartCutNamingBttnsSelection];
            markerLayer.property("Marker").setValueAtTime(onsetTimestamps[i], newMarker);
        }
    }
}



// check if a project is open
var activeProject = app.project;
if (!activeProject) {
    $.writeln("No active project.");
    return;
}
// Check if a sequence is open
var activeSequence = app.project.activeSequence;
if (activeSequence) {
    // Reference to the audio track (change the trackIndex to your desired track)
    var audioTrackIndex = 1;
    var audioTrack = activeSequence.audioTracks[audioTrackIndex];

    // Check if the audio track exists
    if (audioTrack) {
        // Iterate through all clips in the audio track
        for (var i = 0; i < audioTrack.clips.numItems; i++) {
            var audioClip = audioTrack.clips[i];

            // Check if the clip is an audio clip
            if (audioClip.type === ProjectItemType.CLIP && audioClip.isAudio) {
                //get audio clip time position
                var audioClipTime = audioClip.start.seconds;

                // Get audio channel data (assuming mono audio)
                var audioChannelIndex = 0;
                var audioChannelData = audioClip.getAudioChannelData(audioChannelIndex);

                // Set a threshold for onset detection
                var threshold = 0.5;

                // Find timestamps of onset events
                findOnsetTimestamps(audioChannelData, threshold, audioClipTime);

                // Print the onset timestamps
                $.writeln("Onset Timestamps: " + onsetTimestamps);
            }
        }
    } else {
        $.writeln("Audio track not found.");
    }
} else {
    $.writeln("No active sequence.");
}


