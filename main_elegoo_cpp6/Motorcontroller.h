#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H

class MotorController {

private:
  int _L_MTR_DIR_PIN;
  int _R_MTR_DIR_PIN;
  int _L_MTR_PWM_PIN;
  int _R_MTR_PWM_PIN;
  int _STBY_PIN;

public:
  MotorController(int L_MTR_DIR_PIN, int R_MTR_DIR_PIN, 
                  int L_MTR_PWM_PIN, int R_MTR_PWM_PIN,
                  int STBY_PIN);

  void begin();
  void drive(int &L_MTR_PWM, int &R_MTR_PWM, 
             int &L_MTR_DIR, int &R_MTR_DIR);
};

#endif
