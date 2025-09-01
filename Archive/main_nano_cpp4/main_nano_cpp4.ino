/*
  6/17/2025 Arduino Pi Mac Test script
  Purpose is to output the json message from the Arduino to the Pi to test from the Mac
  so that I don't need the motors or sensors hooked up to the Arduino.
  7/6/2025 Add actual encoders and just output the ticks on serial. Pi will handle the calculations
  Adding the gyroscope to the code
  7/8/2025 Send encoder data over json
  7/9/2025 Adding 2 Ultrasonics for left and right. Will eventually move the Elegoo ultrasonic over to it.
  7/12/2025 Adding the magnometer in.
*/
#include "OutputPrinter.h"
#include "UltraSonicSensor.h"
#include <Wire.h>
#include <Adafruit_LSM9DS1.h>
#include <Adafruit_Sensor.h>
#include <EEPROM.h>

unsigned long current_time;
unsigned long last_time_update = 0;
int json_print_interval = 50;
int encoder_interval = 50;

// IMU Variables ---------------------------------------------
Adafruit_LSM9DS1 lsm = Adafruit_LSM9DS1();
// EEPROM layout
#define EEPROM_FLAG_ADDR      0     // 1 byte
#define EEPROM_X_OFFSET_ADDR  1     // 4 bytes
#define EEPROM_Y_OFFSET_ADDR  5     // 4 bytes
float x_offset = 0;
float y_offset = 0;
float mag_interval = 50;
int heading = 0;

// nothing
void setupSensor() {
  lsm.setupAccel(lsm.LSM9DS1_ACCELRANGE_2G, lsm.LSM9DS1_ACCELDATARATE_10HZ);
  lsm.setupMag(lsm.LSM9DS1_MAGGAIN_4GAUSS);
  lsm.setupGyro(lsm.LSM9DS1_GYROSCALE_245DPS);
}

// int 1 | float x_offset | float y_offset
bool loadOffsetsFromEEPROM() {
  if (EEPROM.read(EEPROM_FLAG_ADDR) == 1) {
    EEPROM.get(EEPROM_X_OFFSET_ADDR, x_offset);
    EEPROM.get(EEPROM_Y_OFFSET_ADDR, y_offset);
    return true;
  } else {
    return false;
  }
}

OutputPrinter serial_printer(json_print_interval);  // Print every x-ms
UltrasonicSensor front_uss(9, 8); // trig, echo
UltrasonicSensor left_uss(7, 6);
UltrasonicSensor right_uss(5, 4);
float front_distance_in;
float left_distance_in;
float right_distance_in;
int updateDistance(UltrasonicSensor& sensor, float current_val) {
  int new_val = sensor.getDistanceInches();
  return (new_val > 0) ? new_val : current_val;}

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

  // Interrupts setup 
  pinMode(right_ISR_pin, INPUT_PULLUP);
  pinMode(left_ISR_pin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(right_ISR_pin), rightISR_count, FALLING);
  attachInterrupt(digitalPinToInterrupt(left_ISR_pin), leftISR_count, FALLING);

  // Mag Meter setup
  if (!lsm.begin()) {
    Serial.println("Oops ... unable to initialize LSM9DS1. Check wiring!");
    while (1);
  }

  setupSensor();

  if (loadOffsetsFromEEPROM()) {
    Serial.print("Using stored offsets: ");
    Serial.print("X: "); Serial.print(x_offset);
    Serial.print(" Y: "); Serial.println(y_offset);
  } else {
    Serial.println("ERROR: No calibration in EEPROM. Please calibrate first.");
    while (1); // Stop here — you need to run the calibration version first
  }
}

void loop() {
  current_time = millis();
  lsm.read();
  sensors_event_t a, m, g, temp;
  lsm.getEvent(NULL, &m, NULL, NULL);

  if (current_time - last_time_update >= encoder_interval) {
    noInterrupts();
    right_encoder_value = right_encoder_count;
    left_encoder_value = left_encoder_count;
    interrupts();
    float mx = m.magnetic.x;
    float my = m.magnetic.y;
    float x_cal = mx - x_offset;
    float y_cal = my - y_offset;
    heading = atan2(y_cal, x_cal) * 180 / PI;
    if (heading < 0)
      heading += 360;

    last_time_update = current_time;
  }

  // Front Ultrasonic Sensor
  front_distance_in = updateDistance(front_uss, front_distance_in);
  left_distance_in  = updateDistance(left_uss,  left_distance_in);
  right_distance_in = updateDistance(right_uss, right_distance_in);

  serial_printer.json_print(front_distance_in, left_distance_in, right_distance_in, 
                            left_encoder_value, right_encoder_value, heading, 
                            current_time);
  }
