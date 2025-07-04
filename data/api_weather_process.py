import json
import requests
from datetime import datetime, timezone

# Input and output file paths
INPUT_FILE = "rocket_flight_data.json"
OUTPUT_FILE = "weather_data.json"

# Function to extract the last valid GPS coordinates and timestamp from flight data
def extract_coordinates_and_time(json_path):
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
            samples = data.get("flight_data", [])
            # Search for the last sample with valid latitude, longitude, and timestamp
            for sample in reversed(samples):
                lat = sample.get("latitude")
                lon = sample.get("longitude")
                timestamp = sample.get("timestamp")
                if lat is not None and lon is not None and timestamp is not None:
                    # Convert microseconds to seconds if needed
                    if timestamp > 1e12:  # likely in microseconds
                        timestamp = timestamp / 1e6
                    dt = datetime.fromtimestamp(timestamp).replace(tzinfo=timezone.utc)
                    # Format to match API time, e.g. '2025-07-04T14:00'
                    iso_time = dt.strftime('%Y-%m-%dT%H:00')
                    return lat, lon, iso_time
    except Exception as e:
        print(f"Error reading coordinates: {e}")
    return None, None, None

# Function to fetch weather data from Open-Meteo API
def get_weather_data(lat, lon):
    url = "https://dwd-api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,precipitation",
        "timezone": "auto"
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error fetching weather data:", response.status_code)
    except Exception as e:
        print("Request failed:", e)
    return None

# Find the closest time index in the API response
def find_closest_time_index(api_times, target_time):
    # api_times: list of ISO strings, target_time: ISO string
    min_diff = float('inf')
    min_idx = 0
    for i, t in enumerate(api_times):
        diff = abs(datetime.fromisoformat(t) - datetime.fromisoformat(target_time))
        if diff.total_seconds() < min_diff:
            min_diff = diff.total_seconds()
            min_idx = i
    return min_idx

# Main execution
def main():
    print("Extracting coordinates and time from flight data...")
    lat, lon, iso_time = extract_coordinates_and_time(INPUT_FILE)
    if lat is None or lon is None or iso_time is None:
        print("No valid coordinates or timestamp found.")
        return

    print(f"Coordinates found: Latitude={lat}, Longitude={lon}, Time={iso_time}")
    weather_data = get_weather_data(lat, lon)
    if weather_data and "hourly" in weather_data:
        api_times = weather_data["hourly"]["time"]
        idx = find_closest_time_index(api_times, iso_time)
        temp = weather_data["hourly"]["temperature_2m"][idx]
        precip = weather_data["hourly"]["precipitation"][idx]

        #The result JSON will only have Temperature and Precipitation from the API of the weather.
        result = {
            "temperature_2m": temp,
            "precipitation": precip
        }
        try:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            print(f"Weather data saved to '{OUTPUT_FILE}' (closest hour)")
        except Exception as e:
            print("Error saving weather data:", e)
    else:
        print("No weather data found for the given coordinates.")

if __name__ == "__main__":
    main()


