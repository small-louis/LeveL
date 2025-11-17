// Ultra-simple ESP32 test - just blink and print
// This will help us verify the ESP32 is working at all

void setup() {
  Serial.begin(115200);
  
  // Try multiple possible LED pins
  pinMode(2, OUTPUT);   // Common builtin LED pin
  pinMode(LED_BUILTIN, OUTPUT);  // Use board-defined LED pin
  pinMode(16, OUTPUT);  // Your green LED
  pinMode(17, OUTPUT);  // Your red LED
  
  Serial.println("\n\n=== ESP32 Basic Test Starting ===");
  Serial.print("LED_BUILTIN is defined as pin: ");
  Serial.println(LED_BUILTIN);
  
  // Blink multiple times at startup so it's obvious
  for(int i = 0; i < 5; i++) {
    Serial.println("BLINK!");
    digitalWrite(2, HIGH);
    digitalWrite(LED_BUILTIN, HIGH);
    digitalWrite(16, HIGH);
    digitalWrite(17, HIGH);
    delay(200);
    
    digitalWrite(2, LOW);
    digitalWrite(LED_BUILTIN, LOW);
    digitalWrite(16, LOW);
    digitalWrite(17, LOW);
    delay(200);
  }
  
  Serial.println("=== Setup Complete ===");
  Serial.println("Type anything and press Enter...");
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    
    Serial.print("You typed: ");
    Serial.println(input);
    
    // Turn all LEDs on
    Serial.println("Turning all LEDs ON");
    digitalWrite(2, HIGH);
    digitalWrite(LED_BUILTIN, HIGH);
    digitalWrite(16, HIGH);
    digitalWrite(17, HIGH);
    
    delay(1000);
    
    // Turn all LEDs off
    Serial.println("Turning all LEDs OFF");
    digitalWrite(2, LOW);
    digitalWrite(LED_BUILTIN, LOW);
    digitalWrite(16, LOW);
    digitalWrite(17, LOW);
  }
}

