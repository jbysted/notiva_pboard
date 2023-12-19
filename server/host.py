from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import threading
import time
import json
import requests
import os
import streamdeck_out as out


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def run_process(input_string):
    #import streamdeck
    # Your existing 'run_process' logic, modified to send messages

    time.sleep(1)
    socketio.emit('process_message', {'message': 'Process started'})
    time.sleep(1)
    out.server_input(input_string)
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

def start(ip):
    server = socketio
    server.run(app, host=ip, port=80, allow_unsafe_werkzeug=True)
    return server

def getIP():
    routes = json.loads(os.popen("ip -j -4 route").read())
    ip = None
    for r in routes:
        if r.get("dev") == "eth0" and r.get("prefsrc"):
            ip = r['prefsrc']
            continue
        elif r.get("dev") == "wlan0" and r.get("prefsrc"):
            ip = r['prefsrc']
            continue
    return ip


def internet_connection():
    try:
        response = requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False 
