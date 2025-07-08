import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

# Setup del cliente Open-Meteo con caché y reintentos
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Parámetros de la API
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 49.6785,
    "longitude": 8.97054,
    "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m"],
    "models": "icon_seamless",
    "timezone": "Europe/Berlin",
    "forecast_days": 1,
    "wind_speed_unit": "ms"
}
responses = openmeteo.weather_api(url, params=params)

# Procesar la respuesta
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Obtener datos horarios
hourly = response.Hourly()
hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval())
    ),
    "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
    "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
    "precipitation": hourly.Variables(2).ValuesAsNumpy(),
    "wind_speed_10m": hourly.Variables(3).ValuesAsNumpy()
}

# Crear DataFrame y filtrar para las 14:00
hourly_dataframe = pd.DataFrame(data=hourly_data)
data_14h = hourly_dataframe[hourly_dataframe['date'].dt.hour == 14]

# Mostrar los datos a las 14:00
print("\nDatos a las 14:00:")
print(data_14h)

# Guardar en archivo JSON
data_14h.to_json("datos_14h.json", orient="records", date_format="iso", indent=2)
print("\nDatos guardados en 'datos_14h.json'")
