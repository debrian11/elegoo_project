/*
  Use the elegoo board and shield
  1) Read input over serial for each different state:
    - "stop" | "L" | "R" | "F" "B"

  2) Ultrasonic sensor always running and outputing distance
*/
unsigned long current_time = 0;
unsigned long print_update;

// --------Ultrasonic setup ------------- //
#include <NewPing.h>
int echoPin = 13;
int trigPin = 12;
int max_dist = 300; // max distance to measure in cm
NewPing sonar(trigPin, echoPin, max_dist);
unsigned long ultrasonic_last_update = 0;

// --------Servo setup ------------- //
#include <Servo.h>
Servo servo1;
Servo servo2;
int servo1_pin = 10;
int servo2_pin = 11;
int servo1_angle = 0;
int servo2_angle = 0;
unsigned long servo1_lastUpdate = 0;
unsigned long servo2_lastUpdate = 0;

// --------LED and pot setup ------------- //
int potPin = A0; // Analog pin of pot
int potVal = 0; // Variable to store the input from the potentiometer
String pot_state = "";

// int redPin = 11;   // Red LED,   connected to digital pin 11
// int grnPin = 10;  // Green LED, connected to digital pin 10
// int bluPin = 9;  // Blue LED,  connected to digital pin 9

void setup()
{
  servo1.attach(servo1_pin); servo2.attach(servo2_pin);
  Serial.begin(9600); // Starts the serial communication
}

void loop() {
  current_time = millis();
  unsigned long print_interval = 50;  // update every 50 ms
  int distance_in = read_us_sensor();

  // potVal = analogRead(potPin);
  if (potVal < 341)  // Lowest third of the potentiometer's range (0-340)
  {
    stby_state(distance_in);                  
  }
  else if (potVal > 342 && potVal < 681) // Middle third of potentiometer's range (341-681)
  {
    state1(distance_in);   
  }
  else if (potVal > 682) // Upper third of potentiometer"s range (682-1023)
  {
    state2(distance_in);
  }
  else 
  {
    Serial.println("Invalid Pot val");
  }
}