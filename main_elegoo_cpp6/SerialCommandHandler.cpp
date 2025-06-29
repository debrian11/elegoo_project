#include "SerialCommandHandler.h"
#include <Arduino.h>
#include <ArduinoJson.h>
#include "Motorcontroller.h"

String arduino_input_buffer = "";  // Accumulate chars into a full JSON string
unsigned long last_pi_time = 0;
int SERVO_SWEEP_STATUS = 0;

bool SerialCommandHandler::getCommand_json(int &SERVO_SWEEP_STATUS) {

  if (Serial.available()) { 
    char c = Serial.read(); 

    if (c == '\n') { // wait until the end of the line before trying to parse the JSON
      StaticJsonDocument<200> pi_json_inc; // create json file called pi_json_inc where the parsed data will go
      DeserializationError error = deserializeJson(pi_json_inc, arduino_input_buffer); // ArduinoJson's function to turn raw text into a JSON object

      if (error) { // Need to send a json message back saying error.
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.f_str());
        arduino_input_buffer = "";  // Clear buffer
        return false;
      }

      // Grab the values from the Pi JSON:  { "L_DIR":0, "R_DIR":0, "L_PWM":50, "R_PWM":50 }
      int L_MTR_PWM = pi_json_inc["L_PWM"];
      int R_MTR_PWM = pi_json_inc["R_PWM"];
      int L_MTR_DIR = (pi_json_inc["L_DIR"] == 0) ? LOW : HIGH; // (condition) ? (value_if_true) : (value_if_false);
      int R_MTR_DIR = (pi_json_inc["R_DIR"] == 0) ? LOW : HIGH;
      
      SERVO_SWEEP_STATUS = pi_json_inc["S_SWEEP"];

      // === Apply motor control directly ===
      _motor_object.drive(L_MTR_PWM, R_MTR_PWM,
                          L_MTR_DIR, R_MTR_DIR);

      last_pi_time = millis();
      arduino_input_buffer = "";  // Clear after processing
      return true;
    } else {
      arduino_input_buffer += c;  // Keep accumulating the string until it is fully built message
    }
  }
  return false;  // Not done reading yet
}