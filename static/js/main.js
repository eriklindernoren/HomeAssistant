// ------------------------------------------------
//  				  Speech
// ------------------------------------------------

// Let Alfred know he's whether speaking
var setTalkingStatus = function(value) {
	var url = window.location.href + "_talking";
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
	onstart: voiceStartCallback,
	onend: voiceEndCallback
}

var speak = function(new_message){
	console.log("New speech: " + new_message);
	responsiveVoice.speak(new_message, "UK English Male", speech_parameters);
}

// ------------------------------------------------
//  				Visuals
// ------------------------------------------------

var updateUserMessage = function(new_message){
	console.log("User message: " + new_message);
	$("#user_message").text(new_message);
}

var updateAIMessage = function(new_message){
	console.log("AI message: " + new_message);
	$("#ai_message").text(new_message);
}

var updateTalkingStatus = function(talking){
	if(talking){
		$("#status p").text("Talking");
	}else{
		$("#status p").text("Listening");
	}
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
setInterval(                               
  function()
  {
  	var url = window.location.href + '_messages';
     $.getJSON(
        url,
        {},
        function(data)
        {
        	if(!talking){
	        	if(last_ai_message != data.ai_message){
	        		last_ai_message = data.ai_message;
	        		updateAIMessage(last_ai_message) 
	        		speak(last_ai_message);
        		}
	        	if(last_user_message != data.user_message){
	        		last_user_message = data.user_message;
	        		updateUserMessage(last_user_message);
	        	}
        	}

        });
  },
  50);
});

console.log("Loaded main.js");

