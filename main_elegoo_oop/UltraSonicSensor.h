#ifndef ULTRASONIC_SENSOR_H
#define ULTRASONIC_SENSOR_H

#include <NewPing.h>

class UltrasonicSensor {
private:
  NewPing sonar;
  unsigned long last_update;

public:
  UltrasonicSensor(int trigPin, int echoPin, int maxDistanceCM = 300)
    : sonar(trigPin, echoPin, maxDistanceCM), last_update(0) {}

  void begin() {
    // No initialization needed, but included for consistency
  }

  float getDistanceInches() {
    unsigned long current_time = millis();
    if (current_time - last_update >= 50) {
      last_update = current_time;
      int cm = sonar.ping_cm();
      return cm > 0 ? cm * 0.393701 : -1.0;
    }
    return -1.0;
  }
};

#endif
