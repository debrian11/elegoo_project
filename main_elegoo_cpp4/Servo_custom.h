#ifndef SERVO_CUSTOM_H
#define SERVO_CUSTOM_H

#include <Servo.h> // Arduino servo library

class Servo_custom {
private:
    Servo servo_custom_object;
    int servo_pin;

public:
    Servo_custom(int _servo_pin);
    void servo_custom_begin();
    void servo_custom_stop();
    void servo_custom_write(int servo_angle1);
    void servo_custom_sweep1();
    void servo_custom_sweep2(int angle_start, int angle_end);
    int initial_angle;
    int pos_0;
    unsigned long servo_last_update;
    int currentAngle = 40;
    unsigned long lastMoveTime = 0;
    bool goingUp = true;

    const int step = 10;
    const int minAngle = 40;
    const int maxAngle = 140;
    const unsigned long interval = 200;
};

#endif