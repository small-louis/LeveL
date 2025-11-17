// Include the required libraries
#include <Wire.h>
#include "Adafruit_DRV2605.h"

// Create an instance of the haptic driver
Adafruit_DRV2605 drv;

// ===== CONFIGURABLE BPM =====
int BPM = 72;  // Current BPM (can be changed via serial)
const int delayBetweenLubDub = 150;  // Time between lub and dub

void setup() {
  // Start Serial Monitor at 115200 baud
  Serial.begin(115200);
  Serial.println("DRV2605 Haptic Driver - Heartbeat Pattern");
  
  Serial.print("Starting BPM: ");
  Serial.println(BPM);
  Serial.println("Send BPM value via serial (e.g. '80')");

  // Initialize the driver
  if (!drv.begin()) {
    Serial.println("Could not find DRV2605 driver. Check wiring.");
    while (1); // Halt if the driver is not found
  }
  Serial.println("DRV2605 Driver Found!");

  // Select the vibration motor library
  // Library 1: ERM (Eccentric Rotating Mass) motors
  drv.selectLibrary(1);
  
  // Set the mode to Internal Trigger
  // This mode plays waveforms from the library
  drv.setMode(DRV2605_MODE_INTTRIG);
}

void loop() {
  // Check for serial input to change BPM
  if (Serial.available() > 0) {
    int newBPM = Serial.parseInt();
    if (newBPM >= 30 && newBPM <= 200) {
      BPM = newBPM;
      Serial.print("BPM changed to: ");
      Serial.println(BPM);
    }
  }
  
  // === FIRST BEAT (LUB) ===
  drv.setWaveform(0, 12);
  drv.setWaveform(1, 0);
  drv.go();
  
  delay(delayBetweenLubDub);
  
  // === SECOND BEAT (DUB) ===
  drv.setWaveform(0, 14);
  drv.setWaveform(1, 0);
  drv.go();
  
  // Wait for next heartbeat
  int delayBetweenBeats = 60000 / BPM;
  delay(delayBetweenBeats - delayBetweenLubDub);
}

