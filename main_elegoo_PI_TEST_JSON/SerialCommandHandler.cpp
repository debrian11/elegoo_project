#include "SerialCommandHandler.h"
#include <Arduino.h>
#include <ArduinoJson.h>  // Install ArduinoJson from Library Manager

String arduino_input_buffer = "";  // Accumulate chars into a full JSON string

bool SerialCommandHandler::getCommand_json(int &L_MTR_DIR, int &R_MTR_DIR, int &L_MTR_PWM, int &R_MTR_PWM) {
  if (Serial.available()) { // Only run this code if literally 1 byte is availbe on serial
    char c = Serial.read(); // Serial.read reads litearlly one byte or 1 character from serial.

    if (c == '\n') { // wait until the end of the line before trying to parse the JSON
      StaticJsonDocument<200> pi_json_inc; // create json file called pi_json_inc where the parsed data will go
      DeserializationError error = deserializeJson(pi_json_inc, arduino_input_buffer); // ArduinoJson's function to turn raw text into a JSON object
      // 1st variable in deserailzie is where you store the parsed JSON object.
      // 2nd variable is the raw JSOn text you want to prase
      // error is a vraiable that holds the result ofparsing, can be renamed to something else if need

      if (error) { // Need to send a json message back saying error. TBD
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.f_str());
        arduino_input_buffer = "";  // Clear buffer
        return false;
      }

      // Grab the values from the Pi JSON:  { "L_DIR": 0, "R_DIR": 0, "L_PWM":50, "R_PWM":50 }
      // Stop values:                       { "L_DIR": 1, "R_DIR": 1, "L_PWM": 0, "R_PWM": 0 }

      L_MTR_DIR = pi_json_inc["L_DIR"];
      R_MTR_DIR = pi_json_inc["R_DIR"];
      L_MTR_PWM = pi_json_inc["L_PWM"];
      R_MTR_PWM = pi_json_inc["R_PWM"];

      // Comment out this section for nontest purpose
      Serial.print(" | L Direction: ");
      Serial.print(L_MTR_DIR);
      Serial.print(" | R Direction: ");
      Serial.print(R_MTR_DIR);
      Serial.print(" | L_motor: ");
      Serial.print(L_MTR_PWM);
      Serial.print(" | R_motor: ");
      Serial.println(R_MTR_PWM);

      arduino_input_buffer = "";  // Clear after processing
      return true;
    } else {

      arduino_input_buffer += c;  // Keep accumulating the string until it is fully built message

    }
  }

  return false;  // Not done reading yet
}
