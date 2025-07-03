import json
import requests

# Input and output file paths
INPUT_FILE = "rocket_flight_data.json"
OUTPUT_FILE = "weather_data.json"

# Function to extract the last valid GPS coordinates from flight data
def extract_coordinates(json_path):
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
            samples = data.get("flight_data", [])
            # Search for the last sample with valid latitude and longitude
            for sample in reversed(samples):
                lat = sample.get("latitude")
                lon = sample.get("longitude")
                if lat is not None and lon is not None:
                    return lat, lon
    except Exception as e:
        print(f"Error reading coordinates: {e}")
    return None, None

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

# Main execution
def main():
    print("Extracting coordinates from flight data...")
    lat, lon = extract_coordinates(INPUT_FILE)
    if lat is None or lon is None:
        print("No valid coordinates found.")
        return

    print(f"Coordinates found: Latitude={lat}, Longitude={lon}")
    weather_data = get_weather_data(lat, lon)
    if weather_data:
        try:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(weather_data, f, ensure_ascii=False, indent=4)
            print(f"Weather data saved to '{OUTPUT_FILE}'")
        except Exception as e:
            print("Error saving weather data:", e)

if __name__ == "__main__":
    main()


