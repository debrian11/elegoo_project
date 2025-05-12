#include "MotorController.h"
#include "UltraSonicSensor.h"
#include "OutputPrinter.h"
#include "SerialCommandHandler.h"

#define PWMA 5
#define AIN1 7
#define PWMB 6
#define BIN1 8
#define STBY 3

#define trigPin 13
#define echoPin 12
#define max_dist 300

#define move_distance 8     // in inches
#define stop_distance 3     // in inches

MotorController motor(PWMA, AIN1, PWMB, BIN1, STBY);
UltrasonicSensor ultrasonic(trigPin, echoPin, max_dist);
OutputPrinter printer;
SerialCommandHandler serialHandler;

motorstate_t currentState = STOP;
unsigned long current_time = 0;
unsigned long ultrasonic_last_update = 0;
float distance_in = 0;

void setup() {
  Serial.begin(9600);
  motor.begin();
  ultrasonic.begin();
}

void loop() {
  current_time = millis();

  // Update distance every 50ms
  if (current_time - ultrasonic_last_update >= 50) {
    ultrasonic_last_update = current_time;
    float new_distance = ultrasonic.getDistanceInches();
    if (new_distance > 0) {
      distance_in = new_distance;
    }
  }

  // Serial command input
  motorstate_t newCommand;
  if (serialHandler.getCommand(newCommand)) {
    currentState = newCommand;
  }

  // Motor logic with auto-stop
  switch (currentState) {
    case FORWARD:
      if (distance_in > move_distance) {
        motor.forward();
      } else if (distance_in < stop_distance) {
        motor.stop();
      }
      break;

    case BACKWARD:
      if (distance_in > move_distance) {
        motor.backward();
      } else if (distance_in < stop_distance) {
        motor.stop();
      }
      break;

    case LEFT:
      motor.turnLeft();
      break;

    case RIGHT:
      motor.turnRight();
      break;

    case STOP:
    default:
      motor.stop();
      break;
  }

  // Print status
  Serial.print("in: ");
  Serial.print(distance_in, 1);
  Serial.print(" | MotorState: ");
  Serial.println(printer.motorStateToString(currentState));
}
