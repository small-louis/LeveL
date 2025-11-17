// Simple Heart Rate Monitor for ESP32
// Calculates BPM with smoothing and sends to serial

const int heartPin = 34;
const int numSamples = 100;
int samples[numSamples];
int sampleIndex = 0;

// Beat detection
unsigned long beatTimes[5];  // Store last 5 beat times
int beatIndex = 0;
unsigned long lastBeatTime = 0;
bool wasBelowThreshold = true;

// BPM smoothing
int bpmReadings[8];  // Store last 8 BPM readings
int bpmIndex = 0;
int currentBPM = 0;
unsigned long lastPrintTime = 0;

void setup() {
  Serial.begin(115200);
  pinMode(heartPin, INPUT);
  
  // Initialize arrays
  for (int i = 0; i < 5; i++) beatTimes[i] = 0;
  for (int i = 0; i < 8; i++) bpmReadings[i] = 0;
}

void loop() {
  // Read and store sensor value
  int value = analogRead(heartPin);
  samples[sampleIndex] = value;
  sampleIndex = (sampleIndex + 1) % numSamples;
  
  // Calculate adaptive threshold
  long sum = 0;
  int minVal = 4095;
  int maxVal = 0;
  for (int i = 0; i < numSamples; i++) {
    sum += samples[i];
    if (samples[i] < minVal) minVal = samples[i];
    if (samples[i] > maxVal) maxVal = samples[i];
  }
  int avg = sum / numSamples;
  int range = maxVal - minVal;
  int threshold = avg + (range / 3);  // Dynamic threshold
  
  // Detect beat (rising edge detection)
  unsigned long now = millis();
  if (value > threshold && wasBelowThreshold && now - lastBeatTime > 400) {  // Min 400ms = 150 BPM max
    unsigned long interval = now - lastBeatTime;
    
    if (interval >= 400 && interval <= 1500) {  // Valid: 40-150 BPM
      // Store beat time
      beatTimes[beatIndex] = now;
      beatIndex = (beatIndex + 1) % 5;
      lastBeatTime = now;
      
      // Calculate BPM from last few beats
      int validBeats = 0;
      unsigned long totalInterval = 0;
      for (int i = 0; i < 4; i++) {
        if (beatTimes[i] > 0 && beatTimes[i+1] > 0 && beatTimes[i+1] > beatTimes[i]) {
          totalInterval += beatTimes[i+1] - beatTimes[i];
          validBeats++;
        }
      }
      
      if (validBeats > 0) {
        int instantBPM = 60000 / (totalInterval / validBeats);
        
        // Store and smooth BPM
        bpmReadings[bpmIndex] = instantBPM;
        bpmIndex = (bpmIndex + 1) % 8;
        
        // Calculate average BPM
        int bpmSum = 0;
        int validReadings = 0;
        for (int i = 0; i < 8; i++) {
          if (bpmReadings[i] > 0) {
            bpmSum += bpmReadings[i];
            validReadings++;
          }
        }
        
        if (validReadings > 3) {
          currentBPM = bpmSum / validReadings;
        }
      }
    }
    
    wasBelowThreshold = false;
  } else if (value < threshold) {
    wasBelowThreshold = true;
  }
  
  // Print smoothed BPM every 200ms
  if (now - lastPrintTime > 200 && currentBPM > 0) {
    Serial.println(currentBPM);
    lastPrintTime = now;
  }
  
  delay(10);  // 100Hz sampling
}
