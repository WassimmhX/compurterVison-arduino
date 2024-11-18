const int ledPins[5] = {3, 5, 6, 9, 10};  // Update with your actual pin numbers

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < 5; i++) {
    pinMode(ledPins[i], OUTPUT);
  }
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    Serial.println(command);
    if (command.startsWith("BRIGHTNESS:")) {
      int brightness = command.substring(11).toInt();
      brightness = constrain(brightness, 0, 255);
      for (int i = 0; i < 5; i++) {
        analogWrite(ledPins[i], brightness);
      }
      Serial.print("Brightness Set: ");
      Serial.println(brightness);
    } 
    else if (command.startsWith("LED_STATE:")) {
      String states = command.substring(10);
      int ledStates[5];
      int i = 0;
      int value = 0;
      for (char c : states) {
        if (c == ',') {
          ledStates[i++] = value;
          value = 0;
        } else {
          value = value * 10 + (c - '0');
        }
      }
      ledStates[i] = value; // Last value
      for (int j = 0; j < 5; j++) {
        // Turn LEDs on or off based on received state
        if (ledStates[j] > 0) {
          analogWrite(ledPins[j], 255); // Fully on
        } else {
          analogWrite(ledPins[j], 0); // Off
        }
      }
      Serial.print("LED States: ");
      for (int j = 0; j < 5; j++) {
        Serial.print(ledStates[j]);
        if (j < 4) Serial.print(",");
      }
      Serial.println();
    }
  }
}