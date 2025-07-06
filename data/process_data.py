import json
import math
import numpy as np
from scipy.signal import savgol_filter

# Constants
EARTH_RADIUS = 6371000  # Earth's radius in meters
SEA_LEVEL_PRESSURE = 1013.25  # Standard sea level pressure in hPa
MIN_TIME_DIFF = 1e-3  # Minimum valid time difference between samples (seconds)
MAX_ACCEL = 100.0  # Maximum allowed acceleration (m/s²)
MAX_VELOCITY = 500.0  # Maximum allowed velocity (m/s)

def baro_altitude(p, p0=SEA_LEVEL_PRESSURE):
    """Calculate altitude from barometric pressure using barometric formula"""
    return 0.0 if p <= 0 else 44330 * (1 - (p / p0) ** 0.190294957)

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS coordinates using Haversine formula"""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS * math.asin(math.sqrt(a))

def validate_sample(s):
    """Check if sample contains all required fields with valid values"""
    req = {"timestamp", "latitude", "longitude", "pressure", "acceleration", "gyroscope"}
    if not req.issubset(s):
        return False
    if not all(k in s["acceleration"] for k in ("x", "y", "z")):
        return False
    if not all(k in s["gyroscope"] for k in ("x", "y", "z")):
        return False
    if abs(s["latitude"]) > 90 or abs(s["longitude"]) > 180:
        return False
    return s["timestamp"] > 0

def smooth_data(data, win=5, poly=2):
    """Apply Savitzky-Golay filter to smooth noisy data"""
    n = len(data)
    win = min(win if win % 2 else win + 1, n if n % 2 else n - 1)  # Ensure odd window size
    return savgol_filter(data, win, poly) if n > win else data

def process(samples):
    """Process raw flight data to calculate derived metrics"""
    samples = sorted([s for s in samples if validate_sample(s)], key=lambda d: d["timestamp"])
    n = len(samples)
    if n < 2:
        return {}

    # Extract base measurements
    t = np.array([s["timestamp"] / 1e6 for s in samples])  # Convert to seconds
    alt = np.array([baro_altitude(s["pressure"]) for s in samples])  # Calculate altitudes
    
    # Calculate velocity and acceleration
    vel = np.zeros(n)
    acc = np.zeros(n)
    
    for i in range(1, n):
        dt = (samples[i]["timestamp"] - samples[i-1]["timestamp"]) / 1e6
        if dt > MIN_TIME_DIFF:
            dx = haversine(samples[i-1]["latitude"], samples[i-1]["longitude"],
                           samples[i]["latitude"],  samples[i]["longitude"])
            vel[i] = dx / dt
            if abs(vel[i]) > MAX_VELOCITY:
                vel[i] = vel[i-1]  # Apply velocity limit
        else:
            vel[i] = vel[i-1]
    
    vel = smooth_data(vel)  # Smooth velocity data
    
    for i in range(1, n):
        dt = max((samples[i]["timestamp"] - samples[i-1]["timestamp"]) / 1e6, MIN_TIME_DIFF)
        acc[i] = (vel[i] - vel[i-1]) / dt
        if abs(acc[i]) > MAX_ACCEL:
            acc[i] = acc[i-1]  # Apply acceleration limit
    acc = smooth_data(acc)  # Smooth acceleration data

    # Calculate orientation using complementary filter
    roll = np.zeros(n)
    pitch = np.zeros(n)
    yaw = np.zeros(n)
    k = 0.98  # Complementary filter coefficient

    # Initialize with first sample
    ax0, ay0, az0 = samples[0]["acceleration"].values()
    roll[0]  = math.degrees(math.atan2(ay0, math.sqrt(ax0**2 + az0**2)))
    pitch[0] = math.degrees(math.atan2(-ax0, math.sqrt(ay0**2 + az0**2)))

    for i in range(1, n):
        dt = max((samples[i]["timestamp"] - samples[i-1]["timestamp"]) / 1e6, MIN_TIME_DIFF)
        gx = math.radians(samples[i]["gyroscope"]["x"])
        gy = math.radians(samples[i]["gyroscope"]["y"])
        gz = math.radians(samples[i]["gyroscope"]["z"])
        ax = samples[i]["acceleration"]["x"]
        ay = samples[i]["acceleration"]["y"]
        az = samples[i]["acceleration"]["z"]

        # Calculate orientation from accelerometer
        roll_acc  = math.degrees(math.atan2(ay, math.sqrt(ax**2 + az**2)))
        pitch_acc = math.degrees(math.atan2(-ax, math.sqrt(ay**2 + az**2)))

        # Complementary filter combines gyro and accelerometer data
        roll[i]  = k * (roll[i-1]  + gx * dt) + (1 - k) * roll_acc
        pitch[i] = k * (pitch[i-1] + gy * dt) + (1 - k) * pitch_acc
        yaw[i]   = (yaw[i-1] + gz * dt) % 360  # Yaw from gyro only

    return {
        "timestamp": t.tolist(),
        "altitude":  alt.tolist(),
        "velocity":  vel.tolist(),
        "acceleration": acc.tolist(),
        "roll":  roll.tolist(),
        "pitch": pitch.tolist(),
        "yaw":   yaw.tolist()
    }

def load_samples(path):
    """Load flight data from JSON file"""
    try:
        with open(path) as f:
            data = json.load(f)
            return data.get("flight_data", []) if isinstance(data, dict) else data
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

def save_results(res, path):
    """Save processed results to JSON file"""
    try:
        with open(path, "w") as f:
            json.dump(res, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving results: {e}")
        return False

if __name__ == "__main__":
    # Main execution
    inp, out = "data/rocket_flight_data.json", "data/processed_data.json"
    samples = load_samples(inp)
    if not samples:
        print("No valid data")
    else:
        res = process(samples)
        if res and save_results(res, out):
            print("Done")