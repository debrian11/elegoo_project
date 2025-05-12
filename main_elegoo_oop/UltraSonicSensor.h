#ifndef ULTRASONIC_SENSOR_H
#define ULTRASONIC_SENSOR_H

#include <NewPing.h>

class UltrasonicSensor {
private:
  NewPing sonar;

public:
  UltrasonicSensor(int trigPin, int echoPin, int maxDistanceCM = 300)
    : sonar(trigPin, echoPin, maxDistanceCM) {}

  void begin() {
    // No-op
  }

  float getDistanceInches() {
    int cm = sonar.ping_cm();
    return cm > 0 ? cm * 0.393701 : -1.0;  // -1 = no reading
  }
};

#endif
