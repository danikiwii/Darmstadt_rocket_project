import pandas as pd
import json

def convertir_excel_a_json(ruta_excel, ruta_salida_json):
    # Leer el archivo Excel
    df = pd.read_excel(ruta_excel)

    # Construir la estructura de datos deseada
    flight_data = []
    for _, row in df.iterrows():
        entry = {
            "timestamp": int(row["time"]),
            "latitude": float(row["gps_lat"]),
            "longitude": float(row["gps_lon"]),
            "pressure": float(row["pressure"]),
            "altitude": float(row["altitude"]),
            "acceleration": {
                "x": float(row["accel_x"]),
                "y": float(row["accel_y"]),
                "z": float(row["accel_z"])
            },
            "gyroscope": {
                "x": float(row["gyro_x"]),
                "y": float(row["gyro_y"]),
                "z": float(row["gyro_z"])
            }
        }
        flight_data.append(entry)

    # Guardar en archivo JSON
    salida = {"flight_data": flight_data}
    with open(ruta_salida_json, "w") as f:
        json.dump(salida, f, indent=2)

# Ejemplo de uso
convertir_excel_a_json("data/rocket_log_data.xlsx", "data/rocket_flight_data.json")
