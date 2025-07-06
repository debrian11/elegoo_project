/*
  6/17/2025 Arduino Pi Mac Test script
  Purpose is to output the json message from the Arduino to the Pi to test from the Mac
  so that I don't need the motors or sensors hooked up to the Arduino.
  7/6/2025 Add actual encoders and just output the ticks on serial. Pi will handle the calculations
  Adding the gyroscope to the code
*/
#include "OutputPrinter.h"
#include <Adafruit_ISM330DHCX.h>

// IMU Variables
Adafruit_ISM330DHCX IMU_sensor; // Created IMU Object

// Encoder variables
volatile unsigned long right_encoder_count = 0;
volatile unsigned long left_encoder_count = 0;
unsigned long right_encoder_value = 0;
unsigned long left_encoder_value = 0;
int right_ISR_pin = 2;
int left_ISR_pin = 3;


unsigned long current_time;
unsigned long last_time_update = 0;
int json_print_interval = 50;
int encoder_interval = 50;
//OutputPrinter serial_printer(json_print_interval);  // Print every x-ms

void rightISR_count() {right_encoder_count++;}

void leftISR_count() {left_encoder_count++;}

void setup() {
  Serial.begin(115200);

  pinMode(right_ISR_pin, INPUT_PULLUP);
  pinMode(left_ISR_pin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(right_ISR_pin), rightISR_count, FALLING);
  attachInterrupt(digitalPinToInterrupt(left_ISR_pin), leftISR_count, FALLING);

  if (!IMU_sensor.begin_I2C()) {
    Serial.println("IMU not found");
    while (1);
  }

}

void loop() {
  current_time = millis();
  sensors_event_t accel, gyro, temp; // Must get all 3 sensors then feed it in getEvent
  IMU_sensor.getEvent(&accel, &gyro, &temp);

  if (current_time - last_time_update >= encoder_interval) {
    noInterrupts();
    right_encoder_value = right_encoder_count;
    left_encoder_value = left_encoder_count;
    interrupts();
    last_time_update = current_time;
  }
    Serial.print("Right = "); Serial.print(right_encoder_value);
    Serial.print(" | Left = "); Serial.print(left_encoder_value);
    Serial.print(" | Z rad/s = "); Serial.println(gyro.gyro.z);
    delay(100);

  //serial_printer.json_print(left_encoder, right_encoder, current_time);
}
