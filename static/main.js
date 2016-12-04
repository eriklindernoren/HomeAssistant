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


$(document).ready(function () {

var last_ai_message = ""
var last_user_message = ""
setInterval(                               
  function()
  {
  	var url = 'http://127.0.0.1:5000/_get_message';
     $.getJSON(
        $SCRIPT_ROOT + '/_get_message',
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

