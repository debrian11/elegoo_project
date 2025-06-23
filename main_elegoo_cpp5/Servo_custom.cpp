#include "Servo_custom.h"
#include <Arduino.h>

Servo_custom::Servo_custom(int _servo_pin) : servo_pin(_servo_pin), initial_angle(90) {}

void Servo_custom::servo_custom_begin() {
    servo_custom_object.attach(servo_pin);
    servo_custom_object.write(initial_angle);
}

void Servo_custom::servo_custom_stop(){
    servo_custom_object.write(90);
}

void Servo_custom::servo_custom_write(int servo_angle1){
    servo_custom_object.write(servo_angle1);
}

void Servo_custom::servo_custom_sweep(int sweep_status) {
  if (sweep_status == 1) {
    if (millis() - lastMoveTime >= interval) {
      lastMoveTime = millis();
      servo_custom_object.write(currentAngle);

    if (goingUp) {
      currentAngle += step;
      if (currentAngle >= maxAngle) {
        currentAngle = maxAngle;
        goingUp = false;
      }
    } else {
      currentAngle -= step;
      if (currentAngle <= minAngle) {
        currentAngle = minAngle;
        goingUp = true;
      }
    }
  }
  }

}
