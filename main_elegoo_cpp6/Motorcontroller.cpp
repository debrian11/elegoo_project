#include "Motorcontroller.h"
#include <Arduino.h>

MotorController::MotorController(int L_MTR_DIR_PIN, int R_MTR_DIR_PIN, 
                                 int L_MTR_PWM_PIN, int R_MTR_PWM_PIN,
                                 int STBY_PIN)
  : _L_MTR_DIR_PIN(L_MTR_DIR_PIN),
    _R_MTR_DIR_PIN(R_MTR_DIR_PIN),
    _L_MTR_PWM_PIN(L_MTR_PWM_PIN),
    _R_MTR_PWM_PIN(R_MTR_PWM_PIN),
    _STBY_PIN(STBY_PIN)
{}


void MotorController::begin() {
  pinMode(_L_MTR_DIR_PIN, OUTPUT);
  pinMode(_R_MTR_DIR_PIN, OUTPUT);
  pinMode(_L_MTR_PWM_PIN, OUTPUT);
  pinMode(_R_MTR_PWM_PIN, OUTPUT);
  pinMode(_STBY_PIN, OUTPUT);
  digitalWrite(_STBY_PIN, HIGH);
}


void MotorController::drive(int &L_MTR_PWM, int &R_MTR_PWM, 
                            int &L_MTR_DIR, int &R_MTR_DIR) {
  digitalWrite(_L_MTR_DIR_PIN, L_MTR_DIR);
  digitalWrite(_R_MTR_DIR_PIN, R_MTR_DIR);
  analogWrite(_L_MTR_PWM_PIN, L_MTR_PWM);
  analogWrite(_R_MTR_PWM_PIN, R_MTR_PWM);

  // Store the current values to print later
  _current_L_PWM = L_MTR_PWM;
  _current_R_PWM = R_MTR_PWM;
  _current_L_DIR = L_MTR_DIR;
  _current_R_DIR = R_MTR_DIR;
}