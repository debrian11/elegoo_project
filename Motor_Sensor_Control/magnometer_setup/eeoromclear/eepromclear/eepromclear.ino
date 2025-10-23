#include <EEPROM.h>

void setup() {
  for (int i = 0; i < 32; i++) {
    EEPROM.write(i, 0);
  }
  Serial.begin(115200);
  Serial.println("EEPROM cleared.");
}

void loop() {}
