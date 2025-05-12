#include "MotorController.h"
#include "UltraSonicSensor.h"
#include "OutputPrinter.h"
#include "SerialCommandHandler.h"

// MotorController(pwmA, ain1, pwmB, bin1, stby)
MotorController motorController(5, 7, 6, 8, 3);
UltrasonicSensor ultrasonic(13, 12);
OutputPrinter printer(50);  // Print every 500ms
SerialCommandHandler serialHandler;

motorstate_t currentState = STOP;
unsigned long current_time;
float distance_in = 0;

void setup() {
  Serial.begin(9600);
  motorController.begin();
  ultrasonic.begin();
}

void updateMotors(motorstate_t state, float distance_in) {
  static bool objectTooClose = false;

  if (distance_in <= 2) {
    motorController.stop();
    objectTooClose = true;
  } 
  else if (distance_in > 6 && objectTooClose) {
    // Only resume if a prior stop occurred due to obstacle
    objectTooClose = false;

    switch (state) {
      case FORWARD:  motorController.forward(); break;
      case BACKWARD: motorController.backward(); break;
      case LEFT:     motorController.turnLeft(); break;
      case RIGHT:    motorController.turnRight(); break;
      case STOP:     motorController.stop(); break;
    }
  }
  else if (!objectTooClose) {
    // Normal command flow
    switch (state) {
      case FORWARD:  motorController.forward(); break;
      case BACKWARD: motorController.backward(); break;
      case LEFT:     motorController.turnLeft(); break;
      case RIGHT:    motorController.turnRight(); break;
      case STOP:     motorController.stop(); break;
    }
  }
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

  updateMotors(currentState, distance_in);
  printer.print(distance_in, currentState, current_time);
}
