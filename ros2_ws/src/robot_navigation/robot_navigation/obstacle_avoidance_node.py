#!/usr/bin/env python3
"""
obstacle_avoidance_node.py
Reads /distance from HC-SR04 and blocks forward movement when obstacle detected.

Subscribes to : /distance     (std_msgs/Float32)
               /cmd_vel_raw   (geometry_msgs/Twist) — teleop input
Publishes to  : /cmd_vel      (geometry_msgs/Twist) — filtered output
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist


# Distance thresholds in cm
STOP_DISTANCE    = 25.0
WARNING_DISTANCE = 40.0


class ObstacleAvoidanceNode(Node):
    def __init__(self):
        super().__init__('obstacle_avoidance_node')

        self.current_distance = 999.0
        self.blocked = False

        # Subscribe to raw teleop commands
        self.sub_teleop = self.create_subscription(
            Twist,
            '/cmd_vel_raw',
            self.teleop_callback,
            10
        )

        # Subscribe to HC-SR04 distance
        self.sub_distance = self.create_subscription(
            Float32,
            '/distance',
            self.distance_callback,
            10
        )

        # Publish filtered cmd_vel
        self.pub_cmd = self.create_publisher(Twist, '/cmd_vel', 10)

        # Timer — actively publishes stop at 20Hz when obstacle detected
        self.timer = self.create_timer(0.05, self.safety_timer_callback)

        self.get_logger().info(
            f'ObstacleAvoidanceNode ready — '
            f'stop threshold: {STOP_DISTANCE}cm'
        )

    def distance_callback(self, msg: Float32):
        self.current_distance = msg.data
        self.blocked = self.current_distance < STOP_DISTANCE

        if self.blocked:
            self.get_logger().warn(
                f'OBSTACLE at {self.current_distance:.1f}cm — BLOCKED!',
                throttle_duration_sec=1.0
            )
        elif self.current_distance < WARNING_DISTANCE:
            self.get_logger().info(
                f'Obstacle approaching: {self.current_distance:.1f}cm',
                throttle_duration_sec=2.0
            )

    def safety_timer_callback(self):
        # Actively publish stop at 20Hz when blocked — overrides teleop
        if self.blocked:
            self.pub_cmd.publish(Twist())

    def teleop_callback(self, msg: Twist):
        # If blocked and trying to go forward — block it
        if self.blocked and msg.linear.x > 0:
            stopped = Twist()
            stopped.linear.y  = msg.linear.y    # Allow lateral movement
            stopped.angular.z = msg.angular.z   # Allow rotation
            self.pub_cmd.publish(stopped)
        else:
            # Pass through normally
            self.pub_cmd.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidanceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
