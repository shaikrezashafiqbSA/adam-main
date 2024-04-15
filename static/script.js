$(document).ready(function() {
    // Initial TravellerAI greeting
    displayBotResponse("Hello! I'm a TravellerRAG chatbot. How can I can curate for you an experience today?");

    $('#chat-form').submit(function(e) {
        e.preventDefault(); 
        let message = $('#message-input').val();
        sendMessage(message); 
        $('#message-input').val(''); 
    });
    // Reset session functionality
    $('#reset-button').click(function() {
      $.ajax({
          url: '/reset_session',
          type: 'GET', // GET method typically used for simple actions like this
          success: function(response) {
              console.log(response); // Log the response from the server (should be "Session Reset")

              // Remove all elements within #chat-window EXCEPT the first one:
              $('#chat-window').children().slice(1).remove(); 
          }
      });
  });
});

function sendMessage(message) {
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
    // Split the text into lines
    const lines = text.split('\n');
  
    // Create a new paragraph element for each line, adding formatting as necessary
    const botResponseElement = $('<p></p>');
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (line.startsWith('# ')) {
        // This is a section header, add it as a heading
        $('<h2></h2>').text(line.slice(2)).appendTo(botResponseElement);
      } else {
        // This is a regular line, add it to the paragraph
        $('<span></span>').text(line).appendTo(botResponseElement);
        if (i < lines.length - 1) {
          // Add a line break, except for the last line
          $('<br>').appendTo(botResponseElement);
        }
      }
    }
  
    // Append the bot response element to the chat window
    $('#chat-window').append(botResponseElement);
  
    // Scroll to the bottom
    $("#chat-window").scrollTop($("#chat-window")[0].scrollHeight);
  }