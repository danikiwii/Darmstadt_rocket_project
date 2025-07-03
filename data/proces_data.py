#Start the process

#Needed imports
import numpy as np
import math
import json
import os

# Constants

EARTH_RADIUS = 6371000  # In meters
SEA_LEVEL_PRESSURE = 1013.25  # In hPa

#Calculate barometric altitude
def baro_altitude(p, p0=SEA_LEVEL_PRESSURE):

    return 44330 * (1 - (p / p0) ** 0.190294957)

#Calculate haversine distance
def haversine(lat1, lon1, lat2, lon2):

    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dl / 2) ** 2

    return 2 * EARTH_RADIUS * math.asin(math.sqrt(a))

#Function to check that there are all the parameters needed
def validate_sample(sample):

    required = {"t", "lat", "lon", "pressure", "ax", "ay", "az", "gx", "gy", "gz"}

    return required.issubset(sample)

# Process the data
def process(samples):

    samples = [s for s in samples if validate_sample(s)]
    samples.sort(key=lambda d: d["t"])
    n = len(samples)

    v = np.zeros(n)
    h = np.zeros(n)

    for i, d in enumerate(samples):

        h[i] = baro_altitude(d["pressure"])
        if i:
            dt = d["t"] - samples[i - 1]["t"]
            dx = haversine(samples[i - 1]["lat"], samples[i - 1]["lon"], d["lat"], d["lon"])
            v[i] = dx / dt if dt else 0

    time_array = [s["t"] for s in samples]
    a = np.gradient(v, np.diff(time_array, prepend=time_array[0]))

    roll = np.zeros(n)
    pitch = np.zeros(n)
    yaw = np.zeros(n)
    k = 0.98

    for i, d in enumerate(samples):

        ax, ay, az = d["ax"], d["ay"], d["az"]
        if i:
            dt = d["t"] - samples[i - 1]["t"]
            gx, gy, gz = map(math.radians, (d["gx"], d["gy"], d["gz"]))
            roll_acc = math.degrees(math.atan2(ay, az))
            pitch_acc = math.degrees(math.atan2(-ax, math.sqrt(ay**2 + az**2)))
            roll[i] = k * (roll[i - 1] + gx * dt) + (1 - k) * roll_acc
            pitch[i] = k * (pitch[i - 1] + gy * dt) + (1 - k) * pitch_acc
            yaw[i] = (yaw[i - 1] + gz * dt) % 360

    return {"v": v, "h": h, "a": a, "pitch": pitch, "roll": roll, "yaw": yaw}

# Load the samples of the data from the JSON
def load_samples(path):

    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error al cargar datos: {e}")
        return []

# Save the results to the JSON
def save_results(results, path):
    try:
        with open(path, "w") as f:
            json.dump({k: v.tolist() for k, v in results.items()}, f, indent=2)
        print(f"Resultados guardados en {path}")
    except Exception as e:
        print(f"Error al guardar resultados: {e}")

#Main Function
if __name__ == "__main__":

    #Input File which is the rocket flight data in JSON format
    input_file = "rocket_flight_data.json"

    #Result file which is the result.json
    output_file = "result.json"

    #Load the samples
    samples = load_samples(input_file)

    #If the samples exists just process the data and save the results in the output file.
    if samples:
        results = process(samples)
        save_results(results, output_file)
