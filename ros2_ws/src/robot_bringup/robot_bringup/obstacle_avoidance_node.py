#!/usr/bin/env python3
"""
obstacle_avoidance_node.py
Reads /distance from HC-SR04 and modifies /cmd_vel to avoid obstacles.

Subscribes to : /distance     (std_msgs/Float32)
               /cmd_vel_raw   (geometry_msgs/Twist) — teleop input
Publishes to  : /cmd_vel      (geometry_msgs/Twist) — filtered output
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist


# Distance threshold in cm — stop if obstacle closer than this
STOP_DISTANCE    = 25.0
WARNING_DISTANCE = 40.0


class ObstacleAvoidanceNode(Node):
    def __init__(self):
        super().__init__('obstacle_avoidance_node')

        self.current_distance = 999.0  # Default — no obstacle

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

        self.get_logger().info(
            f'ObstacleAvoidanceNode ready — '
            f'stop threshold: {STOP_DISTANCE}cm'
        )

    def distance_callback(self, msg: Float32):
        self.current_distance = msg.data

        if self.current_distance < STOP_DISTANCE:
            self.get_logger().warn(
                f'Obstacle detected at {self.current_distance:.1f}cm — STOP!'
            )
        elif self.current_distance < WARNING_DISTANCE:
            self.get_logger().info(
                f'Obstacle approaching: {self.current_distance:.1f}cm'
            )

    def teleop_callback(self, msg: Twist):
        filtered = Twist()

        # Block forward movement if obstacle too close
        if (self.current_distance < STOP_DISTANCE and msg.linear.x > 0):
            self.get_logger().warn(
                f'Forward blocked — obstacle at {self.current_distance:.1f}cm'
            )
            filtered.linear.x  = 0.0
            filtered.linear.y  = msg.linear.y   # Allow lateral movement
            filtered.angular.z = msg.angular.z  # Allow rotation
        else:
            filtered = msg  # Pass through normally

        self.pub_cmd.publish(filtered)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidanceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
