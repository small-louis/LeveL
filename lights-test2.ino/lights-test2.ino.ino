#include <Wire.h>
#include "Adafruit_DRV2605.h"

#define TCAADDR 0x70
Adafruit_DRV2605 drv;

// Timing state for each channel
unsigned long lastBeat[6] = {0, 0, 0, 0, 0, 0};
bool inLubDub[6] = {false, false, false, false, false, false};
unsigned long lubTime[6] = {0, 0, 0, 0, 0, 0};
int BPM[6] = {40, 40, 40, 40, 40, 40};  // BPM for each channel
const int lubDubDelay = 150;

void tcaselect(uint8_t i) {
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  
  Serial.println("Multiplexer Test - 6 Motors");
  
  // Init all 6 channels
  for (uint8_t ch = 0; ch < 6; ch++) {
    tcaselect(ch);
    delay(10);
    if (drv.begin()) {
      Serial.print("Ch");
      Serial.print(ch);
      Serial.println(": Found");
      drv.selectLibrary(1);
      drv.setMode(DRV2605_MODE_INTTRIG);
    } else {
      Serial.print("Ch");
      Serial.print(ch);
      Serial.println(": Not found");
    }
  }
  
  Serial.println("Ready");
}

void triggerLub(uint8_t ch) {
  tcaselect(ch);
  delay(10);
  drv.setWaveform(0, 12);
  drv.setWaveform(1, 0);
  drv.go();
}

void triggerDub(uint8_t ch) {
  tcaselect(ch);
  delay(10);
  drv.setWaveform(0, 14);
  drv.setWaveform(1, 0);
  drv.go();
}

void loop() {
  unsigned long now = millis();
  
  // Handle heartbeat timing for all channels
  for (int ch = 0; ch < 6; ch++) {
    int interval = 60000 / BPM[ch];
    
    if (!inLubDub[ch] && now - lastBeat[ch] >= interval) {
      // Time for lub
      triggerLub(ch);
      lubTime[ch] = now;
      inLubDub[ch] = true;
    }
    
    if (inLubDub[ch] && now - lubTime[ch] >= lubDubDelay) {
      // Time for dub
      triggerDub(ch);
      lastBeat[ch] = now;
      inLubDub[ch] = false;
    }
  }
  
  // Read commands from serial
  if (Serial.available()) {
    char cmd = Serial.peek();
    
    if (cmd == 'S') {
      // SYNC command - reset all timers
      Serial.read();  // consume 'S'
      unsigned long now = millis();
      for (int i = 0; i < 6; i++) {
        lastBeat[i] = now;
        inLubDub[i] = false;
      }
      Serial.println("Synced");
    } else {
      // BPM update: "CH:BPM" e.g. "0:80"
      int ch = Serial.parseInt();
      if (Serial.read() == ':') {
        int bpm = Serial.parseInt();
        if (ch >= 0 && ch <= 5 && bpm >= 0 && bpm <= 200) {
          BPM[ch] = bpm;
        }
      }
    }
  }
}

