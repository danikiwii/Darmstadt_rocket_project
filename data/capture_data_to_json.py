import serial
import time
import json

# Serial port configuration
SERIAL_PORT = 'COM3'       # Replace with your actual serial port (e.g., '/dev/ttyUSB0' on Linux)
BAUD_RATE = 115200         # Must match the baud rate used by the ESP32
OUTPUT_FILE = 'rocket_flight_data.json'  # Output file where the JSON data will be saved

# Function to capture JSON data sent over serial and save it to a file
def capture_json_from_serial(port, baudrate, output_file):
    # Open the serial port
    with serial.Serial(port, baudrate, timeout=1) as ser:
        print(f"Listening on {port} at {baudrate} baud...")
        buffer = ""           # Buffer to accumulate the JSON text
        capturing = False     # Flag to indicate whether we're inside a JSON block

        while True:
            # Read a line from the serial port
            line = ser.readline().decode(errors='ignore').strip()

            if not line:
                continue  # Skip empty lines

            # Detect the start of the JSON array
            if line.startswith('['):
                capturing = True
                buffer = line + '\n'
                print("Start of JSON block detected")

            # Detect the end of the JSON array
            elif line.startswith(']') and capturing:
                buffer += line
                print("End of JSON block detected")
                break  # Exit the loop once the full JSON block is received
            # Accumulate lines inside the JSON block
            elif capturing:
                buffer += line + '\n'

        # Try to parse the JSON and save it to a file
        try:
            data = json.loads(buffer)
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Data saved to {output_file}")
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)

# Call this function after the rocket has landed and the ESP32 is connected to the computer
# Uncomment the line below to run the capture
# capture_json_from_serial(SERIAL_PORT, BAUD_RATE, OUTPUT_FILE)
