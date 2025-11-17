/*
 * Integrated GSR + Haptic Control System
 * 
 * Combines GSR sensor reading with 6-motor haptic control via multiplexer
 * 
 * HARDWARE:
 *   - ESP32
 *   - GSR sensor on GPIO34 (analog)
 *   - TCA9548A I2C multiplexer
 *   - 6x DRV2605 haptic drivers on multiplexer channels 0-5
 * 
 * SERIAL PROTOCOL:
 *   FROM PYTHON:
 *     - "CH:BPM:LUB:DUB:LUB_EN:DUB_EN" - Motor config
 *     - "S" - Sync all motors
 *   TO PYTHON:
 *     - "G:value" - GSR reading (e.g., "G:2650")
 */

#include <Wire.h>
#include "Adafruit_DRV2605.h"

#define TCAADDR 0x70
#define GSR_PIN 34

Adafruit_DRV2605 drv;

// Motor configuration
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

// GSR timing
unsigned long lastGSRSend = 0;
const int GSR_INTERVAL = 100;  // Send GSR every 100ms (10Hz)

void tcaselect(uint8_t i) {
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  pinMode(GSR_PIN, INPUT);
  
  Serial.println("Integrated GSR + Haptic System");
  
  // Initialize motors with defaults
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
  
  // Initialize all 6 haptic channels
  for (uint8_t ch = 0; ch < 6; ch++) {
    tcaselect(ch);
    delay(10);
    if (drv.begin()) {
      Serial.print("Motor ");
      Serial.print(ch);
      Serial.println(": OK");
      drv.selectLibrary(1);
      drv.setMode(DRV2605_MODE_INTTRIG);
    } else {
      Serial.print("Motor ");
      Serial.print(ch);
      Serial.println(": FAIL");
    }
  }
  
  Serial.println("Ready");
}

void triggerEffect(uint8_t ch, uint8_t effect) {
  if (effect == 0 || effect > 123) return;
  tcaselect(ch);
  delay(10);
  drv.setWaveform(0, effect);
  drv.setWaveform(1, 0);
  drv.go();
}

void loop() {
  unsigned long now = millis();
  
  // ===== GSR READING & SENDING =====
  if (now - lastGSRSend >= GSR_INTERVAL) {
    // Average 10 readings
    long sum = 0;
    for (int i = 0; i < 10; i++) {
      sum += analogRead(GSR_PIN);
      delay(5);
    }
    int gsr_avg = sum / 10;
    
    // Send GSR data with "G:" prefix
    Serial.print("G:");
    Serial.println(gsr_avg);
    
    lastGSRSend = now;
  }
  
  // ===== HAPTIC MOTOR CONTROL =====
  for (int ch = 0; ch < 6; ch++) {
    if (motors[ch].bpm == 0) continue;
    
    int interval = 60000 / motors[ch].bpm;
    
    if (!motors[ch].inLubDub && now - motors[ch].lastBeat >= interval) {
      // Trigger lub
      if (motors[ch].lub_enabled) {
        triggerEffect(ch, motors[ch].lub_effect);
      }
      motors[ch].lubTime = now;
      motors[ch].inLubDub = true;
    }
    
    if (motors[ch].inLubDub && now - motors[ch].lubTime >= lubDubDelay) {
      // Trigger dub
      if (motors[ch].dub_enabled) {
        triggerEffect(ch, motors[ch].dub_effect);
      }
      motors[ch].lastBeat = now;
      motors[ch].inLubDub = false;
    }
  }
  
  // ===== SERIAL COMMAND PROCESSING =====
  if (Serial.available()) {
    char cmd = Serial.peek();
    
    if (cmd == 'S') {
      // SYNC command
      Serial.read();
      unsigned long syncNow = millis();
      for (int i = 0; i < 6; i++) {
        motors[i].lastBeat = syncNow;
        motors[i].inLubDub = false;
      }
      Serial.println("Synced");
    } else if (cmd >= '0' && cmd <= '9') {
      // Motor config: "CH:BPM:LUB_EFFECT:DUB_EFFECT:LUB_EN:DUB_EN"
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
                
                // Consume remaining newline
                while (Serial.available() && Serial.peek() == '\n') {
                  Serial.read();
                }
                
                if (ch >= 0 && ch <= 5) {
                  motors[ch].bpm = constrain(bpm, 0, 200);
                  motors[ch].lub_effect = constrain(lub_eff, 0, 123);
                  motors[ch].dub_effect = constrain(dub_eff, 0, 123);
                  motors[ch].lub_enabled = (lub_en == 1);
                  motors[ch].dub_enabled = (dub_en == 1);
                  
                  // Send acknowledgment (optional - can comment out to reduce serial traffic)
                  Serial.print("M");
                  Serial.print(ch);
                  Serial.print(":");
                  Serial.println(bpm);
                }
              }
            }
          }
        }
      }
    } else {
      // Unknown command, consume it
      Serial.read();
    }
  }
}
