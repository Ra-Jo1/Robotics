#!/usr/bin/env python3
import json
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import String

# Deadzone threshold — ignores small joystick drift
DEADZONE = 0.15


class ArmTeleop(Node):
    def __init__(self):
        super().__init__('arm_teleop_node')

        self.pub = self.create_publisher(String, '/arm_command', 10)
        self.sub = self.create_subscription(Joy, '/joy', self.joy_cb, 10)

        self.angles = {
            's1': 90, 's2': 90, 's3': 90,
            's4': 90, 's5': 20
        }
        self.axes        = []
        self.buttons     = []
        self.last_joy    = time.monotonic()
        self.last_sent   = None

        # Anti-bounce protection
        self.last_button_time = {}
        self.BUTTON_COOLDOWN  = 0.1   # 100ms between two presses

        self.create_timer(0.02, self.control)  # 50 Hz

    def joy_cb(self, msg):
        self.axes    = list(msg.axes)
        self.buttons = list(msg.buttons)
        self.last_joy = time.monotonic()

    def button(self, i):
        """Returns True only if button i is pressed and cooldown has passed."""
        if i >= len(self.buttons) or self.buttons[i] != 1:
            return False
        now = time.monotonic()
        if now - self.last_button_time.get(i, 0) < self.BUTTON_COOLDOWN:
            return False
        self.last_button_time[i] = now
        return True

    def axis(self, i):
        """Returns axis value with deadzone applied."""
        if i >= len(self.axes):
            return 0.0
        val = self.axes[i]
        return val if abs(val) > DEADZONE else 0.0

    def send(self):
        data = json.dumps(self.angles)
        if data != self.last_sent:
            msg = String()
            msg.data = data
            self.pub.publish(msg)
            self.last_sent = data

    def control(self):
        # Stop if no recent joy message
        if time.monotonic() - self.last_joy > 0.3:
            return

        # L2 must be held to activate arm control
        if len(self.buttons) <= 6 or self.buttons[6] != 1:
            return

        changed = False

        # D-pad horizontal → s1 (base)
        dx = self.axis(6)
        if dx < -0.5:
            self.angles['s1'] -= 2
            changed = True
        elif dx > 0.5:
            self.angles['s1'] += 2
            changed = True

        # D-pad vertical → s2 (shoulder)
        dy = self.axis(7)
        if dy < -0.5:
            self.angles['s2'] += 1
            changed = True
        elif dy > 0.5:
            self.angles['s2'] -= 1
            changed = True

        # Triangle (button 2) → s3 up | Cross (button 0) → s3 down
        if self.button(2):
            self.angles['s3'] += 2
            changed = True
        elif self.button(0):
            self.angles['s3'] -= 2
            changed = True

        # R1 (button 5) → s4 up | L1 (button 4) → s4 down
        if self.button(5):
            self.angles['s4'] += 3
            changed = True
        elif self.button(4):
            self.angles['s4'] -= 3
            changed = True

        # Square (button 3) → gripper close | Circle (button 1) → gripper open
        if self.button(3):
            self.angles['s5'] += 2
            changed = True
        elif self.button(1):
            self.angles['s5'] -= 2
            changed = True

        # Options (button 9) → home position
        if self.button(9):
            self.angles = {
                's1': 90, 's2': 90, 's3': 90,
                's4': 90, 's5': 20
            }
            changed = True
            
        # Enforce servo limits
        limits = {
            's1': (0,   180),
            's2': (0,   180),
            's3': (0,   180),
            's4': (0,   180),
            's5': (20,  100),
        }
        for servo, (lo, hi) in limits.items():
            self.angles[servo] = max(lo, min(hi, self.angles[servo]))

        if changed:
            self.send()


def main(args=None):
    rclpy.init(args=args)
    node = ArmTeleop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
