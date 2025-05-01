// -----Use the elegoo board and shield ---- //
unsigned long current_time = 0;
unsigned long print_update = 0;
unsigned long motor_lastupdate = 0;
unsigned long ultrasonic_last_update = 0;
unsigned long servo1_lastUpdate = 0;
unsigned long servo2_lastUpdate = 0;
// -------- Ultrasonic setup ------------- //
#include <NewPing.h>
#define echoPin 12
#define trigPin 13
#define max_dist 300 // max distance to measure in cm
#define move_distance 8
#define stop_distance 3
int distance_in = 0;
NewPing sonar(trigPin, echoPin, max_dist);

// ----------- Servo setup ------------- //
#include <Servo.h>
Servo servo1;
Servo servo2;
#define servo1_pin 10
#define servo2_pin 11
int servo1_angle = 0;
int servo2_angle = 0;


// --------Motor Setup ------------- //
#define PWMA 5    // Right motors speed
#define AIN1 7    // Right motors direction
#define PWMB 6    // Left motors speed
#define BIN1 8    // Left motors direction
#define STBY 3    // Standby control pin
enum motorstate_t { STOP, FORWARD, BACKWARD, LEFT, RIGHT };
motorstate_t currentmotorstate = STOP;

void setup()
{
  Serial.begin(9600);
  setupMotors();
  setupServo();
}

void loop() {
  current_time = millis();
  distance_in = read_us_sensor(); // Read Ultrasonic sensor and covert to inches
  printOutput(distance_in);           // print output of ultrasonic sensor
  serial_check();                     // Check the input of the serial port
  updateMotors();
}