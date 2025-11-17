/*
 * GSR Sensor Calibration Tool
 * 
 * SETUP:
 * 1. Connect GSR sensor to ESP32:
 *    - Black (GND) -> GND
 *    - Red (5V)    -> VIN
 *    - White (NC)  -> Not connected
 *    - Yellow (A0) -> GPIO34
 * 
 * CALIBRATION STEPS:
 * 1. Upload this code to ESP32
 * 2. DO NOT wear the sensor yet!
 * 3. Open Serial Monitor (115200 baud) or Serial Plotter
 * 4. Use small screwdriver to turn potentiometer on GSR board
 * 5. Adjust until readings are LOWEST and STABLE
 * 6. Note the "CALIBRATION VALUE" shown
 * 7. Write it down - you'll need it for gsr_monitor.ino
 */

const int GSR_PIN = 34;  // ESP32 analog pin
const int NUM_SAMPLES = 10;

void setup() {
  Serial.begin(115200);
  pinMode(GSR_PIN, INPUT);
  
  Serial.println("\n=== GSR SENSOR CALIBRATION ===");
  Serial.println("DO NOT wear the sensor yet!");
  Serial.println("Use screwdriver to adjust potentiometer");
  Serial.println("Goal: Get LOWEST stable reading\n");
  
  delay(2000);
}

void loop() {
  // Average 10 readings to smooth noise
  long sum = 0;
  for (int i = 0; i < NUM_SAMPLES; i++) {
    sum += analogRead(GSR_PIN);
    delay(5);
  }
  int gsr_average = sum / NUM_SAMPLES;
  
  // Display current reading
  Serial.print("Current: ");
  Serial.print(gsr_average);
  Serial.print("  |  ");
  
  // Visual bar graph
  Serial.print("[");
  for (int i = 0; i < gsr_average / 20; i++) {
    Serial.print("=");
  }
  Serial.println("]");
  
  // Guidance message (ESP32 has 12-bit ADC: 0-4095)
  if (gsr_average < 1000) {
    Serial.println("    -> Too low! Turn potentiometer the other way");
  } else if (gsr_average > 3500) {
    Serial.println("    -> Too high! Keep adjusting down");
  } else if (gsr_average >= 1000 && gsr_average <= 3500) {
    Serial.print("    -> GOOD! If stable, your CALIBRATION VALUE = ");
    Serial.println(gsr_average);
  }
  
  Serial.println();
  delay(500);  // Update twice per second
}

