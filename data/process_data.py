import json
import numpy as np

def baro_altitude(p, p0=1013.25):
    return 44330.0 * (1.0 - (p / p0)**(1.0 / 5.255))

def validate_sample(s):
    return (
        "timestamp" in s and
        "pressure" in s and isinstance(s["pressure"], (int, float)) and
        "acceleration" in s and "gyroscope" in s and
        "altitude" in s and isinstance(s["altitude"], (int, float))
    )

def load_samples(path):
    with open(path, 'r') as file:
        data = json.load(file)
    return [s for s in data["flight_data"] if validate_sample(s)]

def save_results(res, path):
    with open(path, 'w') as file:
        json.dump(res, file, indent=2)

def ajustar_polinomio(x, y, grado=3):
    coef = np.polyfit(x, y, grado)
    return np.poly1d(coef)

def calcular_orientacion(giroscopio, timestamps):
    roll = [0]
    pitch = [0]
    yaw = [0]

    for i in range(1, len(timestamps)):
        dt = timestamps[i] - timestamps[i - 1]
        if dt <= 0:
            dt = 1e-3  # evita división por cero

        gx = np.radians(giroscopio[i]['x'])  # Convertir a radianes
        gy = np.radians(giroscopio[i]['y'])  # Convertir a radianes
        gz = np.radians(giroscopio[i]['z'])  # Convertir a radianes

        roll.append(roll[-1] + gx * dt)
        pitch.append(pitch[-1] + gy * dt)
        yaw.append(yaw[-1] + gz * dt)

    return roll, pitch, yaw

def derivar_1D(x, y):
    x = np.array(x)
    y = np.array(y)
    return np.gradient(y, x)

def process(samples):
    timestamps = []
    altitudes = []
    aceleracion = []
    giroscopio = []

    for s in samples:
        timestamps.append(s["timestamp"]/100)  # Convertir a segundos
        altitudes.append(s["altitude"])
        aceleracion.append(s["acceleration"])
        giroscopio.append(s["gyroscope"])

    timestamps = np.array(timestamps)
    tiempo_norm = timestamps - timestamps[0]

    roll, pitch, yaw = calcular_orientacion(giroscopio, tiempo_norm)

    #  CAMBIO: ahora interpolamos con 1000 puntos
    t_interp = np.linspace(tiempo_norm[0], tiempo_norm[-1], 1000)

    pol_alt = ajustar_polinomio(tiempo_norm, altitudes, grado=6)
    alt_ajustada = pol_alt(tiempo_norm)
    alt_interp = pol_alt(t_interp)

    pol_roll = ajustar_polinomio(tiempo_norm, roll, grado=8)
    roll_interp = pol_roll(t_interp) / 100

    pol_pitch = ajustar_polinomio(tiempo_norm, pitch, grado=8)
    pitch_interp = pol_pitch(t_interp) / 100

    pol_yaw = ajustar_polinomio(tiempo_norm, yaw, grado=8)
    yaw_interp = pol_yaw(t_interp) / 100

    velocidad = derivar_1D(tiempo_norm, alt_ajustada)
    aceleracion_lineal = derivar_1D(tiempo_norm, velocidad)

    pol_vel = ajustar_polinomio(tiempo_norm, velocidad, grado=3)
    vel_interp = pol_vel(t_interp)

    pol_acc = ajustar_polinomio(tiempo_norm, aceleracion_lineal, grado=3)
    acc_interp = pol_acc(t_interp)/9.81  # Convertir a g's

    return {
        "timestamp": t_interp.tolist(),
        "altitude": alt_interp.tolist(),
        "velocity": vel_interp.tolist(),
        "acceleration": acc_interp.tolist(),
        "roll": roll_interp.tolist(),
        "pitch": pitch_interp.tolist(),
        "yaw": yaw_interp.tolist()
    }

if __name__ == "__main__":
    samples = load_samples("data/rocket_flight_data.json")
    results = process(samples)
    save_results(results, "processed_data_interp.json")

