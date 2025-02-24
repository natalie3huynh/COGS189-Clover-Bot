from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host = 'localhost', port = 3000, debug = True)

@socketio.on('control_button')  # Event triggered from PsychoPy
def handle_button_control(data):
    # The data received will contain the button to be activated or highlighted
    emit('update_ui', data, broadcast=True)  # Send data to all connected clients

if __name__ == '__main__':
    socketio.run(app)