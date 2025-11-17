"""
Integrated GSR Monitor + 6-Motor Haptic Control System

PURPOSE:
    Combined interface for GSR monitoring with live plotting and recording,
    plus advanced haptic motor control with waveform selection.

HARDWARE:
    - ESP32 with integrated_code.ino uploaded
    - GSR sensor on GPIO34
    - TCA9548A I2C multiplexer
    - 6x DRV2605 haptic drivers (channels 0-5)

USAGE:
    1. Upload integrated_code.ino to ESP32
    2. Run: python integrated_code.py
    3. Left side: GSR plot with recording
    4. Right side: 6-motor haptic controls

FEATURES:
    - Real-time GSR plotting
    - Record GSR data to CSV (GSR-data folder)
    - Individual motor BPM, lub/dub effect control
    - Enable/disable lub and dub per motor
    - Sync button for all motors
"""

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
print("Available ports:")
for i, p in enumerate(ports):
    print(f"{i}: {p}")

port_num = int(input("Select port number: "))
ser = serial.Serial(ports[port_num].device, 115200, timeout=0.01)
print("Connected! Waiting for ESP32...")
time.sleep(2)
print("Starting integrated system...\n")

# Create GSR-data folder
if not os.path.exists('GSR-data'):
    os.makedirs('GSR-data')

# ===== GSR DATA =====
gsr_times = deque(maxlen=500)
gsr_values = deque(maxlen=500)
gsr_count = 0

# Recording state
recording = False
recorded_data = []
start_time = None

def update_motor(ch):
    """Send motor configuration to ESP32"""
    if not motor_vars[ch]['enabled'].get():
        cmd = f"{ch}:0:0:0:0:0\n"
        ser.write(cmd.encode())
        print(f"Sent: {cmd.strip()}")
    else:
        bpm = motor_vars[ch]['bpm'].get()
        lub_effect = motor_vars[ch]['lub_effect'].get()
        dub_effect = motor_vars[ch]['dub_effect'].get()
        lub_en = 1 if motor_vars[ch]['lub_enabled'].get() else 0
        dub_en = 1 if motor_vars[ch]['dub_enabled'].get() else 0
        
        cmd = f"{ch}:{bpm}:{lub_effect}:{dub_effect}:{lub_en}:{dub_en}\n"
        ser.write(cmd.encode())
        ser.flush()  # Ensure it's sent immediately
        print(f"Sent: {cmd.strip()}")

def sync_motors():
    """Synchronize all motors"""
    ser.write(b"S\n")
    print("Motors synchronized!")

def toggle_recording():
    """Start/stop GSR recording"""
    global recording, recorded_data, start_time, gsr_count
    
    if not recording:
        recording = True
        recorded_data = []
        gsr_count = 0
        gsr_times.clear()
        gsr_values.clear()
        start_time = time.time()
        
        record_btn.config(text="STOP & SAVE", bg="red")
        status_label.config(text="Recording...", fg="red")
        print("\n=== GSR RECORDING STARTED ===")
    else:
        recording = False
        record_btn.config(text="START RECORDING", bg="green")
        
        if len(recorded_data) > 0:
            save_gsr_data()
            status_label.config(text=f"Saved {len(recorded_data)} samples", fg="green")
        else:
            status_label.config(text="No data", fg="orange")
        
        print("=== RECORDING STOPPED ===\n")

def save_gsr_data():
    """Save GSR data to CSV"""
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

