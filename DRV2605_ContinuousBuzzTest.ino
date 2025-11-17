// Include the required libraries
#include <Wire.h>
#include "Adafruit_DRV2605.h"

// Create an instance of the haptic driver
Adafruit_DRV2605 drv;

void setup() {
  // Start Serial Monitor at 115200 baud
  Serial.begin(115200);
  Serial.println("DRV2605 Haptic Driver - Continuous Buzz Test");

  // Initialize the driver
  if (!drv.begin()) {
    Serial.println("Could not find DRV2605 driver. Check wiring.");
    while (1); // Halt if the driver is not found
  }
  Serial.println("DRV2605 Driver Found!");

  // Select the vibration motor library
  drv.selectLibrary(1);
  
  // Set the mode to Real-Time Playback (RTP)
  // This allows us to control the motor directly
  drv.setMode(DRV2605_MODE_REALTIME);
}

void loop() {
  // --- MOTOR ON ---
  Serial.println("Motor ON - Buzzing for 5 seconds");

  // Set the motor intensity (0-127). 127 is full strength.
  drv.setRealtimeValue(127);

  // Wait for 5 seconds
  delay(5000);

  // --- MOTOR OFF ---
  Serial.println("Motor OFF - Pausing for 5 seconds");
  
  // Set the motor intensity to 0 to stop it
  drv.setRealtimeValue(0);

  // Wait for 5 seconds
  delay(5000);
}

