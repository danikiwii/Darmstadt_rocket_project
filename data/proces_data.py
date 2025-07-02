#Start of data process

#Need to read: temperature, pressure, accelerometer, gyroscope
#All needed imports
import numpy as np, math
import json
import os

#Calculate the altitude from the barometer
def baro_altitude(p, p0=1013.25):
    return 44330 * (1 - (p / p0) ** 0.190294957)

#Calculate the haversine
def haversine(lat1, lon1, lat2, lon2):
    r = 6371000
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))

#Process
def process(samples):
    samples.sort(key=lambda d: d["t"])
    n = len(samples)
    v = np.zeros(n)
    h = np.zeros(n)
    for i, d in enumerate(samples):
        h[i] = baro_altitude(d["pressure"])
        if i:
            dt = samples[i]["t"] - samples[i - 1]["t"]
            dx = haversine(samples[i - 1]["lat"], samples[i - 1]["lon"], d["lat"], d["lon"])
            v[i] = dx / dt if dt else 0
    a = np.gradient(v, np.diff([s["t"] for s in samples], prepend=samples[0]["t"]))
    roll = np.zeros(n)
    pitch = np.zeros(n)
    yaw = np.zeros(n)
    k = 0.98
    for i, d in enumerate(samples):
        ax, ay, az = d["ax"], d["ay"], d["az"]
        if i:
            dt = samples[i]["t"] - samples[i - 1]["t"]
            gx, gy, gz = map(math.radians, (d["gx"], d["gy"], d["gz"]))
            roll_acc = math.degrees(math.atan2(ay, az))
            pitch_acc = math.degrees(math.atan2(-ax, math.sqrt(ay * ay + az * az)))
            roll[i] = k * (roll[i - 1] + gx * dt) + (1 - k) * roll_acc
            pitch[i] = k * (pitch[i - 1] + gy * dt) + (1 - k) * pitch_acc
            yaw[i] = (yaw[i - 1] + gz * dt) % 360
    return {"v": v, "h": h, "a": a, "pitch": pitch, "roll": roll, "yaw": yaw}


#Check that the samples file exists
if __name__ == "__main__":
    try:
        # Cargar samples desde el archivo JSON
        json_path = os.path.join(os.path.dirname(__file__), "rocket_flight_data.json")
        with open(json_path, "r") as f:
            samples = json.load(f)

        res = process(samples)
        
        #Convert the data from the NumPy version to the JSON version
        res_serializable = {k: v.tolist() for k, v in res.items()}

        #Pass all the data to the JSON file
        with open("resultado.json", "w") as f:
            json.dump(res_serializable, f, indent=2)
    except NameError:
        print("Define 'samples' before running the script.")




