#!/usr/bin/env python3
"""
arm_node.py
Bridge between ROS 2 and Arduino (Adeept 5DOF arm) via Serial USB.
Subscribes to /arm_command (JSON string) -> sends JSON to Arduino.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial
import json
import threading


class ArmNode(Node):
    def __init__(self):
        super().__init__('arm_node')

        # Parameters
        self.declare_parameter('port',     '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 9600)

        port     = self.get_parameter('port').value
        baudrate = self.get_parameter('baudrate').value

        # Serial connection
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            self.get_logger().info(f'Arm Arduino connected on {port}')
        except Exception as e:
            self.get_logger().error(f'Serial error: {e}')
            raise

        # Subscriber — receives JSON commands as string
        self.sub = self.create_subscription(
            String,
            '/arm_command',
            self.command_callback,
            10
        )

        # Serial read thread (Arduino responses)
        self.running = True
        self.read_thread = threading.Thread(target=self.read_serial)
        self.read_thread.daemon = True
        self.read_thread.start()

        self.get_logger().info('ArmNode ready — waiting for /arm_command')

    def command_callback(self, msg: String):
        line = msg.data.strip() + '\n'
        try:
            self.ser.write(line.encode())
        except Exception as e:
            self.get_logger().error(f'Serial send error: {e}')

    def read_serial(self):
        while self.running:
            try:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode().strip()
                    if line:
                        self.get_logger().info(f'Arduino: {line}')
            except Exception:
                pass

    def destroy_node(self):
        self.running = False
        self.ser.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ArmNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()