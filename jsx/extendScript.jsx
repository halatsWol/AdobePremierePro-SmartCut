#target "extendscript"
#include "json2.js"

var proj = app.project;
var seq = proj.activeSequence;

$.nfo = {
	abt : function() {
		output= "SmartCut\t\t\tVersion: 0.8\n";
		output += "Developed by:\t\tkMarflow (Halatschek Wolfram)\n\n\n";
		output += "SmartCut is a tool that helps you to cut your video clips based on the audio content.\n\n\n";
		output += "This is a Beta Version and may contain Bugs.\n\n";
		output += "If suddenly the Extension does not work anymore, try to clear the Extension Cache.\n";
		output += "You can do this by deleting the Folder:\n";
		output += "%TEMP%\\Adobe\\Premiere Pro\\extensions\\SmartCut\n";
		output += "if this does not help, try to re-install the extension (close PP before).\n\n";
		output += "Please report any Bugs to:\ninfo@kmarflow.com\n";

		alert(output);
	},

	seqNFO : function() {
		proj = app.project;
		seq = proj.activeSequence;
		var txt_output= "Project Name: " + proj.name + "\n";
		txt_output += "Sequence Name: " + seq.name + "\n";
		txt_output += "Sequence Timebase: " + seq.timebase + "\n";
		txt_output += "Sequence Frame Size: " + seq.frameSizeHorizontal + "x" + seq.frameSizeVertical + "\n\n";
		txt_output += "Markers - Count: " + seq.markers.numMarkers + "\n";
		for(i=0;i<seq.videoTracks.numTracks;i++){
			txt_output += "Video Track: "+(i+1)+" - Clip Count = "+seq.videoTracks[i].clips.numItems+"\n";
		}
		var playhead_obj = seq.getPlayerPosition();
		txt_output += "\n\nCurrent Playhead Position:\nSeconds: " + playhead_obj["seconds"] + "\n";
		alert(txt_output);
	},

	vidTrckCnt : function() {
		var vtrack_count = seq.videoTracks.numTracks;
		alert("Number of video tracks: " + vtrack_count);
	},

	saveConfig : function(config) {
		var appdata = Folder.userData.fsName;
		var configPath = new Folder(appdata + "/Marflow Software/SmartCut/config");
		if (!configPath.exists){
			try{ configPath.create() }
			catch(e){ alert(e) }
		}
		var configFile = new File(configPath.fsName + "/config.conf");
		try{
			configFile.open("w");
			configFile.write(JSON.stringify(config));
			configFile.close();
		} catch(e){
			alert(e);
		}
	},
	openConfig : function(){
		var appdata = Folder.userData.fsName;
		var configPath = new Folder(appdata + "/Marflow Software/SmartCut/config");
		var configFile = new File(configPath.fsName + "/config.conf");
		if (configFile.exists){
			try{
				configFile.open("r");
				var config = configFile.read();
				configFile.close();
				return config;
			} catch(e){
				return "nc"; // no config
			}

		} else {
			return "nc";
		}

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



	fetchAudTrackData : function(jsn){
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

	runPy : function(loglvl){
		var progData = Folder.appData.fsName;

		if (loglvl == 3) {
			var file = new File(progData+"/Marflow Software/SmartCut/py/run.bat");
		}
		else {
			var file = new File(progData+"/Marflow Software/SmartCut/py/runquiet.vbs");
		}
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

		return 0
	},

	setMarkers : function (data){
		seq = app.project.activeSequence;
		var jsnOnsets = data;
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
					return 1;
				}
			}
		}
		return 0;
	}
}
