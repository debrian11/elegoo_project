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
bool calibrated = false;

float x_min = 9999, x_max = -9999;
float y_min = 9999, y_max = -9999;

unsigned long startTime;

void setupSensor() {
  lsm.setupAccel(lsm.LSM9DS1_ACCELRANGE_2G, lsm.LSM9DS1_ACCELDATARATE_10HZ);
  lsm.setupMag(lsm.LSM9DS1_MAGGAIN_4GAUSS);
  lsm.setupGyro(lsm.LSM9DS1_GYROSCALE_245DPS);
}

void saveOffsetsToEEPROM() {
  EEPROM.put(EEPROM_X_OFFSET_ADDR, x_offset);
  EEPROM.put(EEPROM_Y_OFFSET_ADDR, y_offset);
  EEPROM.write(EEPROM_FLAG_ADDR, 1);  // mark as valid
  Serial.println("✅ Calibration saved to EEPROM.");
}

void setup() {
  Serial.begin(115200);
  delay(1000); // Avoid being stuck on while (!Serial)

  if (!lsm.begin()) {
    Serial.println("LSM9DS1 not found. Check wiring.");
    while (1);
  }

  Serial.println("Running magnetometer calibration...");
  setupSensor();
  startTime = millis(); // begin calibration window
}

void loop() {
  lsm.read();
  sensors_event_t a, m, g, temp;
  lsm.getEvent(NULL, &m, NULL, NULL);

  float mx = m.magnetic.x;
  float my = m.magnetic.y;

  if (!calibrated) {
    if (mx < x_min) x_min = mx;
    if (mx > x_max) x_max = mx;
    if (my < y_min) y_min = my;
    if (my > y_max) y_max = my;

    float x_range = x_max - x_min;
    float y_range = y_max - y_min;
    unsigned long elapsed = millis() - startTime;

    Serial.print("mx: "); Serial.print(mx);
    Serial.print(" my: "); Serial.print(my);
    Serial.print(" | X Range: "); Serial.print(x_range);
    Serial.print(" Y Range: "); Serial.print(y_range);
    Serial.print(" | Time: "); Serial.print(elapsed / 1000.0);
    Serial.println(" sec");

    // Require good range AND at least 10 sec duration
    if ((x_range > 40 && y_range > 40) && elapsed > 20000) {
      x_offset = (x_max + x_min) / 2.0;
      y_offset = (y_max + y_min) / 2.0;
      saveOffsetsToEEPROM();
      calibrated = true;
    }
  }

  delay(200);
}
