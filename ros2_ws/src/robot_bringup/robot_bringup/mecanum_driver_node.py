#!/usr/bin/env python3
"""
mecanum_driver.py
Pont entre ROS 2 /cmd_vel et l'Arduino Mega via Serial USB.
Souscrit à /cmd_vel → envoie JSON à l'Arduino.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial
import json
import threading


class MecanumDriver(Node):
    def __init__(self):
        super().__init__('mecanum_driver')

        # Paramètres
        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('baudrate', 115200)

        port = self.get_parameter('port').value
        baudrate = self.get_parameter('baudrate').value

        # Connexion Serial
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            self.get_logger().info(f'Arduino connecté sur {port}')
        except Exception as e:
            self.get_logger().error(f'Erreur Serial : {e}')
            raise

        # Subscriber /cmd_vel
        self.sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        # Thread lecture Serial (réponses Arduino)
        self.running = True
        self.read_thread = threading.Thread(target=self.read_serial)
        self.read_thread.daemon = True
        self.read_thread.start()

        self.get_logger().info('MecanumDriver prêt — en attente de /cmd_vel')

    def cmd_vel_callback(self, msg: Twist):
        cmd = {
            'vx': round(msg.linear.x, 3),
            'vy': round(msg.linear.y, 3),
            'wz': round(msg.angular.z, 3),
        }
        line = json.dumps(cmd) + '\n'
        try:
            self.ser.write(line.encode())
        except Exception as e:
            self.get_logger().error(f'Erreur envoi Serial : {e}')

    def read_serial(self):
        # Lit les réponses de l'Arduino en continu
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
    node = MecanumDriver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
