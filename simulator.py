# simulator.py

import time
import math

class ReactorSimulator:
    def __init__(self):
        # --- KONDISI OPERASIONAL ---
        self.rod_position = 100
        self.reactor_power = 1.0
        self.coolant_temp = 280.0
        self.system_pressure = 155.0
        self.neutron_flux = 1.0

        # --- INVENTARIS SUMBER DAYA (BARU) ---
        self.uranium_kg = 5000.0  # Total bahan bakar awal
        self.heavy_water_liters = 20000.0 # Total moderator awal
        self.polonium_grams = 100.0 # Inisiator neutron awal
        
        # --- KONSTANTA FISIKA ---
        self.MAX_POWER = 100.0
        self.TEMP_AT_MAX_POWER = 325.0
        self.THERMAL_INERTIA = 100
        self.COOLING_EFFECT = 0.05
        print("Reactor simulator initialized with resources. Status: Standby.")

    def set_control_rod_position(self, position_percent):
        self.rod_position = max(0, min(100, position_percent))
        # Tidak perlu print di sini agar tidak memenuhi log server

    def step(self, delta_time=1):
        # --- KONSUMSI SUMBER DAYA (BARU) ---
        # Konsumsi uranium & polonium bergantung pada daya
        power_ratio = self.reactor_power / self.MAX_POWER
        if self.uranium_kg > 0:
            uranium_consumed = power_ratio * 0.005 * delta_time # kg per detik
            self.uranium_kg -= uranium_consumed
        
        if self.polonium_grams > 0:
            polonium_consumed = power_ratio * 0.0001 * delta_time # gram per detik
            self.polonium_grams -= polonium_consumed
        
        # Moderator (Air Berat) berkurang sangat lambat (misal karena penguapan)
        if self.heavy_water_liters > 0:
            self.heavy_water_liters -= 0.001 * delta_time

        # Jika bahan bakar habis, daya menjadi nol
        if self.uranium_kg <= 0:
            self.reactor_power = 0
        
        # ... (Sisa dari logika step tetap sama) ...
        power_target = self.MAX_POWER * (self.rod_position / 100.0) ** 2
        power_change_rate = (power_target - self.reactor_power) / 20.0
        self.reactor_power += power_change_rate * delta_time
        heat_generated = self.reactor_power * 0.15
        cooling_loss = self.COOLING_EFFECT * (self.coolant_temp - 25)
        temp_change_rate = (heat_generated - cooling_loss) / self.THERMAL_INERTIA
        self.coolant_temp += temp_change_rate * delta_time
        self.system_pressure = self.coolant_temp / 2
        self.neutron_flux = 1.2e13 + (self.reactor_power / 100.0) * 2.5e13
        self.reactor_power = max(0, self.reactor_power)
        self.coolant_temp = max(25, self.coolant_temp)

    def add_resource(self, resource_type, amount):
        """Fungsi untuk menambah sumber daya dari luar (BARU)."""
        if resource_type == 'uranium':
            self.uranium_kg += amount
            return {"status": "success", "message": f"{amount} kg Uranium added."}
        elif resource_type == 'heavy_water':
            self.heavy_water_liters += amount
            return {"status": "success", "message": f"{amount} L Heavy Water added."}
        elif resource_type == 'polonium':
            self.polonium_grams += amount
            return {"status": "success", "message": f"{amount} g Polonium added."}
        return {"status": "error", "message": "Invalid resource type."}

    def get_status(self):
        """Mengembalikan status reaktor saat ini, termasuk sumber daya."""
        return {
            "timestamp": time.time(),
            "rod_position": self.rod_position,
            "reactor_power_percent": self.reactor_power,
            "coolant_temp_celsius": self.coolant_temp,
            "system_pressure_bar": self.system_pressure,
            "neutron_flux": self.neutron_flux,
            # --- Menambahkan data sumber daya (BARU) ---
            "uranium_kg": self.uranium_kg,
            "heavy_water_liters": self.heavy_water_liters,
            "polonium_grams": self.polonium_grams
        }