// // Initialize the SocketIO connection with the direct URL
// const socket = io.connect('http://localhost:5000');

// socket.on('prediction', function(predictedLabel) {
//     console.log(predictedLabel);  // Logs the prediction string (e.g., "thumb-up")

//     // Reset the background color of all buttons
//     const buttons = document.querySelectorAll('.grid-btn');
//     buttons.forEach(button => {
//         button.style.backgroundColor = '';  // Reset background to default
//     });

//     // Use the predictedLabel to highlight the corresponding button
//     const button = document.getElementById(predictedLabel);
//     if (button) {
//         button.style.backgroundColor = 'yellow';  // Highlight the predicted button
//     }
// });

// Initialize the SocketIO connection with the direct URL
const socket = io.connect('http://localhost:5000');

socket.on('highlight_button', function(data) {
    console.log(data.button_id);  // Logs the predicted label for the button

    // Use the button ID to highlight the corresponding button
    const button = document.getElementById(data.button_id);
    if (button) {
        button.style.backgroundColor = 'yellow';  // Example of highlighting the button
    }
});
