#ifndef ULTRASONIC_SENSOR_H
#define ULTRASONIC_SENSOR_H

#include <NewPing.h>

class UltrasonicSensor {
public:
  UltrasonicSensor(int trigPin, int echoPin, int maxDistanceCM = 300)
    : sonar(trigPin, echoPin, maxDistanceCM), last_update(0) {}

  void begin();  // declared only. Not really needed
  float getDistanceInches();  // This is the actual function that will get distance

private:
  NewPing sonar;
  unsigned long last_update;
};

#endif
