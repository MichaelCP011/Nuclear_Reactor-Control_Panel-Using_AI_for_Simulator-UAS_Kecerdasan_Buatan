# simulator.py (v3.0 - Prosedural)
import time

class ReactorSimulator:
    def __init__(self, initial_state=None):
        if initial_state:
            # Muat state dari file jika ada
            self.__dict__.update(initial_state)
            print("Simulator state loaded from file.")
        else:
            # State default jika tidak ada file save
            self.state = "OFFLINE"
            # States: OFFLINE, STARTUP_PROCEDURE, AWAITING_COOLANT, AWAITING_RODS, AWAITING_INITIATOR, MANUAL_CONTROL, OPERATIONAL, SHUTDOWN, FAILURE
            self.sub_state_message = "Menunggu perintah startup."
            
            # Status Prosedur
            self.coolant_on = False
            self.rods_inserted = False
            self.initiator_on = False
            
            # Parameter Fisika
            self.rod_position = 0.0
            self.reactivity_k = 0.8
            self.reactor_power = 0.0
            self.coolant_temp = 25.0
            self.neutron_flux = 0.0
            
            # Sumber Daya
            self.uranium_kg = 5000.0

        # Konstanta
        self.MAX_POWER = 1000.0
        self.THERMAL_INERTIA = 300
        self.COOLING_EFFECT = 0.15

        print(f"Simulator v3.0 Initialized. State: {self.state}")

    # --- Aksi Operator ---
    def begin_startup_procedure(self):
        if self.state == "OFFLINE":
            self.state = "STARTUP_PROCEDURE"
            self.sub_state_message = "Aktifkan sistem pendingin & moderator."
            self.state = "AWAITING_COOLANT"
            return {"status": "success"}
        return {"status": "error"}

    def activate_coolant(self):
        if self.state == "AWAITING_COOLANT":
            self.coolant_on = True
            self.sub_state_message = "Turunkan Fuel Rod & Control Rod."
            self.state = "AWAITING_RODS"
            return {"status": "success"}
        return {"status": "error"}

    def lower_rods_startup(self):
        if self.state == "AWAITING_RODS":
            self.rods_inserted = True
            self.sub_state_message = "Nyalakan sumber inisiator neutron."
            self.state = "AWAITING_INITIATOR"
            return {"status": "success"}
        return {"status": "error"}

    def activate_initiator(self, speed_percent):
        if self.state == "AWAITING_INITIATOR":
            self.initiator_on = True
            self.sub_state_message = "Gunakan Control Rod untuk mencapai Criticality."
            self.state = "MANUAL_CONTROL"
            # Kecepatan reaksi awal bergantung pada input
            self.neutron_flux = 1e5 * (speed_percent / 100.0)
            return {"status": "success"}
        return {"status": "error"}

    def set_control_rod_position(self, position_percent):
        if self.state in ["MANUAL_CONTROL", "OPERATIONAL"]:
            self.rod_position = max(0, min(100, position_percent))
            return {"status": "success"}
        return {"status": "error"}

    def begin_shutdown(self):
        self.state = "SHUTDOWN"
        self.sub_state_message = "Menurunkan daya reaktor secara bertahap."
        return {"status": "success"}
        
    def scram(self):
        self.state = "SHUTDOWN"
        self.rod_position = 0.0
        self.sub_state_message = "EMERGENCY SCRAM ACTIVATED."
        return {"status": "success"}

    # --- Loop Simulasi ---
    def step(self):
        # Perhitungan reaktivitas dengan umpan balik negatif
        k_from_rods = 0.8 + (self.rod_position / 100.0) * 0.45
        temp_feedback = (self.coolant_temp - 150.0) * 0.00015
        power_feedback = (self.reactor_power / self.MAX_POWER) * 0.05
        self.reactivity_k = k_from_rods - temp_feedback - power_feedback

        if self.state in ["MANUAL_CONTROL", "OPERATIONAL"]:
            self.neutron_flux *= self.reactivity_k
        elif self.state == "SHUTDOWN":
            self.neutron_flux *= 0.95
            if self.reactor_power < 0.1:
                # Reset semua ke kondisi awal
                self.__init__() # Panggil konstruktor untuk reset total
        
        self.reactor_power = max(0, self.neutron_flux / 5e10)

        # Perhitungan Suhu & Panas
        if self.coolant_on:
            heat_generated = self.reactor_power * 0.8
            cooling_loss = self.COOLING_EFFECT * (self.coolant_temp - 25)
            temp_change_rate = (heat_generated - cooling_loss) / self.THERMAL_INERTIA
            self.coolant_temp += temp_change_rate
        
        # Logika Kegagalan
        if self.coolant_temp > 450: self.state = "FAILURE"
        
        # Konsumsi bahan bakar
        if self.state == "OPERATIONAL":
            self.uranium_kg -= self.reactor_power * 0.00002
            if self.uranium_kg <= 0: self.begin_shutdown()

        # Update State Otomatis
        if self.state == "MANUAL_CONTROL" and self.reactor_power > (self.MAX_POWER * 0.5):
            self.state = "OPERATIONAL"
            self.sub_state_message = "Reactor at stable power. Maintain parameters."

    def get_status(self):
        return self.__dict__