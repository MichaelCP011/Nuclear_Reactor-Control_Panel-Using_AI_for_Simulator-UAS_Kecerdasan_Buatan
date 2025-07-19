# app.py

# Tambahkan 'request' ke baris import Anda
from flask import Flask, render_template, jsonify, request
from simulator import ReactorSimulator
import threading
import time

app = Flask(__name__)
simulator = ReactorSimulator()

def run_simulation_background():
    # ... (Fungsi ini tidak berubah) ...
    while True:
        simulator.step()
        time.sleep(1)

@app.route('/')
def dashboard_page():
    # ... (Fungsi ini tidak berubah) ...
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    # ... (Fungsi ini tidak berubah, tapi sekarang akan mengirim data resource juga) ...
    status = simulator.get_status()
    return jsonify(status)

# === INI ENDPOINT BARUNYA ===
@app.route('/api/add_resource', methods=['POST'])
def add_resource_api():
    """API endpoint untuk menambah sumber daya."""
    data = request.json
    resource_type = data.get('resource')
    amount = data.get('amount')
    
    if not resource_type or not amount:
        return jsonify({"status": "error", "message": "Missing resource or amount"}), 400

    result = simulator.add_resource(resource_type, float(amount))
    return jsonify(result)
# ============================


if __name__ == '__main__':
    # ... (Bagian ini tidak berubah) ...
    simulation_thread = threading.Thread(target=run_simulation_background, daemon=True)
    simulation_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=True)