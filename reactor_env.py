# reactor_env.py

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from simulator import ReactorSimulator

class ReactorEnv(gym.Env):
    """
    Lingkungan Reinforcement Learning kustom untuk simulator reaktor nuklir.
    """
    metadata = {'render_modes': ['human']}

    def __init__(self):
        super(ReactorEnv, self).__init__()
        
        self.simulator = ReactorSimulator()
        self.target_temp = 315.0

        # --- Mendefinisikan Ruang Aksi dan Observasi ---
        
        # Aksi: Apa yang bisa dilakukan AI?
        # Kita beri 3 pilihan aksi diskrit: 0 = turunkan rod, 1 = tahan, 2 = naikkan rod
        self.action_space = spaces.Discrete(3) 

        # Observasi: Apa yang bisa dilihat AI?
        # Terdiri dari 3 nilai: suhu saat ini, daya saat ini, dan posisi rod saat ini.
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0]), 
            high=np.array([500, 110, 100]), 
            dtype=np.float32
        )

    def _get_obs(self):
        """Mengambil status saat ini dari simulator."""
        status = self.simulator.get_status()
        return np.array([
            status['coolant_temp_celsius'],
            status['reactor_power_percent'],
            status['rod_position']
        ], dtype=np.float32)

    def _get_info(self):
        """Mengembalikan informasi tambahan (opsional)."""
        return {"target_temp": self.target_temp}

    def reset(self, seed=None, options=None):
        """Mereset lingkungan ke kondisi awal."""
        super().reset(seed=seed)
        self.simulator = ReactorSimulator()
        observation = self._get_obs()
        info = self._get_info()
        return observation, info

    def step(self, action):
        """Menjalankan satu langkah waktu di lingkungan berdasarkan aksi dari AI."""
        
        # 1. Menerjemahkan aksi (0, 1, 2) ke gerakan batang kendali
        current_pos = self.simulator.rod_position
        if action == 0: # Turunkan
            self.simulator.set_control_rod_position(current_pos - 1.0)
        elif action == 2: # Naikkan
            self.simulator.set_control_rod_position(current_pos + 1.0)
        # Jika aksi == 1, tidak melakukan apa-apa (tahan posisi)

        # 2. Jalankan satu langkah simulasi
        self.simulator.step()
        
        # 3. Ambil observasi baru
        observation = self._get_obs()
        current_temp = observation[0]

        # --- 4. Menghitung Reward (Bagian Paling Penting) ---
        reward = 0
        
        # Reward utama: seberapa dekat suhu dengan target
        temp_error = abs(current_temp - self.target_temp)
        # Semakin kecil error, semakin besar reward. Kita gunakan fungsi eksponensial.
        reward += np.exp(-0.1 * temp_error)

        # Penalti kecil untuk menjaga suhu tidak terlalu jauh dari target
        if temp_error > 10:
            reward -= 0.1
        
        # Penalti besar jika suhu melebihi batas aman (mencegah meltdown)
        terminated = False
        if current_temp > 340.0 or current_temp < 260.0:
            reward -= 50
            terminated = True # Episode berakhir jika tidak aman

        # Apakah episode selesai? (misal, karena tidak aman)
        truncated = False # Kita tidak punya batas waktu, jadi ini selalu False
        info = self._get_info()

        return observation, reward, terminated, truncated, info