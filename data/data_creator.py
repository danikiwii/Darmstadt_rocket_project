import json
import numpy as np
import os

# Configuración del vuelo
TOTAL_TIME = 30  # segundos
PEAK_TIME = 15   # segundos (cuando alcanza máxima altura)
PEAK_ALTITUDE = 240  # metros

# Función de altitud (parte ascendente y descendente)
def altitude_fn(t):
    if t <= PEAK_TIME:
        # Subida parabólica (0 a 15 segundos)
        return (PEAK_ALTITUDE / (PEAK_TIME**2)) * t**2
    else:
        # Bajada parabólica (15 a 30 segundos)
        time_since_peak = t - PEAK_TIME
        return PEAK_ALTITUDE - (PEAK_ALTITUDE / (PEAK_TIME**2)) * time_since_peak**2

# Generar datos
timestamps = np.round(np.arange(0.00, TOTAL_TIME + 0.01, 0.01), 2).tolist()
altitude = [max(0, altitude_fn(t)) for t in timestamps]  # Evitar valores negativos

# Calcular velocidad y aceleración
velocity = np.gradient(altitude, 0.01).tolist()  # m/s
acceleration = np.gradient(velocity, 0.01).tolist()  # m/s²

# Simular orientación (valores de ejemplo)
roll = [0.1 * t if t <= PEAK_TIME else 0.1 * PEAK_TIME for t in timestamps]
pitch = [5 * np.sin(0.2 * t) for t in timestamps]
yaw = [2 * np.cos(0.3 * t) for t in timestamps]

# Empaquetar datos
data = {
    "timestamp": timestamps,
    "altitude": altitude,
    "velocity": velocity,
    "acceleration": acceleration,
    "roll": roll,
    "pitch": pitch,
    "yaw": yaw
}

# Guardar en JSON
file_path = os.path.join(os.path.dirname(__file__), "../rocket_flight_corrected.json")
with open(file_path, "w") as f:
    json.dump({"flight_results": data}, f, indent=2)

print(f"Datos guardados en {file_path}")

