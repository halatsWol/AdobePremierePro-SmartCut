//absolute value function
function abs(value) {
    return value < 0 ? -value : value;
}

// Function to find timestamps of onset events in audio channel data
function findOnsetTimestamps(audioClip, threshold) {
    if (typeof threshold !== 'number' || threshold < 0 || threshold > 1) {
        throw new Error('Invalid threshold. It should be a number between 0 and 1.');
    }

    var onsetTimestamps = [];
    var audioClipTime = audioClip.start.seconds;

    // Get audio channel data for all channels
    for (var channelIndex = 0; channelIndex < audioClip.numChannels; channelIndex++) {
        var audioChannelData = audioClip.getAudioChannelData(channelIndex);

        for (var i = 1; i < audioChannelData.length; i++) {
            // Check for onset event (amplitude exceeds threshold)
            if (abs(audioChannelData[i]) > threshold && abs(audioChannelData[i - 1]) <= threshold) {
                // Calculate timestamp based on sample index
                var timestamp = i / audioClip.sampleRate;
                onsetTimestamps.push(audioClipTime + timestamp);
            }
        }
    }

    // Create markers for detected onset timestamps
    if (onsetTimestamps.length > 0) {
        for (var i = 0; i < onsetTimestamps.length; i++) {
            try {
                var marker = audioClip.markers.createMarker(onsetTimestamps[i]);
                marker.name = "MyMarker"; // Change this to your desired marker name
                marker.comments = "This is a marker comment."; // Change this to your desired comment
            } catch (error) {
                $.writeln("Error creating marker: " + error.message);
            }
        }
    }

    return 0;
}

function findFirstAudioTrack(sequence) {
    for (var i = 0; i < sequence.audioTracks.numTracks; i++) {
        try {
            if (sequence.audioTracks[i]) {
                return sequence.audioTracks[i];
            }
        } catch (error) {
            $.writeln("Error accessing audio track: " + error.message);
        }
    }
    throw new Error('No audio track found.');
}

// Check if a project is open
var activeProject = app.project;
if (activeProject) {
    // Check if a sequence is open
    var activeSequence = app.project.activeSequence;
    if (activeSequence) {
        try {
            var audioTrack = findFirstAudioTrack(activeSequence);
            if (audioTrack) {
                // Iterate through all clips in the audio track
                for (var i = 0; i < audioTrack.clips.numItems; i++) {
                    var audioClip = audioTrack.clips[i];

                    // Check if the clip is an audio clip
                    if (audioClip.type === ProjectItemType.CLIP && audioClip.isAudio) {
                        // Find timestamps of onset events for the current audio clip
                        var onsetTimestamps = findOnsetTimestamps(audioClip, 0.1);
                    }
                }
            } else {
                $.writeln("Audio track not found.");
            }
        } catch (error) {
            $.writeln("Error processing audio track: " + error.message);
        }
    } else {
        $.writeln("No active sequence.");
    }
} else {
    $.writeln("No active project.");
}