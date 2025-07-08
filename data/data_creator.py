import json
import numpy as np
import os

# Función polinómica para la altitud
def altitude_fn(t):
    return -0.05 * t**3 + 1.5 * t**2  # Ajuste para evitar caída brusca

# Datos
timestamps = np.round(np.arange(0.00, 10.01, 0.01), 2).tolist()
altitude = [max(0, altitude_fn(t)) for t in timestamps]  # evitar altitudes negativas

# Calculamos velocidad y limitamos a no negativa
velocity_raw = np.gradient(altitude, 0.01)
velocity = [max(0, v) for v in velocity_raw]

# Aceleración
acceleration = np.gradient(velocity, 0.01).tolist()

# Funciones suaves para roll, pitch, yaw
roll = [0.5*t for t in timestamps]      # amplitud 0.05, frecuencia baja
pitch = [0.05 * np.cos( 5* t) for t in timestamps]     # pequeño coseno suave
yaw = [(0.05 * np.sin(5 * t))  for t in timestamps]  # muy suave

data = {
    "timestamp": timestamps,
    "altitude": altitude,
    "velocity": velocity,
    "acceleration": acceleration,
    "roll": roll,
    "pitch": pitch,
    "yaw": yaw
}

# Empaquetar dentro de flight_results
final_data = {
    "flight_results": data
}

# Guardar en la carpeta donde está el script
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "../generated_polynomical_data.json")

with open(file_path, "w") as f:
    json.dump(final_data, f, indent=2)

print(f"Archivo guardado en: {file_path}")
