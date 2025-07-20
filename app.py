# app.py (Versi 2.0 - Mekanis & Bertahap)

from flask import Flask, render_template, jsonify, request
from simulator import ReactorSimulator
import threading
import time

app = Flask(__name__)
simulator = ReactorSimulator()

# Hapus semua logika kontrol lama, sekarang semuanya manual
def run_simulation_background():
    while True:
        simulator.step()
        time.sleep(1)

@app.route('/')
def dashboard_page():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify(simulator.get_status())

# --- API BARU UNTUK KONTROL MANUAL ---

@app.route('/api/action', methods=['POST'])
def handle_action():
    data = request.json
    action = data.get('action')
    value = data.get('value')
    
    response = {"status": "error", "message": "Invalid action"}

    if action == 'insert_fuel':
        response = simulator.insert_fuel()
    elif action == 'run_coolant_check':
        response = simulator.run_coolant_check()
    elif action == 'insert_neutron_source':
        response = simulator.insert_neutron_source()
    elif action == 'set_rod_position':
        simulator.set_control_rod_position(float(value))
        response = {"status": "success", "message": f"Control rods set to {value}%"}
    elif action == 'shutdown':
        response = simulator.shutdown_reactor()
        
    return jsonify(response)

# (Endpoint /api/add_resource bisa dihapus atau di-nonaktifkan jika tidak diperlukan lagi)

if __name__ == '__main__':
    simulation_thread = threading.Thread(target=run_simulation_background, daemon=True)
    simulation_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=True)