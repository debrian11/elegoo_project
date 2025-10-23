#include "OutputPrinter.h"
#include "UltraSonicSensor.h"
#include "MagMeter.h"
#include "Encoder.h"

unsigned long current_time;
unsigned long last_time_update = 0;
int json_print_interval = 50;
int encoder_interval = 50;
int heading = 0;

// Output
OutputPrinter serial_printer(json_print_interval);

// Ultrasonic sensors
UltrasonicSensor front_uss(9, 8);  // trig, echo
UltrasonicSensor left_uss(7, 6);
UltrasonicSensor right_uss(5, 4);

float front_distance_in = 0;
float left_distance_in = 0;
float right_distance_in = 0;

int updateDistance(UltrasonicSensor& sensor, float current_val) {
  int new_val = sensor.getDistanceInches();
  return (new_val > 0) ? new_val : current_val;
}

void setup() {
  Serial.begin(115200);
  delay(200);

  encoder_setup(3, 2);  // left on 3, right on 2

  // Mag setup
  if (!lsm.begin()) {
    Serial.println("Oops ... unable to initialize LSM9DS1. Check wiring!");
    while (1);
  }

  magmeter_setup();

  if (magmeter_load_offsets()) {
    Serial.print("X offset: "); Serial.print(x_offset);
    Serial.print(" Y offset: "); Serial.println(y_offset);
  } else {
    Serial.println("ERROR: No calibration in EEPROM. Please calibrate first.");
    while (1);
  }
}

void loop() {
  current_time = millis();

  if (current_time - last_time_update >= encoder_interval) {
    noInterrupts();
    unsigned long right_encoder_value = getRightEncoder();
    unsigned long left_encoder_value = getLeftEncoder();
    interrupts();

    heading = magmeter_get_heading();
    last_time_update = current_time;

    front_distance_in = updateDistance(front_uss, front_distance_in);
    left_distance_in  = updateDistance(left_uss,  left_distance_in);
    right_distance_in = updateDistance(right_uss, right_distance_in);

    serial_printer.json_print(front_distance_in, left_distance_in, right_distance_in,
                              left_encoder_value, right_encoder_value, heading,
                              current_time);
  }
}
