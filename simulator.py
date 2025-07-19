# simulator.py

import time
import math

class ReactorSimulator:
    """
    Kelas untuk mensimulasikan perilaku dasar reaktor nuklir.
    Fokus pada hubungan antara batang kendali, daya, dan suhu.
    """
    def __init__(self):
        # --- KONDISI AWAL REAKTOR ---
        self.rod_position = 100  # % keluar (100% = sepenuhnya ditarik, reaktivitas maks)
        self.reactor_power = 1.0   # % dari daya nominal (dimulai dari daya sangat rendah)
        self.coolant_temp = 280.0  # Suhu pendingin awal dalam Celcius
        self.system_pressure = 155.0 # Tekanan sistem dalam bar

        # --- KONSTANTA FISIKA (Sederhana) ---
        self.MAX_POWER = 100.0         # Daya maksimum 100%
        self.TEMP_AT_MAX_POWER = 325.0 # Suhu target saat daya penuh
        self.THERMAL_INERTIA = 100     # Seberapa lambat suhu berubah
        self.COOLING_EFFECT = 0.05     # Efek pendinginan konstan

        print("Reactor simulator initialized. Status: Standby.")

    def set_control_rod_position(self, position_percent):
        """Fungsi untuk mengatur posisi batang kendali dari luar."""
        # Memastikan posisi berada dalam rentang aman 0-100%
        self.rod_position = max(0, min(100, position_percent))
        print(f"Control rod position set to: {self.rod_position:.2f}%")

    def step(self, delta_time=1):
        """
        Menjalankan satu langkah simulasi maju selama 'delta_time' detik.
        Ini adalah inti dari simulator.
        """
        # 1. Hitung target daya berdasarkan posisi batang kendali
        # Hubungan non-linear sederhana untuk membuatnya lebih realistis
        power_target = self.MAX_POWER * (self.rod_position / 100.0) ** 2

        # 2. Hitung perubahan daya (dengan inersia)
        # Daya tidak langsung melompat ke target, tetapi bergerak menuju target
        power_change_rate = (power_target - self.reactor_power) / 20.0 # Inersia daya
        self.reactor_power += power_change_rate * delta_time

        # 3. Hitung perubahan suhu berdasarkan daya dan pendinginan
        # Panas yang dihasilkan oleh reaktor akan menaikkan suhu
        heat_generated = self.reactor_power * 0.15
        
        # Sistem pendingin selalu mencoba mendinginkan sistem
        cooling_loss = self.COOLING_EFFECT * (self.coolant_temp - 25) # Asumsi suhu luar 25 C
        
        # Perubahan suhu adalah hasil dari panas - pendinginan, dibagi inersia termal
        temp_change_rate = (heat_generated - cooling_loss) / self.THERMAL_INERTIA
        self.coolant_temp += temp_change_rate * delta_time

        # 4. Hitung tekanan (hubungan sederhana dengan suhu)
        self.system_pressure = self.coolant_temp / 2 # Aturan sederhana: 2 C = 1 bar

        # Memastikan nilai tidak menjadi tidak realistis (negatif)
        self.reactor_power = max(0, self.reactor_power)
        self.coolant_temp = max(25, self.coolant_temp)

    def get_status(self):
        """Mengembalikan status reaktor saat ini dalam bentuk dictionary."""
        return {
            "timestamp": time.time(),
            "rod_position": self.rod_position,
            "reactor_power_percent": self.reactor_power,
            "coolant_temp_celsius": self.coolant_temp,
            "system_pressure_bar": self.system_pressure,
        }

if __name__ == '__main__':
    # --- CONTOH PENGGUNAAN SIMULATOR ---
    # Blok ini hanya akan berjalan jika Anda menjalankan file simulator.py secara langsung
    print("--- Running Direct Simulation Test ---")
    my_reactor = ReactorSimulator()
    
    # Atur batang kendali ke 50% untuk menaikkan daya
    my_reactor.set_control_rod_position(50)

    # Jalankan simulasi selama 200 langkah (detik)
    for i in range(200):
        my_reactor.step()
        status = my_reactor.get_status()
        if i % 10 == 0: # Cetak status setiap 10 langkah
            print(f"Step {i:03d}: "
                  f"Power: {status['reactor_power_percent']:.2f}% | "
                  f"Temp: {status['coolant_temp_celsius']:.2f}°C | "
                  f"Pressure: {status['system_pressure_bar']:.2f} bar")
    
    print("\n--- Simulation Test Finished ---")