// ------------------------------------------------
//  				  Speech
// ------------------------------------------------

// Let Alfred know whether he's speaking
var setTalkingStatus = function(value) {
	var url = $SCRIPT_ROOT + "/_talking";
	$.getJSON(url, {
		"talking": value,
	}, function(data) {
		console.log("Talking was set to: " + value)
	});
}

var talking = false;
function voiceStartCallback() {
	updateTalkingStatus(true);
	setTalkingStatus(1);
	talking = true;
}
 
function voiceEndCallback() {
	updateTalkingStatus(false);
	setTalkingStatus(0);
	talking = false;
}

var speech_parameters = {
	onend: voiceEndCallback
}

var speak = function(new_message){
	console.log("New speech: " + new_message);
	voiceStartCallback();
	responsiveVoice.speak(new_message, "UK English Male", speech_parameters);
}

// ------------------------------------------------
//  				Visuals
// ------------------------------------------------

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

var updateTalkingStatus = function(talking){
	src = ""
	if(talking){
		var src = $SCRIPT_ROOT + "/static/images/speakers.png";
	}else{
		var src = $SCRIPT_ROOT + "/static/images/microphone.png";
	}

	$("#status").attr("src", src);

	console.log("Talking: " + talking);
}


// ------------------------------------------------
//  				MAIN LOOP
// 						-
//   Look for changes => Update visuals + speak
// ------------------------------------------------

$(document).ready(function () {

var last_ai_message = ""
var last_user_message = ""
var last_alarms = null
setInterval(                               
  function()
  {
 	if(!talking){
  		var url = $SCRIPT_ROOT + '/_messages';
	    $.getJSON(
	        url,
	        {},
	        function(data){
	        	if(data.ai_message && last_ai_message != data.ai_message){
	        		last_ai_message = data.ai_message;
	        		updateAIMessage(last_ai_message) 
	        		speak(last_ai_message);
        		}
	        	if(data.user_message && last_user_message != data.user_message){
	        		last_user_message = data.user_message;
	        		updateUserMessage(last_user_message);
	        	}
	        	if(data.alarms && !_.isEqual(last_alarms, data.alarms)){
	        		last_alarms = data.alarms;
	        		updateAlarms(data.alarms);
	        	}
        	});
 	}
  },
  100);
});

console.log("Loaded main.js");

