/*
  Use the elegoo board and shield
*/
unsigned long current_time = 0;
unsigned long print_update;
// --------Ultrasonic setup ------------- //
#include <NewPing.h>
#define echoPin 12
#define trigPin 13
#define max_dist 300 // max distance to measure in cm
NewPing sonar(trigPin, echoPin, max_dist);
unsigned long ultrasonic_last_update = 0;

// --------Servo setup ------------- //
#include <Servo.h>
Servo servo1;
Servo servo2;
#define servo1_pin 10
#define servo2_pin 11
int servo1_angle = 0;
int servo2_angle = 0;
unsigned long servo1_lastUpdate = 0;
unsigned long servo2_lastUpdate = 0;

// --------Motor Setup ------------- //
#define PWMA 5    // Right motors speed
#define AIN1 7    // Right motors direction
#define PWMB 6    // Left motors speed
#define BIN1 8    // Left motors direction
#define STBY 3    // Standby control pin
enum motorstate_t { STOP, FORWARD, BACKWARD };
motorstate_t currentmotorstate = STOP;



void setup()
{
  Serial.begin(9600);
  setupMotors();
  setupServo();
}

/*
void loop() {
  current_time = millis();
  // unsigned long print_interval = 50;  // update every 50 ms
  int distance_in = read_us_sensor();
  printOutput(distance_in);
*/

void loop() {
    current_time = millis();
    int distance_in = read_us_sensor(); // Read Ultrasonic sensor and covert to inches
    printOutput(distance_in); // print output of ultrasonic sensor

  // 1. Serial check
  if (Serial.available() > 0) {
      String serial_input = Serial.readStringUntil('\n');
      serial_input.trim();

      if (serial_input == "F") {
          currentmotorstate = FORWARD;
      } else if (serial_input == "B") {
          currentmotorstate = BACKWARD;
      } else if (serial_input == "stop") {
          currentmotorstate = STOP;
      }
  }

  // 2. State Machine
  switch(currentmotorstate) {
      case FORWARD:
          move_fwd();
          break;
      case BACKWARD:
          move_back();
          break;
      case STOP:
      default:
          stop_motors();
          break;
  }
}