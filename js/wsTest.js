var srModeSelectP = document.getElementById('srModeSelect');
var deTypesSelect = document.getElementById("deTypes");
var th_sliderDiv = document.getElementById("th_sliderDiv");
var th_slider = document.getElementById("th_slider");
var th_input = document.getElementById("th_input");
var vTrack = document.getElementById("vTrack");
var ppAudio = document.getElementById("ppAudio");

th_slider.addEventListener("change", (event) => {
    var val = th_slider.value;
    th_input.value = val;
});

th_input.addEventListener("change", (event) => {
    var val = th_input.value;
    th_slider.value = val;
});

function abt() {
    var cs = new CSInterface();
    cs.evalScript('$.nfo.abt()');
}

function seqNFO() {
    var cs = new CSInterface();
    cs.evalScript('$.nfo.seqNFO()');
}

function clearMarkers() {
    var cs = new CSInterface();
    cs.evalScript('$.core.clearMarkers()');
}
function setMarkers() {
    var cs = new CSInterface();
    cs.evalScript("$.core.setMarkers()")
}

function procAud() {
    var cs = new CSInterface();
    // get parameters from user interface
    var method = document.getElementById('deTypes').value;
    var track = document.getElementById('aTrack').value;
    var ppA = false; // not PPAP ;-D
    var sr = 22050; // default Sample Rate
    Array.from( srModeSelectP.childNodes ).forEach( child => {
        if (child.nodeType === Node.ELEMENT_NODE && child.tagName === 'INPUT') {
            if (child.checked) { sr = child.value; }
        }
    });
    if (ppAudio.checked) { ppA = true;} // Pre-Processing switch
    else { ppA = false;}
    var jsn = JSON.stringify({ sr: parseInt(sr), preprocess: ppA, method: method, th: th_input.value, track: track });
    // execute ExtendScript as promises
    cs.evalScript("$.core.fetchAudTrackData('" + jsn + "')", function(pyArg) {
        cs.evalScript("$.core.writeArgData('" + pyArg + "')", function() {
            cs.evalScript('$.core.runPy()', function() {
                setMarkers()
            });
        });
    });
}


function applyCuts() {
    var cs = new CSInterface();
    cs.evalScript("$.core.applyCuts(" + vTrack.value + ")");
}


function vidTrckCnt() {
    var cs = new CSInterface();
    cs.evalScript('$.core.vidTrckCnt()');
}


vTrack.addEventListener("change", (event) => {
    vidTrckCnt();
});