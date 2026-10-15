#!/usr/bin/env python3
"""
mecanum_driver_node.py
Bridge between ROS 2 /cmd_vel and Arduino Mega via Serial USB.
Also reads HC-SR04 distance and publishes on /distance topic.

Subscribes to : /cmd_vel (geometry_msgs/Twist)
Publishes to  : /distance (std_msgs/Float32)
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32
import serial
import json
import threading


class MecanumDriver(Node):
    def __init__(self):
        super().__init__('mecanum_driver')

        # Parameters
        self.declare_parameter('port',     '/dev/ttyACM0')
        self.declare_parameter('baudrate', 115200)

        port     = self.get_parameter('port').value
        baudrate = self.get_parameter('baudrate').value

        # Serial connection
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            self.get_logger().info(f'Arduino connected on {port}')
        except Exception as e:
            self.get_logger().error(f'Serial error: {e}')
            raise

        # /cmd_vel subscriber
        self.sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        # /distance publisher — HC-SR04 readings
        self.pub_distance = self.create_publisher(Float32, '/distance', 10)

        # Serial read thread
        self.running = True
        self.read_thread = threading.Thread(target=self.read_serial)
        self.read_thread.daemon = True
        self.read_thread.start()

        self.get_logger().info('MecanumDriver ready — waiting for /cmd_vel')

    def cmd_vel_callback(self, msg: Twist):
        cmd = {
            'vx': round(msg.linear.x,  3),
            'vy': round(msg.linear.y,  3),
            'wz': round(msg.angular.z, 3),
        }
        line = json.dumps(cmd) + '\n'
        try:
            self.ser.write(line.encode())
        except Exception as e:
            self.get_logger().error(f'Serial send error: {e}')

    def read_serial(self):
        # Continuously reads Arduino responses
        while self.running:
            try:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        # Publish distance if present
                        if 'dist' in data:
                            msg = Float32()
                            msg.data = float(data['dist'])
                            self.pub_distance.publish(msg)
                        else:
                            self.get_logger().info(f'Arduino: {line}')
                    except json.JSONDecodeError:
                        pass
            except Exception:
                pass

    def destroy_node(self):
        self.running = False
        self.ser.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MecanumDriver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
