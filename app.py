# # ------ Most recent attempt ---------
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
sio = socketio.Server()

# integrate Socket.IO with flask app
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

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

# # Handle disconnection event
# @sio.event
# def disconnect(sid):
#     print(f"Client {sid} disconnected.")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)


