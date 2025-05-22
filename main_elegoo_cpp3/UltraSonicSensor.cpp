#include "UltraSonicSensor.h"
#include <Arduino.h>  // needed for millis()

void UltrasonicSensor::begin() {
  // No initialization needed. here just because
}

float UltrasonicSensor::getDistanceInches() {
  //unsigned long current_time = millis();
  if (millis() - last_update >= 50) {
    last_update = millis();
    int cm = sonar.ping_cm();
    return cm > 0 ? cm * 0.393701 : -1.0;
    /*
    if (cm > 0) { 
      return cm * 0.393701;
      } else {
      return -1.0;
      }
    */
  }
  return -1.0;
}