def update_plot(frame):
    """Update GSR plot and read serial data"""
    global gsr_count, start_time
    
    # Read all available serial data
    while ser.in_waiting:
        try:
            line = ser.readline().decode('utf-8').strip()
            
            if line.startswith('G:'):
                # GSR data
                val = int(line[2:])
                gsr_count += 1
                current_time = gsr_count * 0.1
                gsr_times.append(current_time)
                gsr_values.append(val)
                
                if recording and start_time is not None:
                    recording_time = time.time() - start_time
                    recorded_data.append([recording_time, val])
                    
        except Exception as e:
            pass
    
    # Update GSR plot
    ax.clear()
    if len(gsr_values) > 0:
        ax.plot(list(gsr_times), list(gsr_values), 'b-', linewidth=2)
        
        ax.text(0.02, 0.98, f'Current: {gsr_values[-1]}',
                transform=ax.transAxes, fontsize=12,
                verticalalignment='top', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        if recording:
            ax.text(0.98, 0.98, 'RECORDING ●',
                    transform=ax.transAxes, fontsize=12,
                    verticalalignment='top', horizontalalignment='right',
                    fontweight='bold', color='red',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax.set_ylim(0, 4096)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('GSR Value')
    ax.set_title('GSR Monitor')
    ax.grid(True, alpha=0.3)
    
    # Set fixed window - show last 50 seconds
    if len(gsr_times) > 0:
        current_time = gsr_times[-1]
        if current_time > 50:
            ax.set_xlim(current_time - 50, current_time)
        else:
            ax.set_xlim(0, 50)

# ===== CREATE GUI =====
root = tk.Tk()
root.title("Integrated GSR + Haptic Control")
root.geometry("1400x900")

# ===== MOTOR DATA (after root window created) =====
motor_vars = []
for i in range(6):
    motor_vars.append({
        'enabled': tk.BooleanVar(value=True),
        'bpm': tk.IntVar(value=60),
        'lub_effect': tk.StringVar(value='1'),
        'dub_effect': tk.StringVar(value='3'),
        'lub_enabled': tk.BooleanVar(value=True),
        'dub_enabled': tk.BooleanVar(value=True)
    })

# Main container with two columns
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# ===== LEFT SIDE: GSR PLOT =====
left_frame = tk.Frame(main_frame, width=700)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

# GSR controls
gsr_control = tk.Frame(left_frame, bg='lightgray', pady=10)
gsr_control.pack(side=tk.TOP, fill=tk.X)

tk.Label(gsr_control, text="GSR MONITOR", font=("Arial", 14, "bold"),
         bg='lightgray').pack(side=tk.TOP, pady=5)

record_btn = tk.Button(gsr_control, text="START RECORDING",
                       command=toggle_recording,
                       font=("Arial", 12, "bold"),
                       bg='green', fg='white', width=18, height=2)
record_btn.pack(side=tk.LEFT, padx=10)

status_label = tk.Label(gsr_control, text="Not Recording",
                       font=("Arial", 11), bg='lightgray')
status_label.pack(side=tk.LEFT, padx=10)

# GSR plot
fig, ax = plt.subplots(figsize=(7, 7))
fig.tight_layout(pad=3.0)

canvas = FigureCanvasTkAgg(fig, master=left_frame)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# ===== RIGHT SIDE: HAPTIC CONTROLS =====
right_frame = tk.Frame(main_frame, width=650)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

# Header
tk.Label(right_frame, text="HAPTIC CONTROL", font=("Arial", 14, "bold"),
         pady=10).pack()

# Scrollable frame for motors
canvas_scroll = tk.Canvas(right_frame, width=630, height=650)
scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=canvas_scroll.yview)
scrollable_frame = tk.Frame(canvas_scroll)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
)

canvas_scroll.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas_scroll.configure(yscrollcommand=scrollbar.set)

