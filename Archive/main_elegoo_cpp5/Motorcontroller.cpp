#include "Motorcontroller.h"
#include <Arduino.h>

MotorController::MotorController(int l_pwm, int l_dir, int r_pwm, int r_dir, int stby_pin) {
  L_MOTOR_PWM_PIN = l_pwm;
  L_MOTOR_DIR_PIN = l_dir;
  R_MOTOR_PWM_PIN = r_pwm;
  R_MOTOR_DIR_PIN = r_dir;
  stby = stby_pin;
}

void MotorController::begin() {
  pinMode(L_MOTOR_PWM_PIN, OUTPUT);
  pinMode(L_MOTOR_DIR_PIN, OUTPUT);
  pinMode(R_MOTOR_PWM_PIN, OUTPUT);
  pinMode(R_MOTOR_DIR_PIN, OUTPUT);
  pinMode(stby, OUTPUT);
  digitalWrite(stby, HIGH);
}

void MotorController::drive(int speedL, int speedR, bool dirL, bool dirR) {
  digitalWrite(L_MOTOR_DIR_PIN, dirL);
  digitalWrite(R_MOTOR_DIR_PIN, dirR);
  analogWrite(L_MOTOR_PWM_PIN, speedL);
  analogWrite(R_MOTOR_PWM_PIN, speedR);
}
