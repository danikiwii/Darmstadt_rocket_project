import serial
import json
import argparse
import logging
import sys
import time

def setup_logging():
    """Configure logging to file and console with timestamps."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('serial_capture.log'),  # Log to file
            logging.StreamHandler()                     # Log to console
        ]
    )

def capture_json_from_serial(port, baudrate, output_file):
    """
    Capture JSON data from serial port with error handling and retries.
    Args:
        port (str): Serial port (e.g., 'COM3' or '/dev/ttyUSB0')
        baudrate (int): Baud rate (e.g., 115200)
        output_file (str): Path to save JSON data
    """
    max_retries = 3       # Max connection attempts
    retry_delay = 5       # Seconds between retries

    for attempt in range(max_retries):
        try:
            # Open serial connection with timeout
            with serial.Serial(port, baudrate, timeout=2) as ser:
                logging.info(f"Connected to {port}")
                buffer = ""
                
                while True:
                    # Read line and handle decoding errors
                    line = ser.readline().decode(errors='ignore').strip()
                    
                    # Detect JSON start/end and build buffer
                    if line.startswith('{'):
                        buffer = line
                    elif line and buffer:
                        buffer += line
                    
                    # Validate complete JSON
                    if buffer.endswith('}') and buffer.startswith('{'):
                        try:
                            data = json.loads(buffer)  # Parse JSON
                            with open(output_file, 'w') as f:
                                json.dump(data, f, indent=2)
                            logging.info(f"Data saved to {output_file}")
                            return  # Exit on success
                        
                        except json.JSONDecodeError as e:
                            logging.error(f"Invalid JSON: {e}")
                            buffer = ""  # Reset buffer
                            
        except serial.SerialException as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(retry_delay)
    
    logging.error("Max retries reached. Exiting.")
    sys.exit(1)

if __name__ == "__main__":
    setup_logging()
    
    # Configure command-line arguments
    parser = argparse.ArgumentParser(description="Capture JSON data from serial port")
    parser.add_argument('--port', default='COM3', help='Serial port name')
    parser.add_argument('--baud', type=int, default=115200, help='Baud rate')
    parser.add_argument('--output', default='data/rocket_flight_data.json', help='Output JSON file')
    args = parser.parse_args()
    
    # Start capture
    capture_json_from_serial(args.port, args.baud, args.output)