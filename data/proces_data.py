"""
Rocket Flight Data Processor - Improved Version
Processes JSON data from ESP32-S3 logger with robust calculations
"""

import json
import numpy as np
import math
from scipy.signal import savgol_filter

# Constants
EARTH_RADIUS = 6371000  # meters
SEA_LEVEL_PRESSURE = 1013.25  # hPa
MIN_TIME_DIFF = 0.001  # 1ms minimum time difference for calculations
MAX_ACCEL = 100.0  # m/s^2 - reasonable limit for rocket acceleration
MAX_VELOCITY = 500.0  # m/s - reasonable limit for horizontal velocity

# Compute altitude from pressure using barometric formula
def baro_altitude(p, p0=SEA_LEVEL_PRESSURE):
    if p <= 0:
        return 0.0
    return 44330 * (1 - (p / p0) ** 0.190294957)

# Compute distance between GPS coordinates using Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * EARTH_RADIUS * math.asin(math.sqrt(a))

# Validate sample structure and data quality
def validate_sample(sample):
    required = {
        "timestamp", 
        "latitude", 
        "longitude", 
        "pressure", 
        "acceleration", 
        "gyroscope"
    }
    
    # Check required fields exist
    if not required.issubset(sample):
        return False
    
    # Check sensor data structure
    if not all(k in sample["acceleration"] for k in ("x", "y", "z")):
        return False
    if not all(k in sample["gyroscope"] for k in ("x", "y", "z")):
        return False
    
    # Check for valid GPS coordinates
    if abs(sample["latitude"]) > 90 or abs(sample["longitude"]) > 180:
        return False
    
    # Check for valid timestamp
    if sample["timestamp"] <= 0:
        return False
    
    return True

# Smooth data using Savitzky-Golay filter
def smooth_data(data, window_length=5, polyorder=2):
    if len(data) > window_length:
        return savgol_filter(data, window_length, polyorder)
    return data

# Process the list of samples and compute derived quantities
def process(samples):
    # Filter and sort valid samples
    samples = [s for s in samples if validate_sample(s)]
    samples.sort(key=lambda d: d["timestamp"])
    n = len(samples)

    if n < 2:  # Need at least 2 samples for calculations
        return {}

    # Initialize arrays
    time_array = np.array([s["timestamp"] / 1e6 for s in samples])  # Convert μs to seconds
    h = np.zeros(n)  # Barometric altitude
    v = np.zeros(n)  # Horizontal velocity
    a = np.zeros(n)  # Acceleration
    
    # Calculate altitude from pressure
    for i, d in enumerate(samples):
        h[i] = baro_altitude(d["pressure"])

    # Calculate velocity between consecutive GPS points
    for i in range(1, n):
        dt = (samples[i]["timestamp"] - samples[i-1]["timestamp"]) / 1e6
        
        # Only calculate if we have valid time difference and position change
        if dt > MIN_TIME_DIFF:
            lat1, lon1 = samples[i-1]["latitude"], samples[i-1]["longitude"]
            lat2, lon2 = samples[i]["latitude"], samples[i]["longitude"]
            
            # Only calculate if we have valid position change
            if (lat1 != lat2) or (lon1 != lon2):
                dx = haversine(lat1, lon1, lat2, lon2)
                v[i] = dx / dt
                
                # Apply velocity limits
                if abs(v[i]) > MAX_VELOCITY:
                    v[i] = v[i-1]  # Revert to previous value if over limit
            else:
                v[i] = v[i-1]  # No position change
        else:
            v[i] = v[i-1]  # Time difference too small

    # Smooth velocity data before calculating acceleration
    if n > 5:
        v_smooth = smooth_data(v)
    else:
        v_smooth = v.copy()

    # Calculate acceleration from smoothed velocity
    for i in range(1, n):
        dt = (samples[i]["timestamp"] - samples[i-1]["timestamp"]) / 1e6
        if dt > MIN_TIME_DIFF:
            a[i] = (v_smooth[i] - v_smooth[i-1]) / dt
            
            # Apply acceleration limits
            if abs(a[i]) > MAX_ACCEL:
                a[i] = a[i-1]  # Revert to previous value if over limit
        else:
            a[i] = a[i-1]  # Time difference too small

    # Smooth acceleration data
    if n > 5:
        a_smooth = smooth_data(a)
    else:
        a_smooth = a.copy()

    # Orientation estimation using complementary filter
    roll = np.zeros(n)
    pitch = np.zeros(n)
    yaw = np.zeros(n)
    k = 0.98  # Complementary filter constant

    # Initialize orientation from first sample
    ax0 = samples[0]["acceleration"]["x"]
    ay0 = samples[0]["acceleration"]["y"]
    az0 = samples[0]["acceleration"]["z"]
    
    roll[0] = math.degrees(math.atan2(ay0, math.sqrt(ax0**2 + az0**2))
    pitch[0] = math.degrees(math.atan2(-ax0, math.sqrt(ay0**2 + az0**2))
    yaw[0] = 0.0

    for i in range(1, n):
        dt = (samples[i]["timestamp"] - samples[i-1]["timestamp"]) / 1e6
        if dt <= 0:
            dt = MIN_TIME_DIFF  # Prevent division by zero
            
        # Get gyroscope readings (convert to rad/s)
        gx = math.radians(samples[i]["gyroscope"]["x"])
        gy = math.radians(samples[i]["gyroscope"]["y"])
        gz = math.radians(samples[i]["gyroscope"]["z"])
        
        # Get accelerometer readings
        ax = samples[i]["acceleration"]["x"]
        ay = samples[i]["acceleration"]["y"]
        az = samples[i]["acceleration"]["z"]
        
        # Calculate orientation from accelerometer
        roll_acc = math.degrees(math.atan2(ay, math.sqrt(ax**2 + az**2))
        pitch_acc = math.degrees(math.atan2(-ax, math.sqrt(ay**2 + az**2)))
        
        # Complementary filter
        roll[i] = k * (roll[i-1] + gx * dt) + (1 - k) * roll_acc
        pitch[i] = k * (pitch[i-1] + gy * dt) + (1 - k) * pitch_acc
        yaw[i] = (yaw[i-1] + gz * dt) % 360

    return {
        "timestamp": time_array.tolist(),
        "velocity": v_smooth.tolist(),
        "altitude": h.tolist(),
        "acceleration": a_smooth.tolist(),
        "pitch": pitch.tolist(),
        "roll": roll.tolist(),
        "yaw": yaw.tolist()
    }

# Load samples from a JSON file with error handling
def load_samples(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data.get("flight_data", [])
            elif isinstance(data, list):
                return data
            else:
                print("Unexpected data format in JSON file")
                return []
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return []

# Save results to a JSON file with pretty printing
def save_results(results, path):
    try:
        with open(path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Successfully saved results to {path}")
        return True
    except Exception as e:
        print(f"Error saving results: {str(e)}")
        return False

# Main execution with error handling
if __name__ == "__main__":
    input_file = "data/rocket_flight_data.json"
    output_file = "data/result.json"
    
    print("Loading flight data...")
    samples = load_samples(input_file)
    
    if not samples:
        print("No valid samples found or error loading data")
    else:
        print(f"Processing {len(samples)} samples...")
        results = process(samples)
        
        if results:
            if save_results(results, output_file):
                print("Processing completed successfully")
            else:
                print("Error saving results")
        else:
            print("Processing resulted in empty dataset")