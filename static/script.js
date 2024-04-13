$(document).ready(function() {
    $('#chat-form').submit(function(e) {
        e.preventDefault(); 
        let message = $('#message-input').val();
        sendMessage(message); 
        $('#message-input').val(''); // Clear input field
    });
});

function sendMessage(message) {
    // Add user message to chat window
    $('#chat-window').append('<p><strong>You: </strong>' + message + '</p>'); 

    $.ajax({
        url: '/chat',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ message: message }),
        success: function(response) {
            displayBotResponse(response.bot_response); 
        }
    });
}

function displayBotResponse(text) {
    $('#chat-window').append('<p><strong>TravellerAI: </strong>' + text + '</p>');
    // Scroll chat window to the bottom
    $("#chat-window").scrollTop($("#chat-window")[0].scrollHeight);
}
