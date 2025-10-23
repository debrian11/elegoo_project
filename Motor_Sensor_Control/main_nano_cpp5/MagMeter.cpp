#include "MagMeter.h"

// Define the globals ONCE here
Adafruit_LSM9DS1 lsm;
float x_offset = 0;
float y_offset = 0;

void magmeter_setup() {
  lsm.setupAccel(lsm.LSM9DS1_ACCELRANGE_2G, lsm.LSM9DS1_ACCELDATARATE_10HZ);
  lsm.setupMag(lsm.LSM9DS1_MAGGAIN_4GAUSS);
  lsm.setupGyro(lsm.LSM9DS1_GYROSCALE_245DPS);
}

bool magmeter_load_offsets() {
  if (EEPROM.read(EEPROM_FLAG_ADDR) == 1) {
    EEPROM.get(EEPROM_X_OFFSET_ADDR, x_offset);
    EEPROM.get(EEPROM_Y_OFFSET_ADDR, y_offset);
    return true;
  } else {
    return false;
  }
}

float magmeter_get_heading() {
  lsm.read();
  sensors_event_t a, m, g, temp;
  lsm.getEvent(NULL, &m, NULL, NULL);
  float mx = m.magnetic.x;
  float my = m.magnetic.y;
  float heading = atan2(my - y_offset, mx - x_offset) * 180.0 / PI;
  if (heading < 0) heading += 360;
  return heading;
}
