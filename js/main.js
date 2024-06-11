var srModeSelectP = document.getElementById('srModeSelect');
var deTypesSelect = document.getElementById("deTypes");
var th_sliderDiv = document.getElementById("th_sliderDiv");
var th_slider = document.getElementById("th_slider");
var th_input = document.getElementById("th_input");
var vTrack = document.getElementById("vTrack");
var ppAudio = document.getElementById("ppAudio");
var wsPanelStatusMsgs = document.getElementById("wsPanelStatusMsgs");
var settPanelBG = document.getElementById("settPanelBG");
var socket;





var port=11616
var loglvl=2 // 0=Critical ; 1=Error ; 2=Status ; 3=DEBUG

// TODO: Settings implementation
function saveConfig() {
    var cs = new CSInterface();
    port = parseInt(document.getElementById("portNr").value);
    loglvl = parseInt(document.getElementById("logLvl").value);
    var config = {
        "port": port,
        "loglvl": loglvl
    };
    cs.evalScript("$.nfo.saveConfig(" + JSON.stringify(config) + ")");
    // add class hide to settPanelBG

    if (! settPanelBG.classList.contains("hidden")) {
        settPanelBG.classList.add("hidden");
    }
}

function openSettings(){
    var cs = new CSInterface();
    cs.evalScript("$.nfo.openConfig()",function(config) {
        if (config !== "nc") {
            config=JSON.parse(config);
            document.getElementById("portNr").value = config.port;
            document.getElementById("logLvl").value = parseInt(config.loglvl);
        }
    });

    if (settPanelBG.classList.contains("hidden")) {
        settPanelBG.classList.remove("hidden");
    }
}


th_slider.addEventListener("change", (event) => {
    th_input.value = th_slider.value;
});

