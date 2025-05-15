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
    void servo_custom_write(int servo_angle1);
    void servo_custom_sweep1(int servo_angle2);
    void servo_custom_sweep2(int angle_start, int angle_end);
    int initial_angle;
    int pos_0;
};

#endif