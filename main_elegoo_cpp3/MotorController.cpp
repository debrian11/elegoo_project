#include "MotorController.h"
#include <Arduino.h>

MotorController::MotorController(int _pwmA, int _ain1,
                                 int _pwmB, int _bin1,
                                 int _stby)
  : pwmA(_pwmA), ain1(_ain1),
    pwmB(_pwmB), bin1(_bin1),
    stby(_stby), speed(50) {}

/* this commented out section is the same as the constructor above
MotorController::MotorController(int _pwmA, int _ain1, int _pwmB, int _bin1, int _stby) {
  pwmA = _pwmA;
  ain1 = _ain1;
  pwmB = _pwmB;
  bin1 = _bin1;
  stby = _stby;
  speed = 100;
}
*/

void MotorController::begin() {
  pinMode(ain1, OUTPUT);
  pinMode(bin1, OUTPUT);
  pinMode(pwmA, OUTPUT);
  pinMode(pwmB, OUTPUT);
  pinMode(stby, OUTPUT);
  digitalWrite(stby, HIGH);
}

void MotorController::forward() {
  digitalWrite(ain1, HIGH);
  analogWrite(pwmA, speed);
  digitalWrite(bin1, HIGH);
  analogWrite(pwmB, speed);
}

void MotorController::backward() {
  digitalWrite(ain1, LOW);
  analogWrite(pwmA, speed);
  digitalWrite(bin1, LOW);
  analogWrite(pwmB, speed);
}

void MotorController::turnLeft() {
  digitalWrite(ain1, LOW);
  analogWrite(pwmA, speed);
  digitalWrite(bin1, HIGH);
  analogWrite(pwmB, speed);
}

void MotorController::turnRight() {
  digitalWrite(ain1, HIGH);
  analogWrite(pwmA, speed);
  digitalWrite(bin1, LOW);
  analogWrite(pwmB, speed);
}

void MotorController::stop() {
  analogWrite(pwmA, 0);
  analogWrite(pwmB, 0);
}

void MotorController::setSpeed(int s) {
  speed = constrain(s, 0, 255);
}
