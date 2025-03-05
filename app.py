from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on("prediction")
def handle_prediction(data):
    socketio.emit("update_button", data)
    
if __name__ == '__main__':
    socketio.run(debug=True, host='127.0.0.1', port = 8000)