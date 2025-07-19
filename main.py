# main.py

import matplotlib.pyplot as plt
from simulator import ReactorSimulator
from simple_pid import PID
import time
import pandas as pd
import joblib
import numpy as np
import os

# Memuat model AI dan scaler
try:
    model = joblib.load('models/temp_predictor_model.joblib')
    scaler = joblib.load('models/scaler.joblib')
    print("AI model and scaler loaded successfully.")
except FileNotFoundError:
    print("Model not found. Please run 'train_predictor.py' first.")
    exit()

# Konfigurasi dan Setup Plot
TARGET_TEMPERATURE = 315.0
PREDICTION_HORIZON_S = 10 # <-- DEFINISIKAN HORISON PREDIKSI DALAM DETIK
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
fig.suptitle('Live Control Panel with AI Prediction', fontsize=16)

# Plot Daya Reaktor
ax1.set_title('Reactor Power')
ax1.set_xlabel('Time (seconds)')
ax1.set_ylabel('Power (%)')
ax1.set_ylim(0, 110)
ax1.grid(True)

# Plot Suhu Pendingin
ax2.set_title('Coolant Temperature & AI Prediction')
ax2.set_xlabel('Time (seconds)')
ax2.set_ylabel('Temperature (°C)')
ax2.set_ylim(250, 350)
ax2.grid(True)
ax2.axhline(y=TARGET_TEMPERATURE, color='g', linestyle='--', label=f'Target Temp ({TARGET_TEMPERATURE}°C)')

# Inisialisasi list data
time_data, power_data, temp_data = [], [], []
prediction_time_data, predicted_temp_data = [], [] # <-- LIST TERPISAH UNTUK PREDIKSI

# Membuat objek garis plot
power_line, = ax1.plot(time_data, power_data, 'r-', label='Actual Power')
temp_line, = ax2.plot(time_data, temp_data, 'b-', label='Actual Temperature')
predicted_line, = ax2.plot(prediction_time_data, predicted_temp_data, 'y--', label=f'AI Predicted Temp (in {PREDICTION_HORIZON_S}s)') #<-- GARIS PREDIKSI
ax1.legend()
ax2.legend()

plt.tight_layout(rect=[0, 0, 1, 0.96])

def run_live_with_ai():
    reactor = ReactorSimulator()
    pid = PID(Kp=0.8, Ki=0.05, Kd=0.1, setpoint=TARGET_TEMPERATURE)
    pid.output_limits = (0, 100)
    
    start_time = time.time()
    simulation_duration = 300

    while (time.time() - start_time) < simulation_duration:
        # Kontrol reaktor dengan PID
        current_temp = reactor.get_status()['coolant_temp_celsius']
        new_rod_position = pid(current_temp)
        reactor.set_control_rod_position(new_rod_position)
        reactor.step()
        status = reactor.get_status()

        # Gunakan model AI untuk prediksi
        current_features = np.array([[
            status['coolant_temp_celsius'],
            status['reactor_power_percent'],
            status['rod_position']
        ]])
        current_features_scaled = scaler.transform(current_features)
        predicted_temp = model.predict(current_features_scaled)[0]

        # Kumpulkan data
        current_time = time.time() - start_time
        time_data.append(current_time)
        power_data.append(status['reactor_power_percent'])
        temp_data.append(status['coolant_temp_celsius'])
        
        # <-- SIMPAN DATA PREDIKSI PADA WAKTU MASA DEPAN ---
        prediction_time_data.append(current_time + PREDICTION_HORIZON_S)
        predicted_temp_data.append(predicted_temp)

        # Update plot
        if len(time_data) % 5 == 0:
            power_line.set_data(time_data, power_data)
            temp_line.set_data(time_data, temp_data)
            # <-- GUNAKAN DATA WAKTU PREDIKSI UNTUK SUMBU-X GARIS KUNING
            predicted_line.set_data(prediction_time_data, predicted_temp_data)

            ax1.set_xlim(0, current_time + 10)
            ax2.set_xlim(0, current_time + 20) # Perlebar sumbu x untuk melihat prediksi
            fig.canvas.draw()
            fig.canvas.flush_events()
            
    print("Live simulation with AI prediction finished.")
    plt.ioff()
    plt.show()

if __name__ == '__main__':
    run_live_with_ai()