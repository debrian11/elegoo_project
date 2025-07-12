#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H

class MotorController {
private:
  int L_MOTOR_PWM_PIN, L_MOTOR_DIR_PIN;
  int R_MOTOR_PWM_PIN, R_MOTOR_DIR_PIN;
  int stby;

public:
  MotorController(int l_pwm, int l_dir, int r_pwm, int r_dir, int stby_pin);
  void begin();
  void drive(int speedL, int speedR, bool dirL, bool dirR);
};

#endif
