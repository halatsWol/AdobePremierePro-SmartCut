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

var socket = new WebSocket('ws://localhost:11616');
async function procAud() {
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
    var message =JSON.stringify({ctrl:"msg",data:"start Processing"});
    if (socket.readyState === WebSocket.OPEN) {
        // If the connection is already open, send the message immediately
        socket.send(message);
    } else {
        // If the connection is not open, set an event handler to send the message when the connection opens
        socket.onopen = function() {
            socket.send(message);
        };
    }
    socket.onmessage = function(event) {
        var wsPanelStatusMsgs = document.getElementById("wsPanelStatusMsgs");
        var p = document.createElement("p");
        console.log(event.data);
        data=JSON.parse(event.data);
        console.log(data + " >> " + data.data);
        p.textContent = data.data;
        wsPanelStatusMsgs.appendChild(p);
        wsPanelStatusMsgs.scrollTop = wsPanelStatusMsgs.scrollHeight;

        if (data.data.trim()==="done"){
            console.log("done triggered: "+ data.data=="done");

            stopProcessing()
        }
    };
    socket.onclose = function(event) {
        var wsPanelStatusMsgs = document.getElementById("wsPanelStatusMsgs");
        var p = document.createElement("p");
        p.textContent = "Connection to Analysis-Server lost";
        var br = document.createElement("br");
        wsPanelStatusMsgs.appendChild(br);
        wsPanelStatusMsgs.appendChild(p);
        wsPanelStatusMsgs.scrollTop = wsPanelStatusMsgs.scrollHeight;
        var btn_stopProcessing = document.getElementById("btn_stopProcessing");
        if (! btn_stopProcessing.classList.contains("hidden")) {
            btn_stopProcessing.classList.add("hidden");
            var btn_closePanel = document.getElementById("btn_closePanel");
            if (btn_closePanel.classList.contains("hidden")) {
                btn_closePanel.classList.remove("hidden");
            }
        }
    }

}

async function stopProcessing(){
    var message =JSON.stringify({ctrl:"ctrl",data:"stop"});
    if (socket.readyState === WebSocket.OPEN) {
        // If the connection is already open, send the message immediately
        socket.send(message);
    } else {
        // If the connection is not open, set an event handler to send the message when the connection opens
        socket.onopen = function() {
            socket.send(message);
        };
    }
    var btn_stopProcessing = document.getElementById("btn_stopProcessing");
    if (! btn_stopProcessing.classList.contains("hidden")) {
        btn_stopProcessing.classList.add("hidden");
        var btn_closePanel = document.getElementById("btn_closePanel");
        if (btn_closePanel.classList.contains("hidden")) {
            btn_closePanel.classList.remove("hidden");
        }
    }
}
async function btn_closePanel() {
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
