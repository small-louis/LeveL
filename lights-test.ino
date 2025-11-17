// ESP32-compatible pin definitions
// Note: ESP32 has different pin layouts depending on the board
const int redPin = 22;    // External red LED on GPIO17
const int greenPin = 23;  // External green LED on GPIO16
const int builtinLED = 2; // Most ESP32 boards have LED on GPIO2

void setup() {
  Serial.begin(115200);  // ESP32 standard baud rate
  pinMode(greenPin, OUTPUT);
  pinMode(redPin, OUTPUT);
  pinMode(builtinLED, OUTPUT);
  
  // Flash all LEDs to show setup is complete
  digitalWrite(greenPin, HIGH);
  digitalWrite(redPin, HIGH);
  digitalWrite(builtinLED, HIGH);
  delay(500);
  digitalWrite(greenPin, LOW);
  digitalWrite(redPin, LOW);
  digitalWrite(builtinLED, LOW);
  
  Serial.println("ESP32 Ready!");
}

void loop() {
  if (Serial.available() > 0){
    String msg = Serial.readString();
    msg.trim();  // Remove any whitespace/newlines
    
    // Echo back what was received for debugging
    Serial.print("Received: '");
    Serial.print(msg);
    Serial.print("' (length: ");
    Serial.print(msg.length());
    Serial.println(")");

    if (msg == "ON"){
      digitalWrite(greenPin, HIGH);
      digitalWrite(builtinLED, HIGH);  // Also control builtin LED for testing
      Serial.println("Green LED ON + Builtin LED ON");
    }
    else if (msg == "OFF"){
      digitalWrite(greenPin, LOW);
      digitalWrite(builtinLED, LOW);  // Also control builtin LED for testing
      Serial.println("Green LED OFF + Builtin LED OFF");
    }
    else {
      Serial.println("Unknown command - flashing red LED");
      for (int i = 0; i < 5; i++){
        digitalWrite(redPin, HIGH);
        delay(100);
        digitalWrite(redPin, LOW);
        delay(100);
      }
    }
  }
}