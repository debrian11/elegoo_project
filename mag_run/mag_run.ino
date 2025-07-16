#include <Wire.h>
#include <Adafruit_LSM9DS1.h>
#include <Adafruit_Sensor.h>
#include <EEPROM.h>

Adafruit_LSM9DS1 lsm = Adafruit_LSM9DS1();

// EEPROM layout
#define EEPROM_FLAG_ADDR      0     // 1 byte
#define EEPROM_X_OFFSET_ADDR  1     // 4 bytes
#define EEPROM_Y_OFFSET_ADDR  5     // 4 bytes

float x_offset = 0;
float y_offset = 0;

void setupSensor() {
  lsm.setupAccel(lsm.LSM9DS1_ACCELRANGE_2G, lsm.LSM9DS1_ACCELDATARATE_10HZ);
  lsm.setupMag(lsm.LSM9DS1_MAGGAIN_4GAUSS);
  lsm.setupGyro(lsm.LSM9DS1_GYROSCALE_245DPS);
}

bool loadOffsetsFromEEPROM() {
  if (EEPROM.read(EEPROM_FLAG_ADDR) == 1) {
    EEPROM.get(EEPROM_X_OFFSET_ADDR, x_offset);
    EEPROM.get(EEPROM_Y_OFFSET_ADDR, y_offset);
    return true;
  } else {
    return false;
  }
}

void setup() {
  Wire.begin();
  Serial.begin(115200);
  while (!Serial);

  if (!lsm.begin()) {
    Serial.println("Oops ... unable to initialize LSM9DS1. Check wiring!");
    while (1);
  }
  Serial.println("LSM9DS1 found.");
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
  lsm.read();
  sensors_event_t a, m, g, temp;
  lsm.getEvent(NULL, &m, NULL, NULL);

  float mx = m.magnetic.x;
  float my = m.magnetic.y;

  float x_cal = mx - x_offset;
  float y_cal = my - y_offset;
  float heading = atan2(y_cal, x_cal) * 180 / PI;
  if (heading < 0)
    heading += 360;

  Serial.print("Heading: ");
  Serial.println(heading);

  delay(100);
}
