/*
  6/17/2025 Arduino Pi Mac Test script
  Purpose is to output the json message from the Arduino to the Pi to test from the Mac
  so that I don't need the motors or sensors hooked up to the Arduino.
  7/6/2025 Add actual encoders and just output the ticks on serial. Pi will handle the calculations
  Adding the gyroscope to the code
  7/8/2025 Send encoder data over json
  7/9/2025 Adding 2 Ultrasonics for left and right. Will eventually move the Elegoo ultrasonic over to it.
*/
#include "OutputPrinter.h"
#include <Adafruit_ISM330DHCX.h>
#include "UltraSonicSensor.h"

unsigned long current_time;
unsigned long last_time_update = 0;
int json_print_interval = 50;
int encoder_interval = 50;

// IMU Variables
Adafruit_ISM330DHCX IMU_sensor; // Created IMU Object
OutputPrinter serial_printer(json_print_interval);  // Print every x-ms
UltrasonicSensor front_uss(9, 8); // trig, echo
UltrasonicSensor left_uss(7, 6);
UltrasonicSensor right_uss(5, 4);
float front_distance_in;
float left_distance_in;
float right_distance_in;

// Encoder variables
volatile unsigned long right_encoder_count = 0;
volatile unsigned long left_encoder_count = 0;
unsigned long right_encoder_value = 0;
unsigned long left_encoder_value = 0;
int right_ISR_pin = 2;
int left_ISR_pin = 3;

void rightISR_count() {right_encoder_count++;}
void leftISR_count() {left_encoder_count++;}

void setup() {
  Serial.begin(115200);

  pinMode(right_ISR_pin, INPUT_PULLUP);
  pinMode(left_ISR_pin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(right_ISR_pin), rightISR_count, FALLING);
  attachInterrupt(digitalPinToInterrupt(left_ISR_pin), leftISR_count, FALLING);
}

void loop() {
  current_time = millis();
  //sensors_event_t accel, gyro, temp; // Must get all 3 sensors then feed it in getEvent
  //IMU_sensor.getEvent(&accel, &gyro, &temp);

  if (current_time - last_time_update >= encoder_interval) {
    noInterrupts();
    right_encoder_value = right_encoder_count;
    left_encoder_value = left_encoder_count;
    interrupts();
    last_time_update = current_time;
  }

  // Front Ultrasonic Sensor
  float front_new_distance = front_uss.getDistanceInches();
  if (front_new_distance > 0) {
    front_distance_in = front_new_distance;
  }

  // Left Ultrasonic Sensor
  float left_new_distance = left_uss.getDistanceInches();
  if (left_new_distance > 0) {
    left_distance_in = left_new_distance;
  }
  
  // Left Ultrasonic Sensor
  float right_new_distance = right_uss.getDistanceInches();
  if (right_new_distance > 0) {
    right_distance_in = right_new_distance;
  }

  serial_printer.json_print(front_distance_in, left_distance_in, right_distance_in, 
                            left_encoder_value, right_encoder_value, current_time); }
