# train_agent.py

from stable_baselines3 import PPO
from reactor_env import ReactorEnv
import os

# --- 1. MEMBUAT LINGKUNGAN ---
# Ini adalah lingkungan yang baru saja kita uji dan perbaiki.
env = ReactorEnv()

# --- 2. MEMBUAT MODEL / AGEN AI ---
# Kita akan menggunakan algoritma PPO (Proximal Policy Optimization).
# Ini adalah salah satu algoritma RL paling populer dan tangguh.
# 'MlpPolicy' berarti agen akan menggunakan Neural Network (Multi-layer Perceptron) sebagai otaknya.
model = PPO('MlpPolicy', env, verbose=1, tensorboard_log="./reactor_ppo_tensorboard/")

# --- 3. MEMULAI PELATIHAN ---
# Ini adalah proses utama. AI akan berinteraksi dengan lingkungan
# sebanyak 'total_timesteps' untuk belajar.
# Semakin besar nilainya, semakin lama latihannya, dan potensial semakin pintar AI-nya.
# PERINGATAN: Proses ini mungkin akan memakan waktu beberapa menit!
print("\n--- Starting Reinforcement Learning Agent Training ---")
model.learn(total_timesteps=50000)
print("--- Agent Training Complete ---")


# --- 4. MENYIMPAN AGEN YANG SUDAH TERLATIH ---
# Kita simpan "otak" AI yang sudah pintar ini ke dalam sebuah file.
models_dir = "models/PPO"
if not os.path.exists(models_dir):
    os.makedirs(models_dir)

model.save(f"{models_dir}/reactor_ppo_agent")

print(f"\nModel saved successfully to '{models_dir}/reactor_ppo_agent.zip'")
print("You can now test the trained agent.")