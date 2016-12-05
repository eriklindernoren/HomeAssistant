var setClientStatus = function(name, value) {
	var url = window.location.href + "_client_status";
	$.getJSON(url, {
		talking: value,
	}, function(data) {
		console.log("Talking was set to: " + value)
	});
}

var talking = false;

function voiceStartCallback() {
	setClientStatus("talking", 1);
    talking = true;
}
 
function voiceEndCallback() {
	setClientStatus("talking", 0);
    talking = false;
}

var speak = function(new_message){
	console.log("New speech: " + new_message);
	var parameters = {
    	onstart: voiceStartCallback,
    	onend: voiceEndCallback
	}
	responsiveVoice.speak(new_message, "UK English Male", parameters);
}

var updateUserMessage = function(new_message){
	console.log("User message: " + new_message);
	$("#user_message").text(new_message);
}

var updateAIMessage = function(new_message){
	console.log("AI message: " + new_message);
	$("#ai_message").text(new_message);
}

// -------------
// Google STT 
// -------------
// var recognition = new webkitSpeechRecognition();
// recognition.continuous = false;
// recognition.interimResults = true;

// var record = function() {

// 	final_transcript = ""
// 	interim_transcript = ""
// 	recognition.onresult = function(event) { 
// 		var interim_transcript = '';
// 		for (var i = event.resultIndex; i < event.results.length; ++i) {
// 			console.log(event.results[i]);
// 			if (event.results[i].isFinal) {
// 				final_transcript = event.results[i][0].transcript;
// 				$("#you").text(final_transcript);
// 				var url = window.location.href + "_handle_text";
// 				$.getJSON(url, {
// 			        text: final_transcript,
// 			      }, function(data) {
// 			      	say(data.ai_message);
// 			        $("#message").text(data.ai_message);
// 			        final_transcript = "";
// 					setTimeout(function(){ record(); }, 5000);
// 			      });
// 			} else {
// 				interim_transcript += event.results[i][0].transcript;
// 				$("#you").text(interim_transcript);
// 			}
// 		}
// 	}
// 	recognition.start();
// }

// ------------------------------------------------
//  				MAIN LOOP
// - Look for changes => Update visuals + speak -
// ------------------------------------------------

$(document).ready(function () {

var last_ai_message = ""
var last_user_message = ""
setInterval(                               
  function()
  {
  	var url = window.location.href + '_get_message';
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

