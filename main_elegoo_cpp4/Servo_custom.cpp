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

void Servo_custom::servo_custom_sweep1() {
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

void Servo_custom::servo_custom_sweep2(int angle_start, int angle_end){
    Serial.println("Phase 1");
    for (pos_0 = angle_start; pos_0 <= angle_end; pos_0++) {
        servo_custom_object.write(pos_0);
        delay(30);
    }

    Serial.println("Phase 2");
    for (pos_0 = angle_end; pos_0 >= angle_start; pos_0--) {
        servo_custom_object.write(pos_0);
        delay(30);
    }
}
