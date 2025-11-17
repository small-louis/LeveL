// Simple GSR Monitor - Based on Grove GSR Example
// Connect: Black->GND, Red->VIN, Yellow->GPIO34

const int GSR = 34;
int sensorValue = 0;
int gsr_average = 0;

void setup() {
  Serial.begin(115200);
}

void loop() {
  long sum = 0;
  for (int i = 0; i < 10; i++) {
    sensorValue = analogRead(GSR);
    sum += sensorValue;
    delay(5);
  }
  gsr_average = sum / 10;
  Serial.println(gsr_average);
  delay(50);  // Send at ~10Hz to match plot update rate
}
