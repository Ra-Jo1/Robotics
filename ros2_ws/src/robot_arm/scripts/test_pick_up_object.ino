// Watch videos test 6_robot_arm_pick_up_object in Videos and pictures for the result
#include <Servo.h>

int servopin1 = 9;
int servopin2 = 6;
int servopin3 = 5;
int servopin4 = 3;
int servopin5 = 11;

Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
Servo servo5;

int angle1 = 90;
int angle2 = 90;
int angle3 = 10;
int angle4 = 90;
int angle5 = 20;   // Pince ouverte
int angle6 = 100;   // Pince fermée

int d1 = 1200;

// Smooth move function: moves a servo gradually from fromAngle to toAngle
void smoothMove(Servo &servo, int fromAngle, int toAngle, int stepDelay) {
  if (fromAngle < toAngle) {
    for (int pos = fromAngle; pos <= toAngle; pos++) {
      servo.write(pos);
      delay(stepDelay);
    }
  } else {
    for (int pos = fromAngle; pos >= toAngle; pos--) {
      servo.write(pos);
      delay(stepDelay);
    }
  }
}

void setup() {
  pinMode(servopin1, OUTPUT);
  pinMode(servopin2, OUTPUT);
  pinMode(servopin3, OUTPUT);
  pinMode(servopin4, OUTPUT);
  pinMode(servopin5, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // Servo 5 (pince) - ouverte dès le début
  servo5.attach(servopin5);
  servo5.write(angle5);  // Pince ouverte à 20°
  delay(d1);

  // Servo 1
  servo1.attach(servopin1);
  servo1.write(angle1);
  delay(d1);

  // Servo 2
  servo2.attach(servopin2);
  servo2.write(angle2);
  delay(d1);

  // Servo 3 - smooth
  servo3.attach(servopin3);
  smoothMove(servo3, 90, angle3, 15);
  delay(d1);

  // Servo 4
  servo4.attach(servopin4);
  servo4.write(angle4);
  delay(d1);

  // Fermeture de la pince
  servo5.write(angle6);  // Pince fermée à 90°
  delay(d1);

  // Suite des mouvements après fermeture pince
  smoothMove(servo3, angle3, angle1, 15);
  delay(d1);

  // Maintien du signal sur tous les servos pour éviter le relâchement
  while(true) {
    servo5.write(angle6);  // Pince reste fermée
    delay(100);
  }
}
