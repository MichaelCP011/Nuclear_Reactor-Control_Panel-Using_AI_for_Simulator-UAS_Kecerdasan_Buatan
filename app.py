# app.py

from flask import Flask, render_template, jsonify
from simulator import ReactorSimulator
import threading
import time

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Buat satu objek simulator global agar statusnya terus berjalan
simulator = ReactorSimulator()

def run_simulation_background():
    """Fungsi untuk menjalankan simulasi di thread terpisah."""
    while True:
        simulator.step()
        # Anda bisa menambahkan logika kontrol (PID atau RL) di sini nanti
        time.sleep(1) # Simulasi berjalan setiap 1 detik

@app.route('/')
def dashboard_page():
    """Menampilkan halaman dashboard utama (index.html)."""
    return render_template('index.html')

# === INI BAGIAN BARUNYA ===
@app.route('/api/status')
def get_status():
    """Ini adalah API endpoint kita. Mengembalikan status reaktor sebagai JSON."""
    status = simulator.get_status()
    # jsonify mengubah dictionary Python menjadi format JSON untuk web
    return jsonify(status)
# ==========================


if __name__ == '__main__':
    # Jalankan simulasi di thread latar belakang
    simulation_thread = threading.Thread(target=run_simulation_background, daemon=True)
    simulation_thread.start()
    
    # Jalankan server web Flask
    app.run(host='0.0.0.0', port=5000, debug=True)