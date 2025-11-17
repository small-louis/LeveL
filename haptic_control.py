#!/usr/bin/env python3
"""
Haptic Motor Controller - Single Motor Test
Control one DRV2605 haptic motor via serial commands
"""

import serial
import serial.tools.list_ports
import time

class HapticController:
    def __init__(self):
        self.serial = None
        self.connected = False
        
    def connect(self):
        """Connect to ESP32"""
        ports = serial.tools.list_ports.comports()
        
        if len(ports) == 0:
            print("No serial ports found!")
            return False
        
        print("Available ports:")
        for i, port in enumerate(ports):
            print(f"{i}: {port}")
        
        try:
            port_num = int(input("Select port number: "))
            selected_port = ports[port_num].device
        except (ValueError, IndexError):
            print("Invalid selection!")
            return False
        
        print(f"Connecting to {selected_port}...")
        self.serial = serial.Serial(selected_port, 115200, timeout=0.5)
        time.sleep(2.5)  # Wait for ESP32 to reset
        
        # Read startup messages with timeout
        print("\n--- ESP32 Startup ---")
        start_time = time.time()
        while time.time() - start_time < 2:  # Try for 2 seconds max
            if self.serial.in_waiting:
                line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(line)
            else:
                time.sleep(0.1)
        print("--- End Startup ---\n")
        
        self.connected = True
        return True
    
    def send_command(self, command):
        """Send a command to the ESP32"""
        if not self.connected:
            print("Not connected!")
            return
        
        self.serial.write(f"{command}\n".encode('utf-8'))
        time.sleep(0.1)
        
        # Read response
        while self.serial.in_waiting:
            line = self.serial.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(line)
    
    def start_motor(self):
        """Start the heartbeat"""
        print("Starting motor...")
        self.send_command("START")
    
    def stop_motor(self):
        """Stop the heartbeat"""
        print("Stopping motor...")
        self.send_command("STOP")
    
    def set_bpm(self, bpm):
        """Set the BPM"""
        if 30 <= bpm <= 200:
            print(f"Setting BPM to {bpm}...")
            self.send_command(f"BPM:{bpm}")
        else:
            print("BPM must be between 30 and 200")
    
    def get_status(self):
        """Get current status"""
        self.send_command("STATUS")
    
    def close(self):
        """Close the serial connection"""
        if self.serial:
            self.serial.close()
            print("Connection closed")

def main():
    controller = HapticController()
    
    if not controller.connect():
        return
    
    print("\n=== Haptic Motor Control ===")
    print("Commands:")
    print("  start          - Start heartbeat")
    print("  stop           - Stop heartbeat")
    print("  bpm <value>    - Set BPM (30-200)")
    print("  status         - Show status")
    print("  exit           - Exit program")
    print()
    
    try:
        while True:
            user_input = input("haptic> ").strip().lower()
            
            if user_input == "exit":
                break
            elif user_input == "start":
                controller.start_motor()
            elif user_input == "stop":
                controller.stop_motor()
            elif user_input.startswith("bpm "):
                try:
                    bpm = int(user_input.split()[1])
                    controller.set_bpm(bpm)
                except (ValueError, IndexError):
                    print("Usage: bpm <value>")
            elif user_input == "status":
                controller.get_status()
            elif user_input == "":
                continue
            else:
                print(f"Unknown command: {user_input}")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        controller.close()

if __name__ == "__main__":
    main()

