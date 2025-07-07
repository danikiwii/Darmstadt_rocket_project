import json, os, requests
from datetime import datetime, timezone

# File paths and API configuration
INPUT_FILE = "data/rocket_flight_data.json"       # Source file containing rocket trajectory data
OUTPUT_FILE = "data/weather_data.json"            # Output file for weather results
CACHE_FILE = "data/weather_cache.json"            # Cache file to avoid repeated API calls
API_URL = "https://api.open-meteo.com/v1/forecast"  # Weather API endpoint
TIMEOUT = 15                                      # API request timeout in seconds

def validate_coords(lat, lon):
    """Validate that latitude and longitude are within Earth's valid ranges"""
    return -90 <= lat <= 90 and -180 <= lon <= 180

def latest_point(path):
    """
    Extract the most recent valid coordinates and timestamp from flight data.
    Processes data in reverse to find the latest valid entry.
    Returns: (latitude, longitude, ISO-formatted UTC timestamp) or (None, None, None) if no valid data
    """
    with open(path) as f:
        samples = json.load(f).get("flight_data", [])
    
    for s in reversed(samples):  # Process from newest to oldest
        try:
            lat, lon = float(s["latitude"]), float(s["longitude"])
            ts = s["timestamp"]
            
            if validate_coords(lat, lon) and isinstance(ts, (int, float)):
                # Convert milliseconds to seconds if timestamp is too large
                if ts > 1e12:  # Likely in milliseconds
                    ts /= 1e6
                
                # Create timezone-aware datetime object
                dt = datetime.fromtimestamp(ts, timezone.utc)
                return lat, lon, dt.isoformat(timespec="hours")  # Return with hour precision
        except Exception:
            continue  # Skip malformed entries
    
    return None, None, None  # No valid data found

def fetch_weather(lat, lon, use_cache=False):
    """
    Fetch weather data from API or cache.
    Args:
        lat, lon: Coordinates for weather data
        use_cache: If True, uses cached data when available
    Returns: Dictionary containing weather data
    """
    # Check cache first if enabled
    if use_cache and os.path.exists(CACHE_FILE):
        try:
            return json.load(open(CACHE_FILE))
        except Exception:
            pass  # Fall through to API call if cache fails
    
    # API request parameters
    params = dict(
        latitude=lat,
        longitude=lon,
        hourly="temperature_2m,precipitation,wind_speed_10m",
        timezone="UTC",
        forecast_days=1
    )
    
    # Make API request
    r = requests.get(API_URL, params=params, timeout=TIMEOUT)
    r.raise_for_status()  # Raise exception for bad status codes
    data = r.json()
    
    # Update cache if enabled
    if use_cache:
        json.dump(data, open(CACHE_FILE, "w"))
    
    return data

def closest_idx(times, target):
    """
    Find the index of the time entry closest to the target timestamp.
    Args:
        times: List of time strings in ISO format
        target: Target time string in ISO format
    Returns: Index of closest matching time
    """
    # Convert target to timezone-aware datetime (UTC)
    td = datetime.fromisoformat(target).replace(tzinfo=timezone.utc)
    
    return min(
        range(len(times)),
        key=lambda i: abs(
            datetime.fromisoformat(times[i]).replace(tzinfo=timezone.utc) - td
        ).total_seconds()
    )

def main():
    """
    Main execution flow:
    1. Get latest rocket coordinates and timestamp
    2. Fetch weather data for those coordinates
    3. Find weather data closest to the rocket's timestamp
    4. Save relevant weather data to output file
    """
    # Step 1: Get latest valid rocket position
    lat, lon, iso_t = latest_point(INPUT_FILE)
    if None in (lat, lon, iso_t):
        print("Error: No valid coordinates found in input data")
        return
    
    # Step 2: Fetch weather data
    w = fetch_weather(lat, lon)
    if not w or not w.get("hourly"):
        print("Error: No weather data received from API")
        return
    
    # Step 3: Find closest weather data point
    h = w["hourly"]
    i = closest_idx(h["time"], iso_t)
    
    # Step 4: Prepare and save output
    out = dict(
        time=h["time"][i],                          # Timestamp of weather data
        temperature_2m=h["temperature_2m"][i],      # Temperature at 2m height (°C)
        precipitation=h["precipitation"][i],        # Precipitation amount (mm)
        wind_speed_10m=h.get("wind_speed_10m", [None])[i]  # Wind speed at 10m height (km/h)
    )
    
    # Save results without metadata
    json.dump(out, open(OUTPUT_FILE, "w"), indent=2, ensure_ascii=False)
    print(f"Success: Weather data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()