th_input.addEventListener("change", (event) => {
    th_slider.value = th_input.value;
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
    data = data.replace(/\n/g, '<br>').replace(/\t/g, '&emsp;');
    var p = document.createElement("p");
    // alert(data)
    p.innerHTML = data;
    wsPanelStatusMsgs.appendChild(p);
    wsPanelStatusMsgs.scrollTop = wsPanelStatusMsgs.scrollHeight;
}

function sendWsMsg(ctrl,data) {
    var message =JSON.stringify({"ctrl":ctrl,"data":data});
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
    return new Promise((resolve, reject) => {
        var cs = new CSInterface();
        var jsnabl=chkJSONable(data)
        switch (jsnabl){
            case 0:
                break;
            case 1:
                data=JSON.stringify(data);
                break;
            case 2:
                printNFO("Wrong data to set Markers")
        }
        if ( jsnabl ==1 || jsnabl==2 ){
            printNFO("setting Markers")
            try {
                cs.evalScript("$.core.setMarkers(" + data + ")",function(result) {
                    if (result ==0){
                        printNFO("")
                        printNFO("Markers set")
                        resolve(result);
                    }
                    else {
                        printNFO("Error setting Markers:\n\tProcess retuned with error code: "+str(result))
                        reject(new Error("Error setting Markers"));
                    }
                });
            } catch (error) {
                printNFO("Error setting Markers:\n\t"+error)
                reject(new Error("Error setting Markers"));
            }
        } else {
            printNFO("Session canceled")
            reject(new Error("Session canceled"));
        }
    });
}

function showClosePanelbtn() {
    var btn_stopProcessing = document.getElementById("btn_stopProcessing");
    if (! btn_stopProcessing.classList.contains("hidden")) {
        btn_stopProcessing.classList.add("hidden");
        var btn_closePanel = document.getElementById("btn_closePanel");
        if (btn_closePanel.classList.contains("hidden")) {
            btn_closePanel.classList.remove("hidden");
        }
    }
}

function openMessagePanel() {
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
}

function stopProcessing(){
    sendWsMsg("ctrl","stop")
    showClosePanelbtn();
}

function isJsonString(str) {
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
}

function chkJSONable(varToCheck) {
    if(varToCheck==null){
        if(loglvl==3) printNFO("ERROR:\n\tvariable is NULL");
        return 2;
    } else if (typeof varToCheck === 'object') {
        try {
            JSON.stringify(varToCheck);
            if(loglvl==3) printNFO("varToCheck is already JSON object");
            return 1;  // varToCheck is already JSON object
        } catch (e) {
            if(loglvl==3) printNFO("varToCheck is object but not JSON object");
            return 2;  // varToCheck is object but not JSON object
        }
    } else if (typeof varToCheck === 'string') {
        if (isJsonString(varToCheck)) {
            if(loglvl==3) printNFO("varToCheck is JSON string");
            return 0;  // varToCheck is a JSON string
        }
    } else {
        if(loglvl==3) printNFO("varToCheck is not JSONable");
        return 2;  // varToCheck is not JSONable
    }
}


function webSoc(argData) {
    return new Promise((resolve, reject) => {
        var returnVal = null;

        // check readyState to avoid multiple connections
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.close();
        }
        document.getElementById("wsPanelStatusMsgs").innerHTML = "";
        openMessagePanel();
        if (!socket || socket.readyState != WebSocket.OPEN) {
            socket = new WebSocket('ws://localhost:'+port);
        }


        sendWsMsg("msg","start")
        try {
            socket.onmessage = function(event) {
                var data;
                if(isJsonString(event.data)){
                    data=JSON.parse(event.data);
                } else { printNFO("Non-JSON Data Received:\n\t" + event.data + "\n\tisJsonString= " + isJsonString(event.data)); }
                if(isJsonString(data.data)){
                    data.data=JSON.parse(data.data);
                }
                switch (data.ctrl){
                    case "msg":
                        switch (data.data){
                            case "started":
                                sendWsMsg("data",argData)
                                break;
                            default:
                                var p = document.createElement("p");
                                p.innerHTML = data.data+"\n";
                                wsPanelStatusMsgs.appendChild(p);
                                var br = document.createElement("br");
                                wsPanelStatusMsgs.appendChild(br);
                                wsPanelStatusMsgs.scrollTop = wsPanelStatusMsgs.scrollHeight;

                        }
                        break;
                    case "status":
                        //var st=JSON.stringify(data.data);
                        printNFO(data.data);
                        break;
                    case "ctrl":
                        if (data.data.trim()=="done"){
                            stopProcessing();
                            //alert("done triggered: "+ returnVal);
                            if(returnVal !== null){
                                resolve(returnVal);
                            } else {
                                reject(new Error("No data received"));
                            }
                        }
                        break;
                    case "data":
                        printNFO("");
                        printNFO("Event Data Received:\n");
                        try{ if (typeof data.data === 'string') {
                            data.data = JSON.parse(data.data); // Parse the data property if it's a string
                        }} catch (error) { alert("Error parsing data: "+error); }
                        sendWsMsg("msg","Data Received");
                        returnVal = data.data;
                        break;
                    default:
                        printNFO("\tUnknown Control Message Received");
                        printNFO("");

                }
            };
            socket.onclose = function(event) {
                var p = document.createElement("p");
                p.innerHTML = "Analysis-Server disconnected\n";
                var br = document.createElement("br");
                wsPanelStatusMsgs.appendChild(br);
                wsPanelStatusMsgs.appendChild(p);
                wsPanelStatusMsgs.scrollTop = wsPanelStatusMsgs.scrollHeight;
                showClosePanelbtn()
            }
        } catch (error) {
            reject(new Error("An error occurred:", error));
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
        cs.evalScript("$.core.runPy('"+loglvl+"')", function(result) {
            if (result ==0){
                webSoc(pyArg).then((data) => {
                    jsStr=JSON.stringify(data);
                    //alert("post-haste: "+jsStr);
                    try {
                        setMarkers(data).then((result) => {
                            printNFO("\nProcessing Audio Track [" + track + "] completed");
                        }).catch(error => {
                            printNFO("\nERROR\nAn error occurred while setting Markers:\n\t", error);
                        });
                    } catch (error) {
                        printNFO("\nERROR\nAn error occurred while setting Markers:\n\t", error);
                    }
                }).catch(error => {
                    // This function will be called when the Promise is rejected
                    alert("An error occurred:", error);
                });
            }
        });
    });
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