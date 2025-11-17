/*
 * GSR Sensor Raw Test
 * Just reads and prints raw values to verify sensor is working
 */

const int GSR_PIN = 34;

void setup() {
  Serial.begin(115200);
  pinMode(GSR_PIN, INPUT);
  Serial.println("GSR Raw Test");
  Serial.println("Watch values change when you:");
  Serial.println("1. Touch the pads");
  Serial.println("2. Remove your fingers");
  Serial.println("3. Press harder\n");
}

void loop() {
  int raw = analogRead(GSR_PIN);
  
  Serial.print("Raw: ");
  Serial.print(raw);
  Serial.print("  |  ");
  
  // Visual bar
  Serial.print("[");
  for (int i = 0; i < raw / 50; i++) {
    Serial.print("=");
  }
  Serial.println("]");
  
  delay(200);
}

