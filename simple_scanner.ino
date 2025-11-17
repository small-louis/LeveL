#include <Wire.h>

void setup() {
  Serial.begin(115200);
  while (!Serial);
  delay(1000);
  
  Wire.begin();
  
  Serial.println("\n=== Simple I2C Scanner ===");
  Serial.println("Scanning main I2C bus...\n");
  
  int count = 0;
  for (uint8_t addr = 1; addr <= 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("Found device at 0x");
      if (addr < 16) Serial.print("0");
      Serial.print(addr, HEX);
      
      if (addr == 0x5A) Serial.print(" (DRV2605)");
      if (addr == 0x70) Serial.print(" (TCA9548A)");
      
      Serial.println();
      count++;
    }
  }
  
  Serial.print("\nTotal devices found: ");
  Serial.println(count);
  Serial.println("\nDone!");
}

void loop() {
}


