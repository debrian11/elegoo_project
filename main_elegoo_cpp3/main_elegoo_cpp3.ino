#include "MotorController.h"
#include "UltraSonicSensor.h"
#include "OutputPrinter.h"
#include "SerialCommandHandler.h"
#include "MotionController.h"
#include "Servo_custom.h"
#include "ServoSerialCommand.h"

// Create objects:
// MotorController
MotorController motorController(5, 7, 6, 8, 3); //(pwmA, ain1, pwmB, bin1, stby)
Servo_custom servo(10); // added this here before the MotionController Object
// MotionController motionController(motorController);
MotionController motionController(motorController, servo);
UltrasonicSensor ultrasonic(13, 12); // (trig / echo)
OutputPrinter printer(50);  // Print every x-ms
SerialCommandHandler serialHandler; // gGrabs serial 
// ServoSerialCommand servoserialHandler; // gGrabs serial 

motorstate_t currentState = STOP;
servostate_t servocurrentState = S_STOP;

unsigned long current_time;
float distance_in = 0;

void setup() {
  Serial.begin(9600);
  motorController.begin();
  ultrasonic.begin();
  servo.servo_custom_begin();
}

void loop() {
  //servo.servo_custom_sweep(90);
  //servo.servo_custom_sweep2(0, 45);

  current_time = millis();

  float new_distance = ultrasonic.getDistanceInches();
  if (new_distance > 0) {
    distance_in = new_distance;
  }

/* SERVO PORTION
  if (servoserialHandler.getCommand(newServoCommand)) {
    servocurrentState = newServoCommand;
  }
    */


// Comment this part out for now. This controls just motors
  motorstate_t newCommand;
  servostate_t newServoCommand;
  if (serialHandler.getCommand(newCommand, newServoCommand)) {
    currentState = newCommand;
    servocurrentState = newServoCommand;
  }

  Serial.print("Servo = "); Serial.print(servocurrentState);
  Serial.print(" | Motor = "); Serial.println(currentState);

/* COMMENT OUT FOR NOW, MAY 19TH 2025. JUST WANNA TEST THE SERIAL OUTPUT
  motionController.update(currentState, distance_in);
  printer.print(distance_in, currentState, current_time);
*/


// */

}
