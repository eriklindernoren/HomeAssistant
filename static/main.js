var say = function(new_message){
	console.log("New speech: " + new_message);
	responsiveVoice.speak(new_message, "UK English Male");
}

var updateUserMessage = function(new_message){
	console.log("New message from you: " + new_message);
	$("#you").text(new_message);
}

var updateAIMessage = function(new_message){
	console.log("New message: " + new_message);
	$("#message").text(new_message);
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
        	if(last_ai_message != data.ai_message){
        		last_ai_message = data.ai_message;
        		updateAIMessage(last_ai_message) 
        		say(last_ai_message);
        	}
        	if(last_user_message != data.user_message){
        		last_user_message = data.user_message;
        		updateUserMessage(last_user_message);
        	}
        });
  },
  50);
});

console.log("Loaded main.js");

