"""Simple GSR Plotter with Recording - Plots raw sensor values and saves to CSV"""

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
from collections import deque
import time
import csv
from datetime import datetime
import os

# Select port
ports = list(serial.tools.list_ports.comports())
for i, p in enumerate(ports):
    print(f"{i}: {p}")
ser = serial.Serial(ports[int(input("Port: "))].device, 115200, timeout=0.1)
print("Connected! Starting in 2 seconds...")
time.sleep(2)
print("Reading data...\n")

# Create GSR-data folder if it doesn't exist
if not os.path.exists('GSR-data'):
    os.makedirs('GSR-data')
    print("Created GSR-data folder")

# Data storage
times = deque(maxlen=500)
values = deque(maxlen=500)
count = 0

# Recording state
recording = False
recorded_data = []
start_time = None

def update(frame):
    global count, start_time
    # Read ALL available data
    while ser.in_waiting:
        try:
            line = ser.readline().decode('utf-8').strip()
            val = int(line)
            count += 1
            current_time = count * 0.1  # 10Hz sampling
            times.append(current_time)
            values.append(val)
            
            # If recording, save to buffer
            if recording and start_time is not None:
                recording_time = time.time() - start_time
                recorded_data.append([recording_time, val])
            
            # Only print occasionally to avoid terminal spam
            if count % 10 == 0:
                print(f"GSR: {val}")
        except Exception as e:
            pass
    
    ax.clear()
    if len(values) > 0:
        ax.plot(list(times), list(values), 'b-', linewidth=2)
        
        # Show current value
        ax.text(0.02, 0.98, f'Current: {values[-1]}', 
                transform=ax.transAxes, fontsize=14, 
                verticalalignment='top', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # Show recording indicator
        if recording:
            ax.text(0.98, 0.98, 'RECORDING ●', 
                    transform=ax.transAxes, fontsize=14, 
                    verticalalignment='top', horizontalalignment='right',
                    fontweight='bold', color='red',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax.set_ylim(0, 4096)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('GSR Value')
    ax.set_title('GSR Monitor')
    ax.grid(True, alpha=0.3)

def toggle_recording():
    """Start/stop recording"""
    global recording, recorded_data, start_time, count
    
    if not recording:
        # Start recording
        recording = True
        recorded_data = []
        count = 0
        times.clear()
        values.clear()
        start_time = time.time()
        
        record_btn.config(text="STOP & SAVE", bg="red")
        status_label.config(text="Status: RECORDING", fg="red")
        print("\n=== RECORDING STARTED ===")
    else:
        # Stop and save
        recording = False
        record_btn.config(text="START RECORDING", bg="green")
        
        if len(recorded_data) > 0:
            save_data()
            status_label.config(text=f"Saved {len(recorded_data)} samples", fg="green")
        else:
            status_label.config(text="No data to save", fg="orange")
        
        print("=== RECORDING STOPPED ===\n")

def save_data():
    """Save to CSV in GSR-data folder"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"GSR-data/gsr_{timestamp}.csv"
    filepath = os.path.abspath(filename)
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Time (s)', 'GSR Value'])
        writer.writerows(recorded_data)
    
    print(f"\n✓ Saved to: {filepath}")
    print(f"  Samples: {len(recorded_data)}")
    print(f"  Duration: {recorded_data[-1][0]:.1f}s\n")

# Create GUI
root = tk.Tk()
root.title("GSR Monitor")
root.geometry("1000x700")

# Control panel
control_frame = tk.Frame(root, bg='lightgray', pady=10)
control_frame.pack(side=tk.TOP, fill=tk.X)

record_btn = tk.Button(control_frame, text="START RECORDING", 
                       command=toggle_recording,
                       font=('Arial', 14, 'bold'),
                       bg='green', fg='white', width=20, height=2)
record_btn.pack(side=tk.LEFT, padx=20)

status_label = tk.Label(control_frame, text="Status: Not Recording",
                       font=('Arial', 12), bg='lightgray')
status_label.pack(side=tk.LEFT, padx=20)

# Matplotlib figure
fig, ax = plt.subplots(figsize=(10, 5))
fig.tight_layout(pad=3.0)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

ani = FuncAnimation(fig, update, interval=100, cache_frame_data=False)

def on_closing():
    """Cleanup on exit"""
    global recording
    if recording:
        print("\nWindow closed while recording. Saving...")
        save_data()
    ser.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

print("GSR monitor ready!")
print("Click START RECORDING to begin\n")
root.mainloop()
