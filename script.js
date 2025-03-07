// Connect to the Socket.IO server
const socket = io.connect('http://127.0.0.1:8000');

// Listen for 'update_button' events from the server
socket.on('update_button', function(data) {
    const predictedLabel = data.prediction;

    // Remove the highlight from all buttons (optional, just in case)
    const buttons = document.querySelectorAll('.button');  // Assuming you have a class for your buttons
    buttons.forEach(button => {
        button.classList.remove('highlight');
    });

    // Find the button corresponding to the prediction and highlight it
    const button = document.getElementById(predictedLabel);
    if (button) {
        button.classList.add('highlight');
    }
});