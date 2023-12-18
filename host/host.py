from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def run_process(input_string):
    # Your existing 'run_process' logic, modified to send messages
    time.sleep(1)
    socketio.emit('process_message', {'message': 'Process started'})
    time.sleep(1)
    print(input_string)
    time.sleep(1)
    socketio.emit('process_message', {'message': 'Process finished'})
    time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_process', methods=['POST'])
def handle_process():
    input_string = request.json['input']
    thread = threading.Thread(target=run_process, args=(input_string,))
    thread.start()
    thread.join()  # Wait for the process to complete
    return '', 202  # Accepted

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=80)
