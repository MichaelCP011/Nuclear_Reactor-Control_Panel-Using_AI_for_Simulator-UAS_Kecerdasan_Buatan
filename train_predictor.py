# train_predictor.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error
import joblib
import os

print("--- Starting AI Model Training ---")

# --- 1. MEMUAT DATA ---
try:
    df = pd.read_csv('data/pid_simulation_log.csv')
    print(f"Data loaded successfully. Shape: {df.shape}")
except FileNotFoundError:
    print("Error: 'data/pid_simulation_log.csv' not found.")
    print("Please run 'main.py' first to generate the data.")
    exit()

# --- 2. FEATURE ENGINEERING (Mempersiapkan Input dan Output) ---
# Kita akan memprediksi suhu di masa depan berdasarkan kondisi saat ini.

# Input (X): Kondisi saat ini
features = ['coolant_temp_celsius', 'reactor_power_percent', 'rod_position']
X = df[features]

# Output (y): Suhu 10 langkah (detik) ke depan
prediction_horizon = 10
y = df['coolant_temp_celsius'].shift(-prediction_horizon)

# Menghapus baris terakhir yang tidak memiliki target masa depan (NaN)
X = X[:-prediction_horizon]
y = y[:-prediction_horizon]

print(f"Features (X) and Target (y) created. Training on {len(X)} data points.")

# --- 3. MEMBAGI DATA (TRAINING & TESTING) ---
# 80% data untuk melatih model, 20% untuk menguji seberapa baik modelnya.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Data split into training set ({len(X_train)} samples) and testing set ({len(X_test)} samples).")

# --- 4. SCALING DATA ---
# Neural Network bekerja paling baik jika semua input memiliki skala yang sama.
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("Data has been scaled.")

# --- 5. MEMBUAT DAN MELATIH MODEL NEURAL NETWORK ---
# MLPRegressor = Multi-layer Perceptron Regressor
# hidden_layer_sizes=(64, 32): Arsitektur NN kita (2 lapisan tersembunyi dengan 64 & 32 neuron)
# max_iter=500: Batas iterasi pelatihan
print("Training the Neural Network model... (This may take a moment)")
model = MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42, verbose=True)
model.fit(X_train_scaled, y_train)
print("Model training complete.")

# --- 6. MENGEVALUASI MODEL ---
# Kita gunakan data tes yang belum pernah dilihat model sebelumnya.
predictions = model.predict(X_test_scaled)
mae = mean_absolute_error(y_test, predictions)
print("\n--- Model Evaluation ---")
print(f"Mean Absolute Error (MAE) on test data: {mae:.4f}°C")
print(f"(Artinya, prediksi model rata-rata meleset sekitar {mae:.4f} derajat Celcius dari nilai sebenarnya)")

# --- 7. MENYIMPAN MODEL & SCALER ---
# Kita simpan agar bisa digunakan di program utama kita nanti.
if not os.path.exists('models'):
    os.makedirs('models')

joblib.dump(model, 'models/temp_predictor_model.joblib')
joblib.dump(scaler, 'models/scaler.joblib')

print("\nModel and scaler have been saved successfully to the '/models' folder.")
print("--- AI Model Training Finished ---")