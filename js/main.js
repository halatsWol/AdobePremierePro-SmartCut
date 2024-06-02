var srModeSelectP = document.getElementById('srModeSelect');
var deTypesSelect = document.getElementById("deTypes");
var th_sliderDiv = document.getElementById("th_sliderDiv");
var th_slider = document.getElementById("th_slider");
var th_input = document.getElementById("th_input");
var vTrack = document.getElementById("vTrack");
var ppAudio = document.getElementById("ppAudio");
var wsPanelStatusMsgs = document.getElementById("wsPanelStatusMsgs");
var socket;


var PORT=11616
var LOGLVL=2 // 0=none ; 1=Exceptions only ; 2=all

// TODO: Settings implementation

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
function printNFO(data="") {
    var p = document.createElement("p");
    p.textContent = data;
    wsPanelStatusMsgs.appendChild(p);
    wsPanelStatusMsgs.scrollTop = wsPanelStatusMsgs.scrollHeight;
}

function sendWsMsg(ctrl,data) {
    var message =JSON.stringify({ctrl:ctrl,data:data});
    if (socket.readyState === WebSocket.OPEN) {
        // If the connection is already open, send the message immediately
        socket.send(message);
    } else {
        // If the connection is not open, set an event handler to send the message when the connection opens
        socket.onopen = function() {
            socket.send(message);
        };
    }
}

function setMarkers(data) {
    var cs = new CSInterface();
    cs.evalScript("$.core.setMarkers(" + data + ")",function(result) {
        if (result ===0){
            printNFO("")
            printNFO("Markers set")
        }
    });
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
    // execute ExtendScript function to fetch audio track data
    cs.evalScript("$.core.fetchAudTrackData('" + jsn + "')", function(pyArg) {
        cs.evalScript('$.core.runPy()', function(result) {
            if (result ===0){
            data=webSoc(pyArg);
            setMarkers(data)
            }
        });
    });
}

function showClosePanel() {
    var btn_stopProcessing = document.getElementById("btn_stopProcessing");
    if (! btn_stopProcessing.classList.contains("hidden")) {
        btn_stopProcessing.classList.add("hidden");
        var btn_closePanel = document.getElementById("btn_closePanel");
        if (btn_closePanel.classList.contains("hidden")) {
            btn_closePanel.classList.remove("hidden");
        }
    }
}


function webSoc(argData) {
    var returnVal;
    // check readyState to avoid multiple connections
    if (!socket || socket.readyState != WebSocket.OPEN) {
        socket = new WebSocket('ws://localhost:'+PORT);
    }

    var wsPanelBG = document.getElementById("wsPanelBG");
    if (wsPanelBG.classList.contains("hidden")) {
        wsPanelBG.classList.remove("hidden");
        var btn_stopProcessing = document.getElementById("btn_stopProcessing");
        if (btn_stopProcessing.classList.contains("hidden")) {
            btn_stopProcessing.classList.remove("hidden");
        }
        var btn_closePanel = document.getElementById("btn_closePanel");
        if (! btn_closePanel.classList.contains("hidden")) {
            btn_closePanel.classList.add("hidden");
        }
    }
    sendWsMsg("msg","start")

    socket.onmessage = function(event) {
        data=JSON.parse(event.data);
        switch (data.ctrl){
            case "msg":
                switch (data.data){
                    case "started":
                        sendWsMsg("data",argData)
                    default:
                        var p = document.createElement("p");
                        p.textContent = "\tUnknown Message Data Received";
                        wsPanelStatusMsgs.appendChild(p);
                        var br = document.createElement("br");
                        wsPanelStatusMsgs.appendChild(br);
                        wsPanelStatusMsgs.scrollTop = wsPanelStatusMsgs.scrollHeight;
                }
            case "status":
                data=JSON.parse(event.data);
                printNFO(data.data);
            case "ctrl":
                if (data.data.trim()==="done"){
                    stopProcessing()
                }
            case "data":
                printNFO("");
                printNFO("Event Data Received:    Placing Timeline Markers");
                sendWsMsg("msg","Data Received")
                returnVal = data.data;
            default:
                printNFO("\tUnknown Control Message Received");
                printNFO("");
        }
    };
    socket.onclose = function(event) {
        var p = document.createElement("p");
        p.textContent = "Connection to Analysis-Server lost";
        var br = document.createElement("br");
        wsPanelStatusMsgs.appendChild(br);
        wsPanelStatusMsgs.appendChild(p);
        wsPanelStatusMsgs.scrollTop = wsPanelStatusMsgs.scrollHeight;
        showClosePanel()
    }
    return returnVal
}



function stopProcessing(){
    sendWsMsg("ctrl","stop")
    showClosePanel();
}

function btn_closePanel() {
    var wsPanelBG = document.getElementById("wsPanelBG");
    if (! wsPanelBG.classList.contains("hidden")) {
        wsPanelBG.classList.add("hidden");
    }
    var wsPanelStatusMsgs = document.getElementById("wsPanelStatusMsgs");
    var paragraphs = wsPanelStatusMsgs.getElementsByTagName("p");
    for (var i = paragraphs.length - 1; i >= 0; i--) {
        wsPanelStatusMsgs.removeChild(paragraphs[i]);
    }
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