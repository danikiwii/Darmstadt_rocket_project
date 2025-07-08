import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import json

# Configurar sesión con caché y reintento
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Parámetros de la consulta
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 49.678496,
    "longitude": 8.970537,
    "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m"],
    "models": "icon_seamless",
    "timezone": "Europe/Berlin",
    "forecast_days": 1,
    "wind_speed_unit": "ms"
}
responses = openmeteo.weather_api(url, params=params)

# Obtener respuesta
response = responses[0]

# Procesar datos horarios
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(3).ValuesAsNumpy()

# Crear rango de fechas
hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )
}

# Añadir variables al diccionario
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
hourly_data["precipitation"] = hourly_precipitation
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

# Crear DataFrame
hourly_dataframe = pd.DataFrame(data=hourly_data)

# Convertir DataFrame a lista de objetos con el formato deseado
data_list = []
for _, row in hourly_dataframe.iterrows():
    data_list.append({
        "time": row["date"].strftime("%Y-%m-%dT%H:%M"),
        "temperature_2m": row["temperature_2m"],
        "precipitation": row["precipitation"],
        "wind_speed_10m": row["wind_speed_10m"]
    })

# Guardar en JSON
with open("data/weather_data.json", "w", encoding="utf-8") as f:
    json.dump(data_list, f, ensure_ascii=False, indent=2)
print("Weather data saved to weather_data.json")