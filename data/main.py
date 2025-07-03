import json
from get_gps_coordinates import read_coordinates_from_serial
from get_weather_data import get_weather_data

def main():
    print("Waiting for GPS coordinates from ESP32...")
    lat, lon = read_coordinates_from_serial()
    print(f"Coordinates received: {lat}, {lon}")

    weather_data = get_weather_data(lat, lon)
    if weather_data:
        with open("weather_data.json", "w", encoding="utf-8") as f:
            json.dump(weather_data, f, ensure_ascii=False, indent=4)
        print("Weather data saved to 'weather_data.json'")

if __name__ == "__main__":
    main()

