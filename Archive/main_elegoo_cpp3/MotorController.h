#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H

class MotorController {
private:
  int pwmA, ain1;
  int pwmB, bin1;
  int stby;
  int speed;

public:
  MotorController(int _pwmA, int _ain1,
                  int _pwmB, int _bin1,
                  int _stby);
  void begin();
  void forward();
  void backward();
  void turnLeft();
  void turnRight();
  void stop();
  void setSpeed(int s);
};

#endif
