# simulator.py (Versi 2.0 - Mekanis & Bertahap)

import time
import math

class ReactorSimulator:
    def __init__(self):
        # --- STATE MACHINE UTAMA ---
        self.state = "COLD_SHUTDOWN"
        # Kemungkinan State: COLD_SHUTDOWN, PRE_STARTUP, SUBCRITICAL, CRITICAL, POWER_UP, OPERATIONAL, SHUTDOWN, FAILURE
        
        # --- KONDISI SISTEM ---
        self.is_coolant_system_ok = False
        self.is_neutron_source_inserted = False
        self.fuel_capacity_kg = 5000.0  # Kapasitas awal bahan bakar
        self.uranium_kg = 0.0 # Bahan bakar belum dimasukkan
        
        # --- PARAMETER FISIKA & KONTROL ---
        self.rod_position = 0.0  # % keluar (0% = sepenuhnya masuk)
        self.reactivity_k = 0.8  # Faktor multiplikasi neutron (k < 1 = subkritis)
        self.reactor_power = 0.0   # MW (MegaWatt)
        self.coolant_temp = 25.0   # Suhu pendingin awal (suhu ruangan)
        self.system_pressure = 10.0 # Tekanan awal
        self.neutron_flux = 0.0

        # --- KONSTANTA FISIKA (Direvisi sesuai masukan) ---
        self.MAX_POWER = 1000.0 # MW
        self.THERMAL_INERTIA = 200 # Lebih lambat panas
        self.COOLING_EFFECT = 0.1
        print("Mekanikal Simulator v2.0 Initialized. State: COLD_SHUTDOWN")

    # --- AKSI MANUAL OLEH OPERATOR ---
    def insert_fuel(self):
        if self.state == "COLD_SHUTDOWN":
            self.uranium_kg = self.fuel_capacity_kg
            self.state = "PRE_STARTUP"
            return {"status": "success", "message": "Fuel rods inserted. Ready for pre-startup checks."}
        return {"status": "error", "message": "Cannot insert fuel in current state."}

    def run_coolant_check(self):
        if self.state == "PRE_STARTUP":
            self.is_coolant_system_ok = True
            return {"status": "success", "message": "Coolant system check PASSED."}
        return {"status": "error", "message": "Must be in PRE_STARTUP state."}

    def insert_neutron_source(self):
        if self.state == "PRE_STARTUP" and self.is_coolant_system_ok:
            self.is_neutron_source_inserted = True
            self.state = "SUBCRITICAL"
            return {"status": "success", "message": "Neutron source inserted. Reactor is now subcritical."}
        return {"status": "error", "message": "Pre-startup checks not complete."}

    def set_control_rod_position(self, position_percent):
        self.rod_position = max(0, min(100, position_percent))
        # Mengubah posisi rod mempengaruhi reaktivitas
        # Ini adalah model yang sangat disederhanakan
        if self.is_neutron_source_inserted:
            self.reactivity_k = 0.8 + (self.rod_position / 100.0) * 0.4 # max k = 1.2
    
    def shutdown_reactor(self):
        self.state = "SHUTDOWN"
        self.set_control_rod_position(0) # Masukkan semua rod
        return {"status": "success", "message": "Shutdown sequence initiated."}


    # --- LOOP SIMULASI UTAMA ---
    def step(self, delta_time=1):
        # Logika Fisi berdasarkan state
        if self.state in ["SUBCRITICAL", "CRITICAL", "POWER_UP", "OPERATIONAL"]:
            # Reaksi berantai: daya baru = daya lama * reaktivitas
            power_from_fission = self.reactor_power * self.reactivity_k
            
            # Tambahan daya dari sumber neutron eksternal (hanya di awal)
            power_from_source = 1e-5 if self.state == "SUBCRITICAL" and self.neutron_flux < 1e10 else 0
            
            self.reactor_power = power_from_fission + power_from_source
            self.reactor_power = max(0, self.reactor_power) # Pastikan tidak negatif

            # Transisi state otomatis
            if self.state == "SUBCRITICAL" and self.reactivity_k >= 1.0:
                self.state = "CRITICAL"
            if self.state == "CRITICAL" and self.reactivity_k > 1.0:
                self.state = "POWER_UP"
            if self.state == "POWER_UP" and self.reactor_power > (self.MAX_POWER * 0.1): # Dianggap operasional setelah 10% daya
                self.state = "OPERATIONAL"

        elif self.state == "SHUTDOWN":
            self.reactor_power *= 0.8 # Daya turun secara eksponensial
            if self.reactor_power < 1e-3:
                self.reactor_power = 0
                self.state = "COLD_SHUTDOWN" # Kembali ke state awal
        
        elif self.state == "FAILURE":
            self.reactor_power *= 1.5 # Reaksi tak terkendali

        # Update Fisika (Persamaan Baru)
        if self.is_coolant_system_ok:
            heat_generated = self.reactor_power * 0.8
            cooling_loss = self.COOLING_EFFECT * (self.coolant_temp - 25)
            temp_change_rate = (heat_generated - cooling_loss) / self.THERMAL_INERTIA
            self.coolant_temp += temp_change_rate * delta_time
        
        self.system_pressure = 10.0 + self.coolant_temp / 2.5 # Hubungan baru
        self.neutron_flux = 1e12 + self.reactor_power * 1e11 # Hubungan baru

        # Logika Kegagalan
        if self.coolant_temp > 450 and self.state != "FAILURE":
            self.state = "FAILURE"
            print("!!! MELTDOWN IMMINENT: COOLANT TEMPERATURE EXCEEDED SAFE LIMITS !!!")
        
        # Konsumsi bahan bakar
        if self.state == "OPERATIONAL":
            self.uranium_kg -= self.reactor_power * 0.00001 * delta_time
            if self.uranium_kg <= 0:
                print("!!! FUEL DEPLETED. INITIATING SHUTDOWN. !!!")
                self.shutdown_reactor()

    def get_status_indicator(self):
        if self.state == "FAILURE": return "FAILURE"
        if self.coolant_temp > 380: return "BERESIKO"
        if self.state == "OPERATIONAL" and abs(self.reactivity_k - 1.0) > 0.05: return "RENTAN"
        if self.state == "COLD_SHUTDOWN": return "OFFLINE"
        return "AMAN"

    def get_status(self):
        """Mengembalikan status reaktor saat ini."""
        return {
            "reactor_state": self.state,
            "status_indicator": self.get_status_indicator(),
            "rod_position": self.rod_position,
            "reactivity_k": self.reactivity_k,
            "reactor_power_mw": self.reactor_power,
            "coolant_temp_celsius": self.coolant_temp,
            "system_pressure_bar": self.system_pressure,
            "neutron_flux": self.neutron_flux,
            "uranium_kg": self.uranium_kg,
            "fuel_capacity_kg": self.fuel_capacity_kg,
            "is_coolant_system_ok": self.is_coolant_system_ok,
            "is_neutron_source_inserted": self.is_neutron_source_inserted
        }