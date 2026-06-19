/**
 * arm_controller.ino
 * Adeept 5DOF Robotic Arm — ROS 2 compatible firmware
 * Board: Arduino UNO R3 (Adeept Driver Board ATmega328P)
 *
 * Serial JSON command format:
 *   {"s1":90, "s2":90, "s3":10, "s4":90, "s5":20}
 *
 * Servo mapping:
 *   s1 → pin 9  — Base rotation
 *   s2 → pin 6  — Shoulder
 *   s3 → pin 5  — Elbow
 *   s4 → pin 3  — Wrist
 *   s5 → pin 11 — Gripper (20=open, 100=closed)
 */

#include <Servo.h>

// =====================
// SERVO PINS
// =====================
#define PIN_S1  9    // Base
#define PIN_S2  6    // Shoulder
#define PIN_S3  5    // Elbow
#define PIN_S4  3    // Wrist
#define PIN_S5  11   // Gripper

// =====================
// ANGLE LIMITS (safety)
// =====================
const int LIMITS[5][2] = {
  {0,   180},  // s1 base
  {0,   180},  // s2 shoulder
  {0,   180},  // s3 elbow
  {0,   180},  // s4 wrist
  {20,  100}   // s5 gripper
};

// =====================
// HOME POSITION
// =====================
const int HOME[5] = {90, 90, 90, 90, 20};

// =====================
// SERVOS
// =====================
Servo servos[5];
int   current_angles[5] = {90, 90, 90, 90, 20};
const int SERVO_PINS[5] = {PIN_S1, PIN_S2, PIN_S3, PIN_S4, PIN_S5};

// =====================
// SERIAL
// =====================
#define BAUD_RATE   9600
#define SMOOTH_STEP 15   // ms per degree (smoothMove speed)

String serial_buffer = "";

// =====================
// SETUP
// =====================
void setup() {
  // Attach all servos
  for (int i = 0; i < 5; i++) {
    servos[i].attach(SERVO_PINS[i]);
  }

  // Move to home position smoothly at startup
  goHome();

  Serial.begin(BAUD_RATE);
  Serial.println("{\"status\":\"ready\", \"robot\":\"Adeept 5DOF\"}");
}

// =====================
// LOOP
// =====================
void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      parseCommand(serial_buffer);
      serial_buffer = "";
    } else {
      serial_buffer += c;
    }
  }
}

// =====================
// PARSE JSON
// =====================
void parseCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) return;

  // Home command: {"home":1}
  if (cmd.indexOf("\"home\"") != -1) {
    goHome();
    Serial.println("{\"status\":\"home\"}");
    return;
  }

  // Read target angles
  int targets[5];
  String keys[] = {"s1", "s2", "s3", "s4", "s5"};

  for (int i = 0; i < 5; i++) {
    int val = extractInt(cmd, keys[i]);
    // If key not found, keep current angle
    targets[i] = (val == -1) ? current_angles[i] : val;
    // Apply safety limits
    targets[i] = constrain(targets[i], LIMITS[i][0], LIMITS[i][1]);
  }

  // Move all servos smoothly
  moveSmoothAll(targets);

  // Confirm
  Serial.print("{\"s1\":"); Serial.print(current_angles[0]);
  Serial.print(",\"s2\":"); Serial.print(current_angles[1]);
  Serial.print(",\"s3\":"); Serial.print(current_angles[2]);
  Serial.print(",\"s4\":"); Serial.print(current_angles[3]);
  Serial.print(",\"s5\":"); Serial.print(current_angles[4]);
  Serial.println("}");
}

// =====================
// SMOOTH MOVE ALL
// =====================
void moveSmoothAll(int targets[]) {
  bool done = false;
  while (!done) {
    done = true;
    for (int i = 0; i < 5; i++) {
      if (current_angles[i] < targets[i]) {
        current_angles[i]++;
        servos[i].write(current_angles[i]);
        done = false;
      } else if (current_angles[i] > targets[i]) {
        current_angles[i]--;
        servos[i].write(current_angles[i]);
        done = false;
      }
    }
    delay(SMOOTH_STEP);
  }
}

// =====================
// GO HOME
// =====================
void goHome() {
  moveSmoothAll((int*)HOME);
  for (int i = 0; i < 5; i++) {
    current_angles[i] = HOME[i];
  }
}

// =====================
// EXTRACT INT FROM JSON
// =====================
int extractInt(String json, String key) {
  String search = "\"" + key + "\":";
  int idx = json.indexOf(search);
  if (idx == -1) return -1;
  idx += search.length();
  int end = json.indexOf(",", idx);
  if (end == -1) end = json.indexOf("}", idx);
  return json.substring(idx, end).toInt();
}