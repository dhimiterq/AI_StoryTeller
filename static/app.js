$(document).ready(function() {

    var ws = new WebSocket(`ws://${window.location.host}/chat`);
    var messages = document.getElementById('messages');
    var botMessageBuffer = '';
    var lastUserMessage = '';

    ws.onmessage = function(event) {
  
    	removeTypingIndicator();
    	botMessageBuffer += event.data;
    	appendMessage(event.data, 'bot');

    };

    function appendMessage(message, className) {
        var lastMessageContainer = messages.lastElementChild;
        if (lastMessageContainer && lastMessageContainer.classList.contains('message-container') && lastMessageContainer.lastElementChild.classList.contains(className)) {
            lastMessageContainer.lastElementChild.innerText += ' ' + message;
        } else {
            var messageContainer = document.createElement('div');
            messageContainer.className = 'message-container';

            var newMessage = document.createElement('div');
            newMessage.className = 'message ' + className;
            newMessage.innerText = message;

            messageContainer.appendChild(newMessage);
            messages.appendChild(messageContainer);
        }
        messages.scrollTop = messages.scrollHeight;
    }

    window.sendMessage = function() {
        var input = document.getElementById("messageText");
        var message = input.value.trim();
        if (message) {
            appendMessage(message, 'user');
            lastUserMessage = message;
            ws.send(message);
            input.value = '';
            addTypingIndicator();
        }
    }

    function addTypingIndicator() {
        var typingIndicator = document.createElement('div');
        typingIndicator.className = 'message-container';
        typingIndicator.id = 'typingIndicator';

        var indicatorMessage = document.createElement('div');
        indicatorMessage.className = 'message bot typing-indicator';
        indicatorMessage.innerText = 'Typing.....';

        typingIndicator.appendChild(indicatorMessage);
        messages.appendChild(typingIndicator);
        messages.scrollTop = messages.scrollHeight;
    }

    function removeTypingIndicator() {
        var typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

 

 	var socketimage = new WebSocket(`ws://${window.location.host}/ws/image`);
	socketimage.onmessage = function (event)  {
		if (event.data instanceof Blob) {
			const reader = new FileReader();
			
			reader.onload = function() {
				const img = document.getElementById('outputImage');
				img.src = reader.result;
			};
			
			reader.readAsDataURL(event.data);  
		}
		console.log("image received");
	};
	
	socketimage.onclose = function(event) {
		console.log('WebSocket closed:', event);
	}; 
	
	

});
