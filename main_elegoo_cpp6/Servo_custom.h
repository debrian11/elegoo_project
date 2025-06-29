#ifndef SERVO_CUSTOM_H
#define SERVO_CUSTOM_H

#include <Servo.h> // Arduino servo library

class Servo_custom {
private:
    Servo servo_custom_object;
    int servo_pin;
    int _currentAngle;

public:
    Servo_custom(int _servo_pin);
    void servo_custom_begin();
    void servo_custom_sweep(int sweep_status);
    int initial_angle;
    int currentAngle = 40;
    unsigned long lastMoveTime = 0;
    bool goingUp = true;

    const int step = 10;
    const int minAngle = 35;
    const int maxAngle = 145;
    const unsigned long interval = 120;
};

#endif