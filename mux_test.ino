#include <Wire.h>
#include "Adafruit_DRV2605.h"

#define TCAADDR 0x70
Adafruit_DRV2605 drv;

// Motor configuration for each channel
struct MotorConfig {
  int bpm;
  uint8_t lub_effect;
  uint8_t dub_effect;
  bool lub_enabled;
  bool dub_enabled;
  unsigned long lastBeat;
  bool inLubDub;
  unsigned long lubTime;
};

MotorConfig motors[6];
const int lubDubDelay = 150;

void tcaselect(uint8_t i) {
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  
  Serial.println("Advanced Haptic Control - 6 Motors");
  
  // Initialize all motors with defaults
  for (int i = 0; i < 6; i++) {
    motors[i].bpm = 60;
    motors[i].lub_effect = 1;   // Strong Click 100%
    motors[i].dub_effect = 3;   // Sharp Click 100%
    motors[i].lub_enabled = true;
    motors[i].dub_enabled = true;
    motors[i].lastBeat = 0;
    motors[i].inLubDub = false;
    motors[i].lubTime = 0;
  }
  
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

void triggerEffect(uint8_t ch, uint8_t effect) {
  if (effect == 0 || effect > 123) return;  // Invalid effect
  tcaselect(ch);
  delay(10);
  drv.setWaveform(0, effect);
  drv.setWaveform(1, 0);
  drv.go();
}

void loop() {
  unsigned long now = millis();
  
  // Handle heartbeat timing for all channels
  for (int ch = 0; ch < 6; ch++) {
    if (motors[ch].bpm == 0) continue;  // Motor disabled
    
    int interval = 60000 / motors[ch].bpm;
    
    if (!motors[ch].inLubDub && now - motors[ch].lastBeat >= interval) {
      // Time for lub
      if (motors[ch].lub_enabled) {
        triggerEffect(ch, motors[ch].lub_effect);
      }
      motors[ch].lubTime = now;
      motors[ch].inLubDub = true;
    }
    
    if (motors[ch].inLubDub && now - motors[ch].lubTime >= lubDubDelay) {
      // Time for dub
      if (motors[ch].dub_enabled) {
        triggerEffect(ch, motors[ch].dub_effect);
      }
      motors[ch].lastBeat = now;
      motors[ch].inLubDub = false;
    }
  }
  
  // Read commands from serial
  if (Serial.available()) {
    char cmd = Serial.peek();
    
    if (cmd == 'S') {
      // SYNC command - reset all timers
      Serial.read();
      unsigned long syncNow = millis();
      for (int i = 0; i < 6; i++) {
        motors[i].lastBeat = syncNow;
        motors[i].inLubDub = false;
      }
      Serial.println("Synced");
    } else {
      // Motor config: "CH:BPM:LUB_EFFECT:DUB_EFFECT:LUB_EN:DUB_EN"
      // Example: "0:72:12:14:1:1"
      int ch = Serial.parseInt();
      if (Serial.read() == ':') {
        int bpm = Serial.parseInt();
        if (Serial.read() == ':') {
          int lub_eff = Serial.parseInt();
          if (Serial.read() == ':') {
            int dub_eff = Serial.parseInt();
            if (Serial.read() == ':') {
              int lub_en = Serial.parseInt();
              if (Serial.read() == ':') {
                int dub_en = Serial.parseInt();
                
                // Validate and update
                if (ch >= 0 && ch <= 5) {
                  motors[ch].bpm = constrain(bpm, 0, 200);
                  motors[ch].lub_effect = constrain(lub_eff, 0, 123);
                  motors[ch].dub_effect = constrain(dub_eff, 0, 123);
                  motors[ch].lub_enabled = (lub_en == 1);
                  motors[ch].dub_enabled = (dub_en == 1);
                }
              }
            }
          }
        }
      }
    }
  }
}
