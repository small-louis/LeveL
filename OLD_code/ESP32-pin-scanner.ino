// ESP32 Pin Scanner - Tests all safe GPIO pins
// This will help identify which pins work on your board

int testPins[] = {2, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33};
int numPins = sizeof(testPins) / sizeof(testPins[0]);

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n=== ESP32 Pin Scanner ===");
  Serial.println("This will cycle through all safe GPIO pins");
  Serial.println("Watch your LEDs to see which pin they respond to!\n");
  
  // Set all pins as outputs
  for(int i = 0; i < numPins; i++) {
    pinMode(testPins[i], OUTPUT);
    digitalWrite(testPins[i], LOW);
  }
  
  Serial.println("Starting pin scan in 2 seconds...");
  delay(2000);
}

void loop() {
  // Cycle through each pin
  for(int i = 0; i < numPins; i++) {
    Serial.print("Testing GPIO");
    Serial.print(testPins[i]);
    Serial.println(" - LED should be ON now");
    
    digitalWrite(testPins[i], HIGH);
    delay(1000);  // Keep on for 1 second
    
    digitalWrite(testPins[i], LOW);
    delay(500);   // Off for 0.5 seconds before next pin
  }
  
  Serial.println("\n--- Scan complete! Repeating... ---\n");
  delay(1000);
}

