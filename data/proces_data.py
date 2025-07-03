"""
Rocket Flight Data Processor
Processes JSON data from ESP32-S3 logger and computes:
- Barometric altitude
- Horizontal velocity from GPS
- Acceleration from velocity
- Orientation (pitch, roll, yaw) using complementary filter
"""

import json
import numpy as np
import math

# Constants
EARTH_RADIUS = 6371000  # meters
SEA_LEVEL_PRESSURE = 1013.25  # hPa

# Compute altitude from pressure
def baro_altitude(p, p0=SEA_LEVEL_PRESSURE):
    return 44330 * (1 - (p / p0) ** 0.190294957)

# Compute distance between GPS coordinates
def haversine(lat1, lon1, lat2, lon2):
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS * math.asin(math.sqrt(a))

# Validate sample structure
def validate_sample(sample):
    required = {"timestamp", "latitude", "longitude", "pressure", "acceleration", "gyroscope"}
    return (
        required.issubset(sample)
        and all(k in sample["acceleration"] for k in ("x", "y", "z"))
        and all(k in sample["gyroscope"] for k in ("x", "y", "z"))
    )

# Process the list of samples and compute derived quantities
def process(samples):
    samples = [s for s in samples if validate_sample(s)]
    samples.sort(key=lambda d: d["timestamp"])
    n = len(samples)

    v = np.zeros(n)  # Horizontal velocity
    h = np.zeros(n)  # Barometric altitude

    # Compute altitude and velocity
    for i, d in enumerate(samples):
        h[i] = baro_altitude(d["pressure"])
        if i:
            dt = (d["timestamp"] - samples[i - 1]["timestamp"]) / 1e6  # Convert µs to seconds
            dx = haversine(
                samples[i - 1]["latitude"], samples[i - 1]["longitude"],
                d["latitude"], d["longitude"]
            )
            v[i] = dx / dt if dt else 0

    # Compute acceleration from velocity
    time_array = [s["timestamp"] / 1e6 for s in samples]
    a = np.gradient(v, np.diff(time_array, prepend=time_array[0]))

    # Orientation estimation using complementary filter
    roll = np.zeros(n)
    pitch = np.zeros(n)
    yaw = np.zeros(n)
    k = 0.98  # Complementary filter constant

    for i, d in enumerate(samples):
        ax, ay, az = d["acceleration"]["x"], d["acceleration"]["y"], d["acceleration"]["z"]
        if i:
            dt = (d["timestamp"] - samples[i - 1]["timestamp"]) / 1e6
            gx, gy, gz = map(math.radians, (
                d["gyroscope"]["x"], d["gyroscope"]["y"], d["gyroscope"]["z"]
            ))
            roll_acc = math.degrees(math.atan2(ay, az))
            pitch_acc = math.degrees(math.atan2(-ax, math.sqrt(ay**2 + az**2)))
            roll[i] = k * (roll[i - 1] + gx * dt) + (1 - k) * roll_acc
            pitch[i] = k * (pitch[i - 1] + gy * dt) + (1 - k) * pitch_acc
            yaw[i] = (yaw[i - 1] + gz * dt) % 360

    return {
        "velocity": v.tolist(),
        "altitude": h.tolist(),
        "acceleration": a.tolist(),
        "pitch": pitch.tolist(),
        "roll": roll.tolist(),
        "yaw": yaw.tolist()
    }

# Load samples from a JSON file
def load_samples(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return data.get("flight_data", [])
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

# Save results to a JSON file
def save_results(results, path):
    try:
        with open(path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {path}")
    except Exception as e:
        print(f"Error saving results: {e}")

# Main execution
if __name__ == "__main__":
    input_file = "rocket_flight_data.json"  # Input JSON file from Arduino
    output_file = "result.json"             # Output file with processed results
    samples = load_samples(input_file)
    if samples:
        results = process(samples)
        save_results(results, output_file)
