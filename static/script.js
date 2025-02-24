// Initialize the SocketIO connection with the direct URL
const socket = io.connect('http://localhost:5000');

// Listen for updates from Flask
socket.on('update_ui', function(data) {
    console.log(`Highlighting button: ${data.buttonId}`);  // Log the buttonId
    highlightButton(data.buttonId);
});

// Send control data to Flask based on EEG predictions
function sendButtonControl(buttonId) {
    socket.emit('control_button', { buttonId: buttonId });
}

// Function to highlight the button
function highlightButton(buttonId) {
    // Reset the background color for all buttons to clear previous highlights
    const buttons = document.querySelectorAll('.grid-btn');
    buttons.forEach(button => {
        button.style.backgroundColor = ''; // Clear the background color
    });

    // Highlight the button with a specific color
    const buttonToHighlight = document.getElementById(buttonId);
    if (buttonToHighlight) {
        buttonToHighlight.style.backgroundColor = 'yellow';
    }
}