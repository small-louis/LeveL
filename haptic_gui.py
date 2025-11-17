"""
6-Motor Haptic Control GUI with Waveform Control

PURPOSE:
    Advanced GUI for 6 independent haptic motors with per-motor waveform selection.
    Each motor can control lub/dub effects independently and enable/disable each beat.

HARDWARE:
    - ESP32 with mux_test.ino uploaded
    - TCA9548A I2C multiplexer
    - Up to 6 DRV2605 haptic drivers (channels 0-5)

USAGE:
    1. Upload mux_test.ino to ESP32
    2. Run: python haptic_gui.py
    3. For each motor, set:
       - BPM (30-200)
       - Lub effect number (1-123)
       - Dub effect number (1-123)
       - Enable/disable lub and dub individually
    4. Click SYNC to synchronize all motors

CONTROLS PER MOTOR:
    - On/Off toggle
    - BPM slider
    - Lub effect number (text entry)
    - Dub effect number (text entry)
    - Lub enable checkbox
    - Dub enable checkbox
"""

import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
import time

# Select port
ports = list(serial.tools.list_ports.comports())
print("Available ports:")
for i, p in enumerate(ports):
    print(f"{i}: {p}")

port_num = int(input("Select port number: "))
ser = serial.Serial(ports[port_num].device, 115200, timeout=0.01)
print("Waiting for ESP32...")
time.sleep(2)
print("Starting GUI...\n")

# Create GUI
root = tk.Tk()
root.title("6-Motor Haptic Control - Advanced")
root.geometry("900x700")

# Motor state variables
motor_vars = []
for i in range(6):
    motor_vars.append({
        'enabled': tk.BooleanVar(value=True),
        'bpm': tk.IntVar(value=60),
        'lub_effect': tk.StringVar(value='1'),  # Default: Strong Click 100%
        'dub_effect': tk.StringVar(value='3'),  # Default: Sharp Click 100%
        'lub_enabled': tk.BooleanVar(value=True),
        'dub_enabled': tk.BooleanVar(value=True)
    })

def update_motor(ch):
    """Send motor configuration to ESP32"""
    if not motor_vars[ch]['enabled'].get():
        # Motor off
        ser.write(f"{ch}:0:0:0:0:0\n".encode())
    else:
        bpm = motor_vars[ch]['bpm'].get()
        lub_effect = motor_vars[ch]['lub_effect'].get()
        dub_effect = motor_vars[ch]['dub_effect'].get()
        lub_en = 1 if motor_vars[ch]['lub_enabled'].get() else 0
        dub_en = 1 if motor_vars[ch]['dub_enabled'].get() else 0
        
        # Format: CH:BPM:LUB_EFFECT:DUB_EFFECT:LUB_EN:DUB_EN
        cmd = f"{ch}:{bpm}:{lub_effect}:{dub_effect}:{lub_en}:{dub_en}\n"
        ser.write(cmd.encode())
        print(f"Motor {ch}: BPM={bpm}, Lub={lub_effect}({lub_en}), Dub={dub_effect}({dub_en})")

def sync_motors():
    """Synchronize all motors"""
    ser.write(b"S\n")
    print("Motors synchronized!")

# Header
header = tk.Label(root, text="Haptic Motor Control Panel", 
                 font=("Arial", 16, "bold"), pady=10)
header.pack()

