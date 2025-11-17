"""
Multiplexer Test Script - Command Line Version

PURPOSE:
    Simple command-line test for 6-motor multiplexer setup.
    Sends hardcoded BPM values to ESP32 which handles all timing.

HARDWARE:
    - ESP32 with mux_test.ino uploaded
    - TCA9548A I2C multiplexer
    - Up to 6 DRV2605 haptic drivers
    
USAGE:
    1. Upload mux_test.ino to ESP32
    2. Run: python mux_test.py
    3. Select serial port
    4. Motors run automatically at predefined BPMs

NOTE:
    This is a basic test script. Use haptic_gui.py for full control interface.
    BPM values are set in line 7 of this file.

CREATED: Initial testing before GUI development
"""

import serial
import serial.tools.list_ports
import time
import threading

# BPM settings for 6 channels
BPM = [40, 40, 40, 40, 40, 40]  # Ch0-Ch5

# Select port
ports = list(serial.tools.list_ports.comports())
for i, p in enumerate(ports):
    print(f"{i}: {p}")

ser = serial.Serial(ports[int(input("Port: "))].device, 115200, timeout=0.01)
print("Waiting for ESP32...")
time.sleep(3)

# Read startup
print("Reading startup messages...")
found_ready = False
for _ in range(50):
    if ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            print(line)
            if "Ready" in line:
                found_ready = True
                break
    time.sleep(0.1)
    
if not found_ready:
    print("Warning: Did not receive 'Ready' from ESP32")

print("\nBPM Settings:")
for i, bpm in enumerate(BPM):
    print(f"  Ch{i}: {bpm} BPM")
print("Running...\n")

# Thread to read serial output
def read_serial():
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"ESP32: {line}")
        time.sleep(0.05)

reader = threading.Thread(target=read_serial, daemon=True)
reader.start()

# Send initial BPM values
print("Sending BPM settings to ESP32...")
for ch in range(6):
    ser.write(f"{ch}:{BPM[ch]}\n".encode())
    time.sleep(0.1)

print("Motors running!\n")

try:
    while True:
        time.sleep(1)  # Arduino handles all timing
except KeyboardInterrupt:
    print("\nStopped")
    ser.close()

