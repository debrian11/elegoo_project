#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H

class MotorController {

private:
  int _L_MTR_DIR_PIN;
  int _R_MTR_DIR_PIN;
  int _L_MTR_PWM_PIN;
  int _R_MTR_PWM_PIN;
  int _STBY_PIN;

  int _current_L_PWM = 0;
  int _current_R_PWM = 0;
  int _current_L_DIR = 0;
  int _current_R_DIR = 0;


public:
  MotorController(int L_MTR_DIR_PIN, int R_MTR_DIR_PIN, 
                  int L_MTR_PWM_PIN, int R_MTR_PWM_PIN,
                  int STBY_PIN);

  void begin();
  void drive(int &L_MTR_PWM, int &R_MTR_PWM, 
             int &L_MTR_DIR, int &R_MTR_DIR);

      // Add getter functions
  int getLeftPWM() { return _current_L_PWM; }
  int getRightPWM() { return _current_R_PWM; }
  int getLeftDIR() { return _current_L_DIR; }
  int getRightDIR() { return _current_R_DIR; }
};

#endif
