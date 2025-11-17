import serial
import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
for i, p in enumerate(ports):
    print(f"{i}: {p}")

ser = serial.Serial(ports[int(input("Port: "))].device, 115200)

while True:
    ser.write(f"{input('BPM: ')}\n".encode())

