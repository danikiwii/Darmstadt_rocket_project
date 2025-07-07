import serial
import time
import random
import json
from datetime import datetime

def generate_fake_data(points=2000):
    """Genera datos de vuelo simulados"""
    base_altitude = random.uniform(100, 200)
    data = {
        "metadata": {
            "id": "SIM-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
            "type": "simulation"
        },
        "data": []
    }
    
    for i in range(points):
        timestamp = time.time() + i * 0.1
        accel_z = random.uniform(0.8, 15.0)  # Simula despegue y ascenso
        altitude = base_altitude + i * random.uniform(0.1, 3.0)
        
        data["data"].append({
            "t": timestamp,
            "a": {
                "x": random.uniform(-0.5, 0.5),
                "y": random.uniform(-0.5, 0.5),
                "z": accel_z
            },
            "alt": altitude,
            "temp": random.uniform(15, 35)
        })
    
    return data

def simulate_rocket(port='COM3', baudrate=921600, points=500):
    """Simula el envío de datos por serial"""
    try:
        # Configuración del puerto
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        time.sleep(2)  # Espera a que se establezca la conexión

        print(f"🚀 Simulación iniciada en {port} @ {baudrate} baudios")
        print("Ctrl+C para detener...")

        # Genera y envía datos
        fake_data = generate_fake_data(points)
        json_str = json.dumps(fake_data, indent=2)
        
        # Envía con delimitadores
        ser.write(b"BEGIN_JSON\n")
        for line in json_str.split('\n'):
            ser.write(line.encode() + b'\n')
            time.sleep(0.01)  # Pequeño delay entre líneas
        ser.write(b"END_JSON\n")

        print("✅ Datos enviados correctamente")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Simulador de Datos de Cohete")
    parser.add_argument('--port', default='COM3', help='Puerto serial')
    parser.add_argument('--baud', type=int, default=921600, help='Baud rate')
    parser.add_argument('--points', type=int, default=500, help='Puntos de datos a generar')
    
    args = parser.parse_args()
    
    simulate_rocket(
        port=args.port,
        baudrate=args.baud,
        points=args.points
    )