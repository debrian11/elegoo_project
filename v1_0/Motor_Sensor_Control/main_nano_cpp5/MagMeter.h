#ifndef MAGMETER_H
#define MAGMETER_H

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_LSM9DS1.h>
#include <Adafruit_Sensor.h>
#include <EEPROM.h>

#define EEPROM_FLAG_ADDR      0
#define EEPROM_X_OFFSET_ADDR  1
#define EEPROM_Y_OFFSET_ADDR  5

// Only declare here
extern Adafruit_LSM9DS1 lsm;
extern float x_offset;
extern float y_offset;

void magmeter_setup();
bool magmeter_load_offsets();
float magmeter_get_heading();

#endif
