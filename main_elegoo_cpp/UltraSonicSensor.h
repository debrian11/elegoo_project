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

  void begin();  // declared only
  float getDistanceInches();  // declared only
};

#endif
