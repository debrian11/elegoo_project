#include "UltraSonicSensor.h"
#include <Arduino.h>  // needed for millis()

void UltrasonicSensor::begin() {
  // No initialization needed. here just because
}

float UltrasonicSensor::getDistanceInches() {
  unsigned long current_time = millis();
  if (current_time - last_update >= 50) {
    last_update = current_time;
    int cm = sonar.ping_cm();
    return cm > 0 ? cm * 0.393701 : -1.0;
  }
  return -1.0;
}
