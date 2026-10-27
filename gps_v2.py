import pynmea2
import logging
import serial
from time import sleep

logging.basicConfig(level=logging.INFO, filename="gps_logs.log", filemode="a", format="%(asctime)s [%(levelname)s] %(message)s")

PORT = "/dev/ttyACM0" # "COM4" for windows
BAUDRATE = 9600
TIMEOUT = 1

# Combined GNSS data structure
gnss_data = {
    "date": None,
    "time_utc": None,
    "gga_time_utc": None,
    "latitude": None,
    "longitude": None,
    "altitude_m": None,
    "satellites_used": None,
    "fix_quality": None,
    "speed_km_h": None,
    "course_degrees": None,
    "status": None,
}

# Track which valid sentences have arrived
received_sentences = set()

def optional_float(value):
    return None if value in (None, "") else float(value)

def process_data(raw_data) -> tuple | None:
    try:
        message = pynmea2.parse(raw_data, check=True)

        if message.sentence_type == "GGA": # Process only GGA sentences 

            # Check position fix quality
            if message.gps_qual in (0, "0", "", None):
                return None
            
            return  "GGA", {
                "latitude": message.latitude,
                "longitude": message.longitude,
                "altitude_m": optional_float(message.altitude),
                "satellites_used": int(message.num_sats or 0),
                "fix_quality": message.gps_qual,
                "gga_time_utc": str(message.timestamp),
            }

        elif message.sentence_type == "RMC":

            # Check navigation status
            if message.status != "A":
                return None

            speed_knots = optional_float(message.spd_over_grnd)
            return "RMC", {
                "latitude": message.latitude,
                "longitude": message.longitude,
                "speed_km_h": convert_speed_to_km_h(speed_knots) if message.spd_over_grnd else None, # speed_knots to km/h
                "course_degrees": (float(message.true_course) if message.true_course else None),
                "date": str(message.datestamp),
                "time_utc": str(message.timestamp),
                "status": message.status,
            }
        return None
    
    except (pynmea2.ParseError, ValueError) as error:
                print(f"NMEA parsing error: {error}")
                return None

def convert_speed_to_km_h(knots)->float | None:
     # 1 knot = 1 nauttical mile/hour
     # 1 nauttical mile = 1852 meters
     # 1 nauttical mile = 1.852 kilometers
     speed_km_h = knots * 1.852 #km/h
     return speed_km_h

def serial_config()->serial.Serial | None:
    conection_trails = 5
    while conection_trails > 0:
        try:
            serial_conn_gps = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)
            print("Serial connected")
            logging.info("Serial Connected")
            serial_conn_gps.reset_input_buffer()
            sleep(1)
            return serial_conn_gps

        except serial.SerialException as error:
            print(f"Connection failed: {error}")
            print(f"Retrying in 2 seconds ... ")
            logging.error(f"Connection failed: {error}")
            conection_trails -= 1
            sleep(2)   
    
def main():
    
    serial_data = serial_config()

    if serial_data == None:
        print("Faild to connect to serial port")
        return 
    
    try:
        while True:
            raw = serial_data.readline()

            if not raw.endswith(b"\n"):
                continue

            line = raw.decode("ascii", errors="replace").strip()

            if not line.startswith("$"):
                continue

            gps_data = process_data(line) 

            if gps_data is None:
                continue

            sentence_type, new_data = gps_data

            # Merge new fields into the shared dictionary
            gnss_data.update(new_data)
            received_sentences.add(sentence_type)

            # Display only after both valid sentences arrive
            if {"GGA", "RMC"}.issubset(received_sentences):
                print(gnss_data)
                logging.info("%s", gnss_data)

    except KeyboardInterrupt:
        print("\nGNSS data stream stopped")
        logging.warning("GNSS data stream stopped")

    finally:
        serial_data.close()

if __name__ == "__main__":
    main()