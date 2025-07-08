import json
import numpy as np
import os
import math

# Configuración
TOTAL_TIME = 30  # segundos
PEAK_TIME = 15   # segundos para alcanzar ~240m
PEAK_ALTITUDE = 240  # metros
DESCENT_RATE = 12  # m/s (velocidad de descenso con paracaídas)

# Función de altitud compuesta
def altitude_fn(t):
    if t <= PEAK_TIME:
        # Ascenso exponencial (rápido al inicio)
        return PEAK_ALTITUDE * (1 - math.exp(-t / 5))
    else:
        # Descenso lineal controlado (paracaídas)
        return max(0, PEAK_ALTITUDE - DESCENT_RATE * (t - PEAK_TIME))  # max(0) evita valores negativos

# Generar datos
timestamps = np.round(np.arange(0.00, TOTAL_TIME + 0.01, 0.01), 2).tolist()
altitude = [altitude_fn(t) for t in timestamps]

# Calcular velocidad y aceleración
velocity = np.gradient(altitude, 0.01).tolist()  # m/s
acceleration = np.gradient(velocity, 0.01).tolist()  # m/s²

# Simular orientación (ejemplo)
roll = [0.5 * t if t <= PEAK_TIME else 0 for t in timestamps]  # Giro durante ascenso
pitch = [10 * math.sin(0.3 * t) for t in timestamps]  # Oscilaciones moderadas
yaw = [5 * math.cos(0.2 * t) for t in timestamps]

# Guardar en JSON
data = {
    "timestamp": timestamps,
    "altitude": altitude,
    "velocity": velocity,
    "acceleration": acceleration,
    "roll": roll,
    "pitch": pitch,
    "yaw": yaw
}

file_path = os.path.join(os.path.dirname(__file__), "rocket_flight_parachute.json")
with open(file_path, "w") as f:
    json.dump({"flight_results": data}, f, indent=2)

print(f"Datos guardados en {file_path}")