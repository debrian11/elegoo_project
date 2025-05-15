#include "MotorController.h"
#include "UltraSonicSensor.h"
#include "OutputPrinter.h"
#include "SerialCommandHandler.h"
#include "MotionController.h"

// Create objects:
// MotorController
MotorController motorController(5, 7, 6, 8, 3); //(pwmA, ain1, pwmB, bin1, stby)
MotionController motionController(motorController);
UltrasonicSensor ultrasonic(13, 12); // (trig / echo)
OutputPrinter printer(50);  // Print every x-ms
SerialCommandHandler serialHandler;

motorstate_t currentState = STOP;
unsigned long current_time;
float distance_in = 0;

void setup() {
  Serial.begin(9600);
  motorController.begin();
  ultrasonic.begin();
}

void loop() {
  current_time = millis();

  float new_distance = ultrasonic.getDistanceInches();
  if (new_distance > 0) {
    distance_in = new_distance;
  }

  motorstate_t newCommand;
  if (serialHandler.getCommand(newCommand)) {
    currentState = newCommand;
  }

  motionController.update(currentState, distance_in);
  printer.print(distance_in, currentState, current_time);
}
