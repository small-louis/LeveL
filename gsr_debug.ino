// GSR Debug - Raw readings without averaging
// This will show you if the sensor is working at all

const int GSR = 34;

void setup() {
  Serial.begin(115200);
  pinMode(GSR, INPUT);
  Serial.println("\n=== GSR DEBUG TEST ===");
  Serial.println("Watch for changes when you:");
  Serial.println("1. Touch the sensor pads");
  Serial.println("2. Remove your fingers");
  Serial.println("3. Touch with wet fingers");
  Serial.println("====================\n");
  delay(2000);
}

void loop() {
  int raw = analogRead(GSR);
  
  // Print with visual indicator
  Serial.print("Raw: ");
  Serial.print(raw);
  Serial.print("  ");
  
  // Bar graph
  Serial.print("[");
  int bars = raw / 50;
  for (int i = 0; i < bars; i++) {
    Serial.print("=");
  }
  for (int i = bars; i < 80; i++) {
    Serial.print(" ");
  }
  Serial.println("]");
  
  delay(100);  // 10Hz updates
}

