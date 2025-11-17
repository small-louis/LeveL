#include <Wire.h>

#define TCAADDR 0x70

void tcaselect(uint8_t i) {
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200);
  while (!Serial);
  delay(1000);
  
  Wire.begin();
  
  Serial.println("\n=== I2C Scanner ===");
  
  // First check if multiplexer is present
  Serial.print("Checking for multiplexer at 0x70... ");
  Wire.beginTransmission(TCAADDR);
  if (Wire.endTransmission() == 0) {
    Serial.println("FOUND!");
  } else {
    Serial.println("NOT FOUND!");
    Serial.println("Check multiplexer wiring!");
    while(1);
  }
  
  // Scan each channel
  for (uint8_t t = 0; t < 8; t++) {
    tcaselect(t);
    delay(10);  // Give channel time to stabilize
    Serial.print("Channel ");
    Serial.print(t);
    Serial.print(": ");
    
    bool found = false;
    for (uint8_t addr = 1; addr <= 127; addr++) {
      if (addr == TCAADDR) continue;
      
      Wire.beginTransmission(addr);
      if (Wire.endTransmission() == 0) {
        Serial.print("0x");
        if (addr < 16) Serial.print("0");
        Serial.print(addr, HEX);
        Serial.print(" ");
        found = true;
      }
    }
    if (!found) Serial.print("empty");
    Serial.println();
  }
  
  Serial.println("\nDone!");
}

void loop() {
}

