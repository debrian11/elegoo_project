// OOP Code: Convert this function into a MotorControll class first
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
                  int _stby)
    : pwmA(_pwmA), ain1(_ain1),
      pwmB(_pwmB), bin1(_bin1),
      stby(_stby), speed(100) {}

  void begin() {
    pinMode(ain1, OUTPUT);
    pinMode(bin1, OUTPUT);
    pinMode(pwmA, OUTPUT);
    pinMode(pwmB, OUTPUT);
    pinMode(stby, OUTPUT);
    digitalWrite(stby, HIGH);
  }

  void forward() {
    digitalWrite(ain1, HIGH);
    analogWrite(pwmA, speed);

    digitalWrite(bin1, HIGH);
    analogWrite(pwmB, speed);
  }

  void backward() {
    digitalWrite(ain1, LOW);
    analogWrite(pwmA, speed);

    digitalWrite(bin1, LOW);
    analogWrite(pwmB, speed);
  }

  void turnLeft() {
    digitalWrite(ain1, LOW);
    analogWrite(pwmA, speed);

    digitalWrite(bin1, HIGH);
    analogWrite(pwmB, speed);
  }

  void turnRight() {
    digitalWrite(ain1, HIGH);
    analogWrite(pwmA, speed);

    digitalWrite(bin1, LOW);
    analogWrite(pwmB, speed);
  }

  void stop() {
    analogWrite(pwmA, 0);
    analogWrite(pwmB, 0);
  }

  void setSpeed(int s) {
    speed = constrain(s, 0, 255);
  }
};

#endif