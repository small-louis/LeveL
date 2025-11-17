"""
Serial Communication Test

PURPOSE:
    Quick diagnostic tool to verify serial communication with ESP32.
    Reads 20 samples and prints them to verify data is being sent.

USAGE:
    1. Upload any Arduino sketch that sends serial data
    2. Run: python test_serial.py
    3. Select serial port
    4. Check if data is being received

CREATED: For debugging serial communication issues
"""

import serial
import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
for i, p in enumerate(ports):
    print(f"{i}: {p}")

port_num = int(input("Port: "))
ser = serial.Serial(ports[port_num].device, 115200, timeout=1)

print("Reading 20 samples...")
for i in range(20):
    if ser.in_waiting:
        line = ser.readline().decode('utf-8').strip()
        print(f"Sample {i}: {line}")

ser.close()