# Create controls for each motor
for ch in range(6):
    frame = tk.Frame(root, relief=tk.RAISED, borderwidth=2, padx=10, pady=8)
    frame.pack(fill=tk.X, padx=10, pady=5)
    
    # Row 1: Motor name and main enable
    row1 = tk.Frame(frame)
    row1.pack(fill=tk.X)
    
    tk.Label(row1, text=f"Motor {ch}", font=("Arial", 12, "bold"), width=8
            ).pack(side=tk.LEFT, padx=5)
    
    # On/Off checkbox
    def make_toggle(ch):
        def callback():
            update_motor(ch)
        return callback
    
    tk.Checkbutton(row1, text="Enable", variable=motor_vars[ch]['enabled'],
                  command=make_toggle(ch), font=("Arial", 10)
                  ).pack(side=tk.LEFT, padx=10)
    
    # Row 2: BPM control
    row2 = tk.Frame(frame)
    row2.pack(fill=tk.X, pady=5)
    
    tk.Label(row2, text="BPM:", font=("Arial", 10), width=8
            ).pack(side=tk.LEFT, padx=5)
    
    bpm_label = tk.Label(row2, text=str(motor_vars[ch]['bpm'].get()), 
                        font=("Arial", 10, "bold"), width=4)
    bpm_label.pack(side=tk.LEFT)
    
    def make_bpm_callback(ch, label):
        def callback(val):
            bpm = int(float(val))
            label.config(text=str(bpm))
            motor_vars[ch]['bpm'].set(bpm)
            update_motor(ch)
        return callback
    
    slider = tk.Scale(row2, from_=30, to=200, orient="horizontal",
                     length=300, command=make_bpm_callback(ch, bpm_label),
                     variable=motor_vars[ch]['bpm'], showvalue=False)
    slider.pack(side=tk.LEFT, padx=5)
    
    # Row 3: Lub controls
    row3 = tk.Frame(frame)
    row3.pack(fill=tk.X, pady=2)
    
    tk.Label(row3, text="Lub:", font=("Arial", 10), width=8
            ).pack(side=tk.LEFT, padx=5)
    
    def make_lub_enable(ch):
        def callback():
            update_motor(ch)
        return callback
    
    tk.Checkbutton(row3, text="Enable", variable=motor_vars[ch]['lub_enabled'],
                  command=make_lub_enable(ch), font=("Arial", 9)
                  ).pack(side=tk.LEFT)
    
    tk.Label(row3, text="Effect #:", font=("Arial", 9)
            ).pack(side=tk.LEFT, padx=5)
    
    def make_lub_effect_callback(ch):
        def callback(*args):
            update_motor(ch)
        return callback
    
    lub_entry = tk.Entry(row3, textvariable=motor_vars[ch]['lub_effect'], 
                        width=5, font=("Arial", 10))
    lub_entry.pack(side=tk.LEFT, padx=2)
    motor_vars[ch]['lub_effect'].trace('w', make_lub_effect_callback(ch))
    
    tk.Label(row3, text="(1-123)", font=("Arial", 8), fg="gray"
            ).pack(side=tk.LEFT, padx=2)
    
    # Row 4: Dub controls
    row4 = tk.Frame(frame)
    row4.pack(fill=tk.X, pady=2)
    
    tk.Label(row4, text="Dub:", font=("Arial", 10), width=8
            ).pack(side=tk.LEFT, padx=5)
    
    def make_dub_enable(ch):
        def callback():
            update_motor(ch)
        return callback
    
    tk.Checkbutton(row4, text="Enable", variable=motor_vars[ch]['dub_enabled'],
                  command=make_dub_enable(ch), font=("Arial", 9)
                  ).pack(side=tk.LEFT)
    
    tk.Label(row4, text="Effect #:", font=("Arial", 9)
            ).pack(side=tk.LEFT, padx=5)
    
    def make_dub_effect_callback(ch):
        def callback(*args):
            update_motor(ch)
        return callback
    
    dub_entry = tk.Entry(row4, textvariable=motor_vars[ch]['dub_effect'],
                        width=5, font=("Arial", 10))
    dub_entry.pack(side=tk.LEFT, padx=2)
    motor_vars[ch]['dub_effect'].trace('w', make_dub_effect_callback(ch))
    
    tk.Label(row4, text="(1-123)", font=("Arial", 8), fg="gray"
            ).pack(side=tk.LEFT, padx=2)

# Sync button at bottom
sync_frame = tk.Frame(root, pady=15)
sync_frame.pack()

sync_btn = tk.Button(sync_frame, text="SYNC ALL MOTORS", command=sync_motors,
                    font=("Arial", 14, "bold"), bg="orange", fg="white",
                    width=20, height=2)
sync_btn.pack()

# Send initial values after a short delay
root.after(100, lambda: [update_motor(i) for i in range(6)])

def on_closing():
    ser.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
