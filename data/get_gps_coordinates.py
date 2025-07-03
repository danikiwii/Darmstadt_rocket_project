import serial
import json

def read_coordinates_from_serial(port='/dev/ttyUSB0', baudrate=9600):
    with serial.Serial(port, baudrate, timeout=5) as ser:
        while True:
            line = ser.readline().decode('utf-8').strip()
            try:
                data = json.loads(line)
                lat = data.get("lat")
                lon = data.get("lon")
                if lat and lon:
                    return lat, lon
            except json.JSONDecodeError:
                continue

