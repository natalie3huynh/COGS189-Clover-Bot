# # ------ Most recent attempt ---------
# from flask import Flask, render_template
# from flask_socketio import SocketIO, emit

# app = Flask(__name__)
# socketio = SocketIO(app, cors_allowed_origins="*")  # Allow cross-origin connections

# @app.route('/')
# def index():
#     return render_template('index.html')

# # Listen for the prediction event from run_vep.py
# @socketio.on("prediction")
# def handle_prediction(predicted_label):
#     print(f"Received prediction: {predicted_label}")  # Debugging
#     # Emit prediction to client/browser
#     socketio.emit('update_button', {'prediction': predicted_label}, broadcast=True)

# if __name__ == '__main__':
#     socketio.run(app, host='127.0.0.1', port=8000, debug=True)


# --------1st attempt------------
# from flask import Flask, render_template
# from flask_socketio import SocketIO

# app = Flask(__name__)
# socketio = SocketIO(app)

# @app.route('/')
# def index():
#     return render_template('index.html')

# #listen for prediction event labeled in run_vep
# @socketio.on("prediction")
# def handle_prediction(predicted_label):
#     #emit prediction to client/browser
#     emit('update_button', {'prediction': predicted_label}, broadcast=True)

# if __name__ == '__main__':
#     socketio.run(app, host='127.0.0.1', debug = True, port = 8000)

#------ 2nd attempt---------------
from flask import Flask, render_template
import socketio

# Initialize the Flask app and Socket.IO
app = Flask(__name__)
sio = socketio.Server()

# Integrate Socket.IO with the Flask app
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# Route for checking if the server is running
@app.route('/')
def index():
    return render_template('index.html')

# Handle prediction event from the client
@sio.event
def connect(sid, environ):
    print(f"Client {sid} connected.")

# Handle the prediction data from the client
@sio.event
def send_prediction(sid, data):
    print(f"Prediction data received: {data}")
    # Process the prediction here (for example, call a model prediction function)
    result = process_prediction(data)  # Assume this function processes the data
    # Send the prediction result back to the client
    sio.emit('prediction_result', result, room=sid)

# Handle disconnection event
@sio.event
def disconnect(sid):
    print(f"Client {sid} disconnected.")

# Function to process prediction (just an example, adapt it to your model)
def process_prediction(data):
    # Replace with your actual prediction logic
    # For example, this could be where you load a trained model and make predictions
    return {"predicted_class": "some_class", "confidence": 0.85}

if __name__ == '__main__':
    # Run the Flask app with the Socket.IO server
    app.run(host='127.0.0.1', port=8000)


