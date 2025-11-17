"""
Single Motor Haptic Control with GUI

PURPOSE:
    Simple GUI for controlling one DRV2605 haptic motor.
    Includes live BPM slider and serial monitor display.

HARDWARE:
    - ESP32 with DRV2605_serial-ClickBPM.ino uploaded
    - One DRV2605 haptic driver on I2C
    - Vibration motor connected to DRV2605

USAGE:
    1. Upload DRV2605_serial-ClickBPM.ino to ESP32
    2. Wire DRV2605 to ESP32 I2C (GPIO21/22)
    3. Run: python simple_haptic.py
    4. Use slider to adjust BPM

CREATED: Initial single-motor test before multiplexer integration
"""

import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import scrolledtext
import time

# Select port
ports = list(serial.tools.list_ports.comports())
for i, p in enumerate(ports):
    print(f"{i}: {p}")
port_num = int(input("Port: "))
ser = serial.Serial(ports[port_num].device, 115200, timeout=0.01)
time.sleep(2)  # Wait for ESP32 to boot

# Create GUI
root = tk.Tk()
root.title("Haptic Motor Control")

tk.Label(root, text="BPM", font=("Arial", 14)).pack(pady=10)
bpm_label = tk.Label(root, text="72", font=("Arial", 24, "bold"))
bpm_label.pack()

last_update = 0
def update_bpm(val):
    global last_update
    now = time.time()
    if now - last_update < 0.1:  # Limit updates to every 100ms
        return
    last_update = now
    
    bpm = int(float(val))
    bpm_label.config(text=str(bpm))
    ser.write(f"{bpm}\n".encode())
    ser.flush()

slider = tk.Scale(root, from_=30, to=200, orient="horizontal", length=400, 
                  command=update_bpm, showvalue=False)
slider.set(72)
slider.pack(pady=20)

# Serial monitor
tk.Label(root, text="Serial Monitor", font=("Arial", 10)).pack()
monitor = scrolledtext.ScrolledText(root, width=50, height=10, font=("Courier", 9))
monitor.pack(pady=10)

def read_serial():
    if ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            monitor.insert(tk.END, line + "\n")
            monitor.see(tk.END)
    root.after(100, read_serial)

read_serial()

root.mainloop()
ser.close()

