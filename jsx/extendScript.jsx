#target "extendscript"

var proj = app.project;
var seq = proj.activeSequence;

$.nfo = {
	abt : function() {
		alert("Please find and read the ReadMe.txt file for instruction on how to use this panel template.")
	},

	seqNFO : function() {
		proj = app.project;
		seq = proj.activeSequence;
		var txt_output= "Project Name: " + proj.name + "\n";
		txt_output += "Sequence Name: " + seq.name + "\n";
		txt_output += "Sequence Timebase: " + seq.timebase + "\n";
		txt_output += "Sequence Frame Size: " + seq.frameSizeHorizontal + "x" + seq.frameSizeVertical + "\n";
		txt_output += "Sequence Frame Rate: " + seq.frameRate + "\n";
		txt_output += "Markers - Count: " + seq.markers.numMarkers + "\n";
		var playhead_obj = seq.getPlayerPosition();
		txt_output += "\n\nCurrent Playhead Position:\nSeconds: " + playhead_obj["seconds"] + "\n";
		alert(txt_output);
	},

	trackNFO : function() {
		proj = app.project;
		seq = proj.activeSequence;
		var txt_output = "Clips in the project:\n\n";
		var vtrack_count = seq.videoTracks.numTracks;
		txt_output += "Video Tracks:\n"
		for (var i = 0; i < vtrack_count; i++) {
			var track = seq.videoTracks[i];
			txt_output += "Track " + (i+1) + ":\n";
			var clip_count = track.clips.numItems;
			for (var j = 0; j < clip_count; j++) {
				var clip = track.clips[j];
				txt_output += "Clip " + (j+1) + ": " + clip.name + "\n";
			}
			txt_output += "\n";
		}
		txt_output += "\n\nAudio Tracks:\n"
		var atrack_count = seq.audioTracks.numTracks;
		for (var i = 0; i < atrack_count; i++) {
			var track = seq.audioTracks[i];
			txt_output += "Track " + (i+1) + ":\n";
			var clip_count = track.clips.numItems;
			for (var j = 0; j < clip_count; j++) {
				var clip = track.clips[j];
				txt_output += "Clip " + (j+1) + ": " + clip.name + "\n";
			}
			txt_output += "\n";
		}
		alert(txt_output);
	},
	vidTrckCnt : function() {
		var vtrack_count = seq.videoTracks.numTracks;
		alert("Number of video tracks: " + vtrack_count);
	}
};

$.core = {
	clearMarkers: function() {
		proj = app.project;
		seq = proj.activeSequence;
		var markers = seq.markers;
		var marker = markers.getFirstMarker();
		var count = markers.numMarkers;
		while (marker) {
			markers.deleteMarker(marker);
			marker = markers.getFirstMarker();
		}
		alert('Removed ' + count.toString() + ' markers');
	},

	procAud : function(jsn){
		proj = app.project;
		seq = proj.activeSequence;
		jsn = JSON.parse(jsn);
		var tnr= jsn.track -1;
		var track = seq.audioTracks[tnr];
		var clipdata = [];
		for (var i = 0; i < track.clips.numItems; i++) {
			var clip = track.clips[i];
			var jsnc = JSON.stringify({name:clip.name, start:clip.start.seconds, indelay:clip.inPoint.seconds, end:clip.end.seconds, path:clip.projectItem.getMediaPath()});
			clipdata.push(JSON.parse(jsnc));
		}
		var pyArg= JSON.stringify({clipdata:clipdata, track:tnr, threshold:jsn.th, method : jsn.method, preprocess: jsn.preprocess, sr: parseInt(jsn.sr)});
		return pyArg;
	},

	applyCuts : function(vtrack){
		vtrack = vtrack - 1;
		proj = app.project;
		seq = proj.activeSequence;
		var markers = seq.markers;
		var marker = markers.getFirstMarker();
		for(i = 0; i < markers.numMarkers; i++){
			var track = seq.videoTracks[vtrack];
			for(j = 0; j < track.clips.numItems; j++){
				if(marker.start.seconds >= track.clips[j].start.seconds && marker.start.seconds <= track.clips[j].end.seconds){
					var duration = track.clips[j].end.seconds - track.clips[j].start.seconds;
					track.clips[j].end = marker.start;
					if(j+1 < track.clips.numItems){
						duration = track.clips[j+1].end.seconds - track.clips[j+1].start.seconds;
						track.clips[j+1].start = marker.start;
						track.clips[j+1].end.seconds = track.clips[j+1].start.seconds + duration;
					}
					else {
						track.clips[j].end.seconds = track.clips[j].start.seconds + duration;
					}
					break;
				}
			}
		marker = markers.getNextMarker(marker);
		}
	},

	createTempFolder : function(jsn){
		var tmp = Folder.temp.fsName;
		var tempFolder = new Folder(tmp + "/Adobe/Premiere Pro/extensions/SmartCut/");
		try{
			tempFolder.create();
		} catch(e){
			alert(e);
		}
		var arg = new File(tempFolder.fsName + "/arg.json");
		try{
			arg.open("w");
			arg.write(jsn);
			arg.close();
		} catch(e){
			alert(e);
		}
		return arg.fsName;
	},

	runPy : function(){
		var progData = Folder.appData.fsName;
		var file = new File(progData+"/Adobe/CEP/extensions/SmartCut/py/run.bat");
		if (file.exists){
			try{
				file.execute();
			} catch(e){
				alert(e);
			}
		} else {
			alert("File does not exist");
		}

		$.sleep(2000);
		var tmp = Folder.temp.fsName;
		var tempFolder = new Folder(tmp + "/Adobe/Premiere Pro/Extensions/SmartCut/");
		var argFile = new File(tempFolder.fsName + "/arg.json");
		if (argFile.exists){
			var lckfile = new File(tempFolder.fsName + "/lockfile.lck");
			while(lck){
				$.sleep(1000);
				if(!lckfile.exists){
					lck=false;
				}
			}
		}
		else {
			alert("cannot start analyzing Audio\nCache has been Cleared during Operation.\nPlease restart!")
		}
		var jsnOF=new File (tempFolder.fsName + "/onsets.json");
		var jsnOnsets ="";
		if (jsnOF.exists) {
			try{
				jsnOF.open("r");
				jsnOnsets = jsnOF.read();
				jsnOF.close();
			}
			catch(e) {
				alert (e)
			}
			jsnOnsets = JSON.parse(jsnOnsets);
			var clipdata=jsnOnsets.clipdata;
			for (i =0; i< clipdata.length; i++) {
				var clip = clipdata[i];
				timeList=clip.peaks;
				for (t=0; t<timeList.length; t++) {
					var time = timeList[t];
					if (typeof time !== "number") {
						time = parseFloat(time);
					}
					try{
						seq.markers.createMarker(time+clip.start);
					}
					catch(e){
						alert(e);
					}
				}
				alert ("Markers added");
			}
		}
		else {
			alert("No onset.json File found")
		}
	}
}

