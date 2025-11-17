// DRV2605 Haptic Driver - Serial Controlled Heartbeat
// Control BPM and start/stop via serial commands from Python

#include <Wire.h>
#include "Adafruit_DRV2605.h"

// Create an instance of the haptic driver
Adafruit_DRV2605 drv;

// State variables
int currentBPM = 72;  // Default BPM
bool motorRunning = false;  // Motor on/off state
unsigned long lastBeatTime = 0;  // Timing for heartbeat
bool inLubDubCycle = false;  // Track if we're between lub and dub
unsigned long lubTime = 0;  // Time when lub was triggered

const int delayBetweenLubDub = 150;  // Time between lub and dub clicks

void setup() {
  Serial.begin(115200);
  Serial.println("\n=== DRV2605 Serial Control - Heartbeat ===");
  
  // Initialize the driver
  if (!drv.begin()) {
    Serial.println("ERROR: Could not find DRV2605 driver. Check wiring!");
    while (1);
  }
  Serial.println("DRV2605 Driver Found!");
  
  // Select the vibration motor library
  drv.selectLibrary(1);  // Library 1: ERM motors
  
  // Set the mode to Internal Trigger
  drv.setMode(DRV2605_MODE_INTTRIG);
  
  Serial.println("\nCommands:");
  Serial.println("  START - Start heartbeat");
  Serial.println("  STOP - Stop heartbeat");
  Serial.println("  BPM:XX - Set BPM (e.g., BPM:80)");
  Serial.println("  STATUS - Show current status");
  Serial.println();
  printStatus();
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    command.toUpperCase();
    
    handleCommand(command);
  }
  
  // Handle heartbeat timing if motor is running
  if (motorRunning) {
    unsigned long currentTime = millis();
    int beatInterval = 60000 / currentBPM;  // Convert BPM to milliseconds
    
    if (!inLubDubCycle) {
      // Time for a new heartbeat cycle
      if (currentTime - lastBeatTime >= beatInterval) {
        // First beat (LUB)
        drv.setWaveform(0, 12);  // Sharp Click 100%
        drv.setWaveform(1, 0);
        drv.go();
        
        lubTime = currentTime;
        inLubDubCycle = true;
      }
    } else {
      // Wait for lub-dub delay, then do second beat
      if (currentTime - lubTime >= delayBetweenLubDub) {
        // Second beat (DUB)
        drv.setWaveform(0, 14);  // Sharp Click 30%
        drv.setWaveform(1, 0);
        drv.go();
        
        lastBeatTime = currentTime;
        inLubDubCycle = false;
      }
    }
  }
}

void handleCommand(String cmd) {
  if (cmd == "START") {
    motorRunning = true;
    lastBeatTime = millis();
    inLubDubCycle = false;
    Serial.println("Motor STARTED");
    printStatus();
    
  } else if (cmd == "STOP") {
    motorRunning = false;
    Serial.println("Motor STOPPED");
    printStatus();
    
  } else if (cmd.startsWith("BPM:")) {
    int newBPM = cmd.substring(4).toInt();
    if (newBPM >= 30 && newBPM <= 200) {
      currentBPM = newBPM;
      Serial.print("BPM set to: ");
      Serial.println(currentBPM);
      printStatus();
    } else {
      Serial.println("ERROR: BPM must be between 30 and 200");
    }
    
  } else if (cmd == "STATUS") {
    printStatus();
    
  } else if (cmd.length() > 0) {
    Serial.print("Unknown command: ");
    Serial.println(cmd);
  }
}

void printStatus() {
  Serial.println("--- STATUS ---");
  Serial.print("Motor: ");
  Serial.println(motorRunning ? "RUNNING" : "STOPPED");
  Serial.print("BPM: ");
  Serial.println(currentBPM);
  Serial.print("Beat interval: ");
  Serial.print(60000 / currentBPM);
  Serial.println(" ms");
  Serial.println("--------------");
}

