// ----------
//  Speech
// ----------


function voiceStartCallback() {
	updateStatus("talking");
}
 
function voiceEndCallback() {
	updateStatus("inactive");
}

var speech_parameters = {
	onend: voiceEndCallback
}

var speak = function(new_message){
	console.log("New speech: " + new_message);
	voiceStartCallback();
	responsiveVoice.speak(new_message, "UK English Male", speech_parameters);
}

// ----------
//  Visuals
// ----------

var updateAlarms = function(alarms){
	$("#alarms").empty();
	var i;
	for(i = 0; i < alarms.length; i++){
		var alarm = alarms[i];
		console.log("Alarm: " + alarm.date + " " + alarm.time);
		$("#alarms").append("<p class='alarm'>" + alarm.date + " " + alarm.time + "</p>");
	}
}

var updateUserMessage = function(new_message){
	console.log("User message: " + new_message);
	$("#user_message").text(new_message);
}

var updateAIMessage = function(new_message){
	console.log("AI message: " + new_message);
	$("#ai_message").text(new_message);
}

var inactive = $SCRIPT_ROOT + "/static/images/microphone.png";
var listening = $SCRIPT_ROOT + "/static/images/microphone-1.png";
var thinking = $SCRIPT_ROOT + "/static/images/settings.png";
var talking = $SCRIPT_ROOT + "/static/images/speakers.png";
var glasses = $SCRIPT_ROOT + "/static/images/eyeglasses.png";

var current_status = "inactive";
var updateStatus = function(status){
	$("#inactiveStatus img").attr("src", inactive);
	$('#activeStatus').css({'animation': 'none'});
	$("#activeStatus").attr("src", glasses);

	if(status == "talking"){
		$("#activeStatus").attr("src", talking);
	}
	else if(status == "thinking"){
		$('#inactiveStatus').css({'display': 'none'});
		$('#activeStatus').css({'animation': '2s rotate360 infinite linear'});
		$("#activeStatus").attr("src", thinking);
	}
	else if(status == "listening"){
		$("#inactiveStatus img").attr("src", listening);
	}
	else{
		$('#inactiveStatus').css({'display':'block'});
	}

	current_status = status;
	console.log("Status: " + status);
}

updateStatus(current_status);

// ----------------
//  Communication
// ----------------

var previous_response = ""
var sendMessage = function(message){
	if (!message) return;
	console.log(message);
    updateUserMessage(message);
	updateStatus("thinking");
	var url = $SCRIPT_ROOT + "/_communication";
	$.getJSON(url, {
        text: message,
      }, function(data) {
      	console.log("Response: " + data.ai_message);
      	if(data.ai_message == " - "){
      		updateStatus("inactive");
      		return;
      	}
      	if(data.ai_message != previous_response){
      		updateAIMessage(data.ai_message);
      		speak(data.ai_message);
      	}else{
      		updateStatus("inactive");
      	}
      	previous_response = data.ai_message;
      });
}

$('input').keypress(function (e) {
	  if (e.which == 13) {
			event.preventDefault();
			text_input = $(this).val();
			$(this).val("");
			sendMessage(text_input);
	  }
});

// -------------
// Google STT 
// -------------
var recognition = new webkitSpeechRecognition();
recognition.continuous = false;
recognition.interimResults = true;
var record = function() {
	if(current_status == "listening"){
		updateStatus("inactive");
		recognition.stop();
		return;
	}
	updateStatus("listening");
	final_transcript = ""
	interim_transcript = ""
	recognition.onresult = function(event) { 
		var interim_transcript = '';
		for (var i = event.resultIndex; i < event.results.length; ++i) {
			console.log(event.results[i]);
			if (event.results[i].isFinal) {
				final_transcript = event.results[i][0].transcript;
				sendMessage(final_transcript);
			} else {
				interim_transcript += event.results[i][0].transcript;
				updateUserMessage(interim_transcript);
			}
		}
	}
	recognition.start();
}

console.log("Loaded main.js");


