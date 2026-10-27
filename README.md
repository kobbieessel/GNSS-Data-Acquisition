# GNSS Data Acquisition for Robot Navigation

A Python-based project for acquiring and processing Global Navigation Satellite System (GNSS) data for future use in robot navigation and localization. It reads NMEA sentences from a GNSS receiver over a serial connection and organizes valid positioning and motion information into a structured format that can be consumed by other robotics software.

> **Project status:** Early-stage prototype focused on data acquisition and parsing. This project does not currently perform autonomous navigation, route planning, or sensor fusion.

## Overview

Robotic navigation systems need reliable position and motion measurements. This project provides an initial software interface between a GNSS receiver and Python-based robotics applications.

The application reads incoming NMEA data, processes `GGA` and `RMC` sentences, and maintains the latest accepted values in a combined data structure. The resulting information is intended to serve as an input to future navigation and localization work.

## Current Features

- Read NMEA messages from a GNSS receiver using serial communication.
- Parse `GGA` and `RMC` sentences with `pynmea2`.
- Check GNSS fix quality (`GGA`) and data validity (`RMC`) before accepting measurements.
- Extract coordinates, altitude, satellites used, speed, course, and timestamps when available.
- Convert speed from knots to kilometers per hour.
- Maintain a combined dictionary of the latest accepted GNSS fields.
- Record diagnostic messages in a log file.

## Technologies

- **Language:** Python 3
- **Serial communication:** [`pyserial`](https://pyserial.readthedocs.io/)
- **NMEA parsing:** [`pynmea2`](https://github.com/Knio/pynmea2)
- **Hardware:** A compatible GNSS receiver exposed as a serial device

## Getting Started

### Prerequisites

- Python 3 installed
- A connected GNSS receiver that outputs NMEA sentences over a serial interface
- Permission to access the serial device

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Replace `YOUR_USERNAME` and `YOUR_REPOSITORY` with your GitHub details.

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, activate it with `.venv\Scripts\activate` instead.

### 3. Install dependencies

```bash
python -m pip install pyserial pynmea2
```

Alternatively, if your repository includes a `requirements.txt` file:

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the serial connection

In your Python script, set the serial port and baud rate to match your receiver:

```python
PORT = "/dev/ttyACM0"  # Example on Linux; may change when reconnected
BAUDRATE = 9600          # Confirm against your receiver's configuration
TIMEOUT = 1
```

On Windows, the port may be named something like `COM4`. On Linux, find connected serial devices using `ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null`.

### 5. Run the application

```bash
python gps_tracker.py
```

> This command assumes the main script is named `gps_tracker.py`. Replace it with your actual filename if different.

For best results, operate the receiver where it has a clear view of the sky. A valid satellite fix may take time to become available.

## GNSS Data Fields

| Field | Description | Source |
| --- | --- | --- |
| `date` | UTC date reported by the receiver | RMC |
| `time_utc` | UTC time from the RMC sentence | RMC |
| `gga_time_utc` | UTC time from the GGA sentence | GGA |
| `latitude` | Latitude in decimal degrees | GGA / RMC |
| `longitude` | Longitude in decimal degrees | GGA / RMC |
| `altitude_m` | Altitude in meters | GGA |
| `satellites_used` | Number of satellites used in the solution | GGA |
| `fix_quality` | Receiver-reported GNSS fix quality | GGA |
| `speed_km_h` | Ground speed in kilometers per hour | RMC |
| `course_degrees` | Course over ground in degrees | RMC |
| `status` | RMC navigation-data status | RMC |

### Example data structure

The following is **illustrative sample data**, not a recorded location:

```json
{
  "date": "2026-10-26",
  "time_utc": "14:30:05",
  "gga_time_utc": "14:30:05",
  "latitude": 37.6,
  "longitude": -77.4,
  "altitude_m": 100.0,
  "satellites_used": 9,
  "fix_quality": 1,
  "speed_km_h": 12.0,
  "course_degrees": 85.0,
  "status": "A"
}
```

Values and representations depend on the incoming NMEA messages and how the script formats them. Some fields will remain `None` until an applicable valid sentence has been received.

## How It Works

1. Open the serial connection to the GNSS receiver.
2. Read incoming NMEA sentences.
3. Parse each sentence and identify its type.
4. Validate `GGA` fix quality and `RMC` status before accepting data.
5. Update the corresponding fields of the shared GNSS data dictionary.
6. Make the collected data available for inspection or future robotics integration.

**Important:** GGA and RMC updates can arrive at different times. Combining their latest values does **not** guarantee that every field belongs to exactly the same GNSS fix. Timestamp alignment and stale-data detection are useful next steps before using this information to make robot-navigation decisions.

## Planned Improvements

- [ ] Detect serial-port disconnections and automatically reconnect to the GNSS receiver.
- [ ] Add stale-data detection and timestamp synchronization.
- [ ] Improve parsing tests using representative NMEA samples.
- [ ] Expose GNSS measurements to robot software through a defined interface (for example, a ROS 2 node).
- [ ] Investigate integration with other sensors for more robust robot localization.

## Limitations

- GNSS accuracy depends on receiver quality, satellite visibility, and the surrounding environment.
- Measurements may be delayed, invalid, or unavailable indoors or near obstructions.
- Automatic USB reconnection is not yet implemented.
- This project acquires navigation-related data; it does not command a robot, perform path planning, or establish a safety-certified position estimate.

## Privacy and Logging

GNSS logs can contain sensitive location history. Do not commit real coordinate logs or private test data to a public repository. A suggested `.gitignore` includes:

```gitignore
.venv/
__pycache__/
*.pyc
*.log
.env
```

## Purpose

This repository documents the foundational GNSS data-acquisition stage of a broader robotics navigation workflow. It is intended as a practical learning and development project in Python, serial communication, NMEA parsing, and robotics sensing.