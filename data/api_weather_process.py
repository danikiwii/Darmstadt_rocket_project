import json, os, requests
from datetime import datetime, timezone

INPUT_FILE = "data/rocket_flight_data.json"
OUTPUT_FILE = "data/weather_data.json"
CACHE_FILE = "data/weather_cache.json"
API_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 15

def validate_coords(lat, lon):
    return -90 <= lat <= 90 and -180 <= lon <= 180

def latest_point(path):
    with open(path) as f:
        samples = json.load(f).get("flight_data", [])
    for s in reversed(samples):
        try:
            lat, lon = float(s["latitude"]), float(s["longitude"])
            ts = s["timestamp"]
            if validate_coords(lat, lon) and isinstance(ts, (int, float)):
                if ts > 1e12:
                    ts /= 1e6
                dt = datetime.fromtimestamp(ts, timezone.utc)
                return lat, lon, dt.isoformat(timespec="hours")
        except Exception:
            pass
    return None, None, None

def fetch_weather(lat, lon, use_cache=False):
    if use_cache and os.path.exists(CACHE_FILE):
        try:
            return json.load(open(CACHE_FILE))
        except Exception:
            pass
    params = dict(latitude=lat, longitude=lon,
                  hourly="temperature_2m,precipitation,wind_speed_10m",
                  timezone="UTC", forecast_days=1)
    r = requests.get(API_URL, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    if use_cache:
        json.dump(data, open(CACHE_FILE, "w"))
    return data

def closest_idx(times, target):
    # Make both datetimes timezone-aware (UTC)
    td = datetime.fromisoformat(target).replace(tzinfo=timezone.utc)
    return min(range(len(times)),
               key=lambda i: abs(datetime.fromisoformat(times[i]).replace(tzinfo=timezone.utc) - td).total_seconds())

def main():
    lat, lon, iso_t = latest_point(INPUT_FILE)
    if None in (lat, lon, iso_t):
        print("No coords")
        return
    w = fetch_weather(lat, lon)
    if not w or not w.get("hourly"):
        print("No weather")
        return
    h = w["hourly"]
    i = closest_idx(h["time"], iso_t)
    out = dict(time=h["time"][i],
               temperature_2m=h["temperature_2m"][i],
               precipitation=h["precipitation"][i],
               wind_speed_10m=h.get("wind_speed_10m", [None])[i])
    res = dict(metadata=dict(source="Open-Meteo", generated_at=datetime.now(timezone.utc).isoformat()),
               weather=out)
    json.dump(res, open(OUTPUT_FILE, "w"), indent=2, ensure_ascii=False)
    print("Saved", OUTPUT_FILE)

if __name__ == "__main__":
    main()