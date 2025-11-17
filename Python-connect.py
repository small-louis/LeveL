import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
SerialInst = serial.Serial()
portsList = []

print("Available ports:")
for i, one in enumerate(ports):
    portsList.append(str(one))
    print(f"{i}: {str(one)}")

if len(portsList) == 0:
    print("No serial ports found!")
    exit()

port_num = input("Select port number: ")

try:
    selected_port = ports[int(port_num)].device
    print(f"Using port: {selected_port}")
except (ValueError, IndexError):
    print("Invalid selection!")
    exit()

import time

SerialInst.baudrate = 115200  # Updated for ESP32
SerialInst.port = selected_port
SerialInst.timeout = 1  # Set read timeout

print("Opening serial port...")
SerialInst.open()

print("Waiting for ESP32 to reset and start up (3 seconds)...")
time.sleep(3)  # Give ESP32 time to reset and print startup messages

# Read and display ALL startup messages
print("\n--- ESP32 Output ---")
timeout_counter = 0
while timeout_counter < 10:  # Wait up to 1 second for messages
    if SerialInst.in_waiting:
        line = SerialInst.readline().decode('utf-8', errors='ignore').strip()
        if line:
            print(f"ESP32: {line}")
        timeout_counter = 0  # Reset counter if we got data
    else:
        time.sleep(0.1)
        timeout_counter += 1

print("--- End ESP32 Output ---\n")
print("Ready to send commands!")

while True:
    command = input("Arduino Command (ON/OFF/exit): ")
    SerialInst.write(command.encode('utf-8'))
    print(f"Sent: '{command}' ({len(command)} bytes)")
    
    # Wait a bit and read response
    time.sleep(0.1)
    while SerialInst.in_waiting:
        response = SerialInst.readline().decode('utf-8').strip()
        print(f"ESP32: {response}")

    if command == "exit":
        SerialInst.close()
        exit()



