/*
4/26/2025 Elegoo Code written for basic motor functionality example
*/

// TB6612 pin mappings based on Elegoo V4.0
#define PWMA 5    // Right motors speed
#define AIN1 7    // Right motors direction
#define PWMB 6    // Left motors speed
#define BIN1 8    // Left motors direction
#define STBY 3    // Standby control pin

void setup() {
  pinMode(PWMA, OUTPUT);
  pinMode(AIN1, OUTPUT);
  pinMode(PWMB, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(STBY, OUTPUT);

  digitalWrite(STBY, HIGH);  // Enable motors
  Serial.begin(9600);
}

void loop() {
  // Move forward
  digitalWrite(AIN1, HIGH);  // Right motors forward
  digitalWrite(BIN1, HIGH);  // Left motors forward
  analogWrite(PWMA, 100);    // Right speed
  analogWrite(PWMB, 100);    // Left speed
  Serial.println("FWD");
  delay(3000);

  // Stop
  analogWrite(PWMA, 0);
  analogWrite(PWMB, 0);
  delay(1000);

  // Move backward
  digitalWrite(AIN1, LOW);   // Right motors backward
  digitalWrite(BIN1, LOW);   // Left motors backward
  analogWrite(PWMA, 100);
  analogWrite(PWMB, 100);
    Serial.println("BWD");
  delay(3000);

  // Stop again
  analogWrite(PWMA, 0);
  analogWrite(PWMB, 0);
  delay(1000);
}
