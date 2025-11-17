import serial
import serial.tools.list_ports

# List ports
ports = list(serial.tools.list_ports.comports())
for i, p in enumerate(ports):
    print(f"{i}: {p}")

port_num = int(input("Port: "))
ser = serial.Serial(ports[port_num].device, 115200, timeout=1)

print("Connected! Type BPM values (30-200) or 'q' to quit\n")

while True:
    bpm = input("BPM: ")
    if bpm == 'q':
        break
    ser.write(f"{bpm}\n".encode())

ser.close()

