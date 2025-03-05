from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

#listen for prediction event labeled in run_vep
@socketio.on("prediction")
def handle_prediction(predicted_label):
    #emit prediction to client/browser
    emit('update_button', {'prediction': predicted_label}, broadcast=True)

if __name__ == '__main__':
    socketio.run(debug=True, host='127.0.0.1', port = 8000)

