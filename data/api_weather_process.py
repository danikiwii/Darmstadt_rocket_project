import json

# Leer el JSON original
with open("data/weather_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Buscar la entrada con la hora deseada
entry_14h = next((item for item in data if item["time"] == "2025-07-08T14:00"), None)

# Sobrescribir el archivo con el objeto plano (sin lista)
if entry_14h is not None:
    with open("data/weather_data.json", "w", encoding="utf-8") as f:
        json.dump(entry_14h, f, ensure_ascii=False, indent=2)
    print("Archivo sobrescrito con la entrada de las 14:00.")
else:
    print("No se encontró la entrada de las 14:00.")
