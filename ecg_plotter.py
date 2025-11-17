"""
Simple Heart Rate Monitor
Plots heart rate values received from Arduino/ESP32
"""

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import serial
import serial.tools.list_ports
from collections import deque
import time

# Select port
ports = list(serial.tools.list_ports.comports())
for i, p in enumerate(ports):
    print(f"{i}: {p}")
ser = serial.Serial(ports[int(input("Port: "))].device, 115200, timeout=0.1)
print("Connected! Waiting for ESP32...")
time.sleep(2)

# Data storage
times = deque(maxlen=100)
heart_rates = deque(maxlen=100)
sample_count = 0

print("Starting plot...")

# Create figure and axis
fig, ax = plt.subplots(figsize=(10, 6))

def update(frame):
    global sample_count
    
    # Read serial data
    if ser.in_waiting:
        try:
            line = ser.readline().decode('utf-8').strip()
            value = int(line)
            
            sample_count += 1
            times.append(sample_count / 5.0)  # Assuming 5Hz updates
            heart_rates.append(value)
            print(f"HR: {value} BPM")  # Debug output
        except:
            pass
    
    # Update plot
    ax.clear()
    if len(heart_rates) > 0:
        ax.plot(list(times), list(heart_rates), 'r-', linewidth=2, marker='o', markersize=4)
        ax.text(0.02, 0.98, f'HR: {heart_rates[-1]} BPM', 
                transform=ax.transAxes, fontsize=16, 
                verticalalignment='top', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    ax.set_ylim(40, 180)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Heart Rate (BPM)')
    ax.set_title('Live Heart Rate')
    ax.grid(True, alpha=0.3)

ani = FuncAnimation(fig, update, interval=100, cache_frame_data=False)

try:
    plt.show()
except KeyboardInterrupt:
    pass

ser.close()
print("\nClosed.")
