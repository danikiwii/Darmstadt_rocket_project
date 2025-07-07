import serial
import json
import argparse
import logging
import sys
import time
from datetime import datetime

# Constants
MAX_JSON_SIZE = 10 * 1024 * 1024  # 10 MB maximum JSON size
DEFAULT_BAUDRATE = 921600         # Faster than standard 115200
BUFFER_READ_SIZE = 4096           # Read chunks of 4KB at a time
TIMEOUT = 0.2                       # Serial port timeout in seconds

def setup_logging():
    """Configure comprehensive logging to file and console"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler('flight_data_capture.log', mode='w'),
            logging.StreamHandler()
        ]
    )
    logging.info("Initialized logging system")

def validate_json_structure(data):
    """Check if the received data has the expected structure"""
    required_fields = ['timestamp', 'acceleration', 'altitude']
    if not isinstance(data, dict):
        return False
    return all(field in data for field in required_fields)

def capture_flight_data(port, baudrate, output_file):
    """
    Capture JSON flight data from serial port with optimized performance
    and robust error handling.
    
    Args:
        port (str): Serial port (e.g., 'COM3' or '/dev/ttyUSB0')
        baudrate (int): Baud rate (e.g., 921600)
        output_file (str): Path to save JSON data
    """
    logging.info(f"Starting capture on {port} at {baudrate} baud")
    start_time = time.time()
    retry_count = 0
    max_retries = 3
    retry_delay = 5
    
    while retry_count < max_retries:
        try:
            with serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=TIMEOUT
            ) as ser:
                
                logging.info(f"Successfully connected to {port}")
                buffer = bytearray()
                json_started = False
                bytes_received = 0
                
                while True:
                    # Read available data in chunks for better performance
                    chunk = ser.read(BUFFER_READ_SIZE)
                    if not chunk:
                        continue
                    
                    bytes_received += len(chunk)
                    buffer.extend(chunk)
                    
                    # Check for maximum size to prevent memory issues
                    if len(buffer) > MAX_JSON_SIZE:
                        logging.error("Maximum JSON size exceeded")
                        raise ValueError("JSON data too large")
                    
                    # Check for complete JSON (start with { and end with })
                    if not json_started and b'{' in buffer:
                        json_started = True
                        # Trim anything before the opening brace
                        buffer = buffer[buffer.index(b'{'):]
                        logging.debug("JSON start detected")
                    
                    if json_started and b'}' in buffer:
                        # Extract the complete JSON
                        json_end = buffer.index(b'}') + 1
                        json_data = buffer[:json_end]
                        remaining_data = buffer[json_end:]
                        
                        try:
                            # Decode and validate JSON
                            decoded = json_data.decode('utf-8', errors='strict')
                            data = json.loads(decoded)
                            
                            if validate_json_structure(data):
                                # Save the valid JSON data
                                with open(output_file, 'w') as f:
                                    json.dump(data, f, indent=2)
                                
                                transfer_time = time.time() - start_time
                                transfer_rate = bytes_received / (transfer_time * 1024)
                                
                                logging.info(f"Successfully saved data to {output_file}")
                                logging.info(f"Transfer stats: {bytes_received/1024:.1f} KB "
                                            f"in {transfer_time:.2f} seconds "
                                            f"({transfer_rate:.1f} KB/s)")
                                return
                            
                            logging.warning("JSON structure validation failed")
                            
                        except (UnicodeDecodeError, json.JSONDecodeError) as e:
                            logging.error(f"JSON decoding failed: {str(e)}")
                        
                        # Reset buffer with remaining data
                        buffer = remaining_data
                        json_started = False
                
        except serial.SerialException as e:
            retry_count += 1
            if retry_count < max_retries:
                logging.warning(f"Attempt {retry_count} failed: {str(e)}")
                logging.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logging.error(f"Max retries reached. Last error: {str(e)}")
                raise
        
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            raise

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Rocket Flight Data Capture Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--port',
        default='COM3',
        help="Serial port name (COM3 on Windows, /dev/ttyUSB0 on Linux)"
    )
    parser.add_argument(
        '--baud',
        type=int,
        default=DEFAULT_BAUDRATE,
        help="Baud rate for serial communication"
    )
    parser.add_argument(
        '--output',
        default='data/rocket_flight_data.json',
        help="Output JSON file path"
    )
    
    args = parser.parse_args()
    
    try:
        setup_logging()
        logging.info(f"Starting rocket flight data capture")
        logging.info(f"Configuration: Port={args.port}, Baud={args.baud}, Output={args.output}")
        
        capture_flight_data(args.port, args.baud, args.output)
        
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)
        
    logging.info("Capture completed successfully")
    sys.exit(0)

if __name__ == "__main__":
    main()