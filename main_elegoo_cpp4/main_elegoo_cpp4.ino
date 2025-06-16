#include "MotorController.h"
#include "UltraSonicSensor.h"
#include "OutputPrinter.h"
#include "SerialCommandHandler.h"
#include "MotionController.h"
#include "ServoMotionController.h"
#include "Servo_custom.h"

// Create objects:
// MotorController
MotorController motorController(5, 7, 6, 8, 3); //(pwmA, ain1, pwmB, bin1, stby)
Servo_custom servo(10);
Servo_custom servo2(11);
MotionController motionController(motorController);
ServoMotionController servoMotionController(servo);
ServoMotionController servoMotionController2(servo2);
UltrasonicSensor ultrasonic(13, 12); // (trig / echo)
OutputPrinter printer(50);  // Print every x-ms
SerialCommandHandler serialHandler; // gGrabs serial 

motorstate_t currentState = STOP;
servostate_t servocurrentState = S_STOP;
unsigned long current_time;
unsigned long last_serial_time = 0;
unsigned long serial_timeout = 2500; // Time in ms for motor movement before having to enter annother cmd
float distance_in = 0;

void setup() {
  Serial.begin(115200);
  motorController.begin();
  ultrasonic.begin();
  servo.servo_custom_begin();
  servo2.servo_custom_begin();
}

void loop() {
  current_time = millis();

  float new_distance = ultrasonic.getDistanceInches();
  if (new_distance > 0) {
    distance_in = new_distance;
  }

  motorstate_t newCommand;
  servostate_t newServoCommand;
  if (serialHandler.getCommand(newCommand, newServoCommand)) {
    currentState = newCommand;
    servocurrentState = newServoCommand;
    last_serial_time = current_time;
  }

  // If serial command hasn't arrived in time, STOP
  if (current_time - last_serial_time >= serial_timeout) {
    currentState = STOP;
  }

  motionController.update(currentState, distance_in);
  servoMotionController.update(servocurrentState, distance_in);
  servoMotionController2.update(servocurrentState, distance_in);
  printer.json_print(distance_in, currentState, servocurrentState, current_time);  

}
