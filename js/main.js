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

function procAud() {
    var cs = new CSInterface(); //deTypesSelect.options[deTypesSelect.selectedIndex].value
    var method = document.getElementById('deTypes').value;
    var track = document.getElementById('aTrack').value;
    var ppAb = false;
    var sr = 22050;
    Array.from(srModeSelectP.childNodes).forEach(child => {
        //check if child type is input
        if (child.nodeType === Node.ELEMENT_NODE && child.tagName === 'INPUT') {
            if (child.checked) {
                sr = child.value;
            }
        }
    });
    if (ppAudio.checked) {
        ppAb = true;
    } else {
        ppAb = false;
    }
    var jsn = JSON.stringify({ sr: parseInt(sr), preprocess: ppAb, method: method, th: th_input.value, track: track });
    cs.evalScript("$.core.procAud('" + jsn + "')", function(result) {
        cs.evalScript("$.core.createTempFolder('" + result + "')", function(result) {
            cs.evalScript('$.core.runPy()', function(result) {});
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