canvas_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create motor controls
for ch in range(6):
    frame = tk.Frame(scrollable_frame, relief=tk.RAISED, borderwidth=2, padx=10, pady=8)
    frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Row 1: Motor name and enable
    row1 = tk.Frame(frame)
    row1.pack(fill=tk.X)
    
    tk.Label(row1, text=f"Motor {ch}", font=("Arial", 11, "bold"), width=8
            ).pack(side=tk.LEFT, padx=5)
    
    def make_toggle(ch):
        def callback():
            update_motor(ch)
        return callback
    
    tk.Checkbutton(row1, text="Enable", variable=motor_vars[ch]['enabled'],
                  command=make_toggle(ch), font=("Arial", 9)
                  ).pack(side=tk.LEFT, padx=10)
    
    # Row 2: BPM
    row2 = tk.Frame(frame)
    row2.pack(fill=tk.X, pady=5)
    
    tk.Label(row2, text="BPM:", font=("Arial", 9), width=8
            ).pack(side=tk.LEFT, padx=5)
    
    bpm_label = tk.Label(row2, text=str(motor_vars[ch]['bpm'].get()),
                        font=("Arial", 9, "bold"), width=4)
    bpm_label.pack(side=tk.LEFT)
    
    def make_bpm_callback(ch, label):
        def callback(val):
            bpm = int(float(val))
            label.config(text=str(bpm))
            motor_vars[ch]['bpm'].set(bpm)
            update_motor(ch)
        return callback
    
    slider = tk.Scale(row2, from_=30, to=200, orient="horizontal",
                     length=250, command=make_bpm_callback(ch, bpm_label),
                     variable=motor_vars[ch]['bpm'], showvalue=False)
    slider.pack(side=tk.LEFT, padx=5)
    
    # Row 3: Lub
    row3 = tk.Frame(frame)
    row3.pack(fill=tk.X, pady=2)
    
    tk.Label(row3, text="Lub:", font=("Arial", 9), width=8
            ).pack(side=tk.LEFT, padx=5)
    
    def make_lub_enable(ch):
        def callback():
            update_motor(ch)
        return callback
    
    tk.Checkbutton(row3, text="En", variable=motor_vars[ch]['lub_enabled'],
                  command=make_lub_enable(ch), font=("Arial", 8)
                  ).pack(side=tk.LEFT)
    
    tk.Label(row3, text="Effect:", font=("Arial", 8)
            ).pack(side=tk.LEFT, padx=3)
    
    def make_lub_effect_callback(ch):
        def callback(*args):
            update_motor(ch)
        return callback
    
    lub_entry = tk.Entry(row3, textvariable=motor_vars[ch]['lub_effect'],
                        width=4, font=("Arial", 9))
    lub_entry.pack(side=tk.LEFT, padx=2)
    motor_vars[ch]['lub_effect'].trace('w', make_lub_effect_callback(ch))
    
    # Row 4: Dub
    row4 = tk.Frame(frame)
    row4.pack(fill=tk.X, pady=2)
    
    tk.Label(row4, text="Dub:", font=("Arial", 9), width=8
            ).pack(side=tk.LEFT, padx=5)
    
    def make_dub_enable(ch):
        def callback():
            update_motor(ch)
        return callback
    
    tk.Checkbutton(row4, text="En", variable=motor_vars[ch]['dub_enabled'],
                  command=make_dub_enable(ch), font=("Arial", 8)
                  ).pack(side=tk.LEFT)
    
    tk.Label(row4, text="Effect:", font=("Arial", 8)
            ).pack(side=tk.LEFT, padx=3)
    
    def make_dub_effect_callback(ch):
        def callback(*args):
            update_motor(ch)
        return callback
    
    dub_entry = tk.Entry(row4, textvariable=motor_vars[ch]['dub_effect'],
                        width=4, font=("Arial", 9))
    dub_entry.pack(side=tk.LEFT, padx=2)
    motor_vars[ch]['dub_effect'].trace('w', make_dub_effect_callback(ch))

# Sync button
sync_frame = tk.Frame(right_frame, pady=10)
sync_frame.pack(side=tk.BOTTOM)

sync_btn = tk.Button(sync_frame, text="SYNC ALL", command=sync_motors,
                    font=("Arial", 12, "bold"), bg="orange", fg="white",
                    width=15, height=2)
sync_btn.pack()

# Animation
ani = FuncAnimation(fig, update_plot, interval=100, cache_frame_data=False)

# Send initial motor values
root.after(100, lambda: [update_motor(i) for i in range(6)])

def on_closing():
    global recording
    if recording:
        print("\nClosing while recording. Saving...")
        save_gsr_data()
    ser.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

print("Integrated system ready!")
print("Left: GSR monitor | Right: Haptic controls\n")
root.mainloop()
