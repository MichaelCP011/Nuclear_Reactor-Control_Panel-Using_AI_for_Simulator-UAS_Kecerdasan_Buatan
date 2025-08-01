# app.py (v3.0 - Prosedural dengan Persistence)
import threading
import time
import json
import os
from flask import Flask, render_template, jsonify, request
from simulator import ReactorSimulator

# --- Manajemen State & Persistence ---
STATE_FILE = "savestate.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return None

def save_state(sim_instance):
    with open(STATE_FILE, 'w') as f:
        json.dump(sim_instance.get_status(), f)

# --- Inisialisasi Aplikasi & Simulator ---
app = Flask(__name__)
initial_state = load_state()
simulator = ReactorSimulator(initial_state)

# --- Proses Latar Belakang ---
def background_thread():
    while True:
        simulator.step()
        save_state(simulator) # Simpan state setiap detik
        time.sleep(1)

# --- Rute & API ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify(simulator.get_status())

@app.route('/api/action', methods=['POST'])
def handle_action():
    data = request.json
    action = data.get('action')
    value = data.get('value')
    
    response = {"status": "error", "message": "Invalid action"}

    if action == 'begin_startup': response = simulator.begin_startup_procedure()
    elif action == 'activate_coolant': response = simulator.activate_coolant()
    elif action == 'lower_rods': response = simulator.lower_rods_startup()
    elif action == 'activate_initiator': response = simulator.activate_initiator(float(value))
    elif action == 'set_rod_position': response = simulator.set_control_rod_position(float(value))
    elif action == 'shutdown': response = simulator.begin_shutdown()
    elif action == 'scram': response = simulator.scram()
        
    return jsonify(response)

if __name__ == '__main__':
    sim_thread = threading.Thread(target=background_thread, daemon=True)
    sim_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=True)