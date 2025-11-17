// Include the required libraries
#include <Wire.h>
#include "Adafruit_DRV2605.h"

// Create an instance of the haptic driver
Adafruit_DRV2605 drv;

// ===== CONFIGURABLE BPM =====
// Set your desired beats per minute here
const int BPM = 72;  // Change this value to adjust heartbeat frequency (typical resting: 60-100)

// Calculate delay between heartbeats in milliseconds
const int delayBetweenBeats = 60000 / BPM;

// Timing for the heartbeat pattern (lub-dub)
const int delayBetweenLubDub = 150;  // Time between the two clicks in a heartbeat

void setup() {
  // Start Serial Monitor at 115200 baud
  Serial.begin(115200);
  Serial.println("DRV2605 Haptic Driver - Heartbeat Pattern");
  
  // Display the configured BPM
  Serial.print("Heart rate (BPM): ");
  Serial.println(BPM);
  Serial.print("Delay between heartbeats: ");
  Serial.print(delayBetweenBeats);
  Serial.println(" ms");

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
  // === FIRST BEAT (LUB) ===
  // Use Sharp Click for more distinct, shorter effect
  drv.setWaveform(0, 12);  // Sharp Click 100% - short and crisp
  drv.setWaveform(1, 0);   // End of waveform sequence
  drv.go();
  
  // Short pause between lub and dub
  delay(delayBetweenLubDub);
  
  // === SECOND BEAT (DUB) ===
  // Softer, shorter click
  drv.setWaveform(0, 14);  // Sharp Click 30% - much softer and shorter
  drv.setWaveform(1, 0);   // End of waveform sequence
  drv.go();
  
  // Wait for the next heartbeat cycle
  // Subtract the lub-dub delay to maintain accurate BPM
  delay(delayBetweenBeats - delayBetweenLubDub);
}

