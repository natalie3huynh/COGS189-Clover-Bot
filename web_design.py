from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port = 8000)

# from flask import Flask, render_template
# from flask_socketio import SocketIO, emit
# from flask_cors import CORS  # For handling cross-origin requests

# app = Flask(__name__)
# socketio = SocketIO(app)

# # Enable CORS (for local development, it allows any origin)
# CORS(app)

# @app.route("/")
# def index():
#     return render_template("index.html")

# # Handle incoming predictions from the PsychoPy experiment
# @socketio.on('prediction')
# def handle_prediction(predicted_label):
#     print(f"Prediction received: {predicted_label}")
#     # Emit event to update UI and highlight the corresponding button
#     emit('highlight_button', {'button_id': predicted_label}, broadcast=True)

# # Test route to simulate sending a prediction
# @app.route("/test")
# def test_prediction():
#     socketio.emit('prediction', 'H') 
#     return "Test Prediction Sent!"

# if __name__ == '__main__':
#     socketio.run(app, host='localhost', port=5000, debug=True)

