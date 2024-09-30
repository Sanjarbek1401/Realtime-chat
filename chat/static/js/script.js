let chatSocket;

function connectWebSocket() {
    chatSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/');

    chatSocket.onopen = function() {
        console.log('WebSocket connection established.');
        sendButton.disabled = false;
    };

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        appendMessage('Other: ' + data.message);
    };

    chatSocket.onclose = function() {
        console.log('WebSocket connection closed.');
        sendButton.disabled = true;
    };

    chatSocket.onerror = function(error) {
        console.error('WebSocket Error:', error);
        sendButton.disabled = true;
    };
}

function sendMessage() {
    const message = messageInput.value;
    if (message) {
        chatSocket.send(JSON.stringify({ 'message': message }));
        messageInput.value = '';
        appendMessage('You: ' + message);
    }
}

function appendMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Initialize WebSocket connection
connectWebSocket();

const sendButton = document.getElementById('sendButton');
const messageInput = document.getElementById('messageInput');
const chatBox = document.getElementById('chatBox');
const messageForm = document.getElementById('messageForm');

sendButton.onclick = sendMessage;

messageInput.onkeypress = function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
};

messageForm.onsubmit = function(e) {
    e.preventDefault();
    sendMessage();
};

window.onbeforeunload = function() {
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.close();
    }
};
