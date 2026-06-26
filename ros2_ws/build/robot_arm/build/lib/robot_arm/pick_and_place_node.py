#!/usr/bin/env python3
"""
pick_and_place_node.py
Decision node: listens to YOLO detections and triggers
the arm to pick up small/light target objects.

Subscribes to : /detections (vision_msgs/Detection2DArray)
Publishes to  : /arm_command (std_msgs/String, JSON)

Logic:
  1. Filter detections by target classes (light objects)
  2. Pick the highest-confidence detection
  3. Compute horizontal position (left / center / right)
  4. Send a pick sequence to the arm via /arm_command
  5. Cooldown period to avoid repeated triggers
"""

import rclpy
from rclpy.node import Node
from vision_msgs.msg import Detection2DArray
from std_msgs.msg import String
import json
import time


# Light objects only (~under 200g) recognized by YOLO COCO classes
TARGET_CLASSES = ['bottle', 'cup', 'apple', 'orange', 'banana', 'cell phone']

# Minimum confidence to trigger a pick attempt
CONFIDENCE_THRESHOLD = 0.6

# Cooldown after a pick sequence (seconds) — avoids re-triggering immediately
PICK_COOLDOWN = 8.0

# Camera frame width (must match camera_node resolution)
FRAME_WIDTH = 320

# Horizontal zones (in pixels) — left / center / right
LEFT_ZONE_MAX = FRAME_WIDTH * 0.35
RIGHT_ZONE_MIN = FRAME_WIDTH * 0.65

# Arm servo angles for each zone — [s1, s2, s3, s4, s5]
# s1 = base rotation, s5 = gripper (20=open, 100=closed)
POSE_HOME = {"s1": 90, "s2": 90, "s3": 90, "s4": 90, "s5": 20}
POSE_APPROACH_L = {"s1": 60, "s2": 90, "s3": 30, "s4": 90, "s5": 20}
POSE_APPROACH_C = {"s1": 90, "s2": 90, "s3": 30, "s4": 90, "s5": 20}
POSE_APPROACH_R = {"s1": 120, "s2": 90, "s3": 30, "s4": 90, "s5": 20}
POSE_GRAB_OFFSET = {"s3": 10}     # lower toward object
GRIPPER_CLOSED = {"s5": 100}
GRIPPER_OPEN = {"s5": 20}


class PickAndPlaceNode(Node):
    def __init__(self):
        super().__init__('pick_and_place_node')

        self.declare_parameter('dry_run', False)
        self.dry_run = self.get_parameter('dry_run').value

        self.sub = self.create_subscription(
            Detection2DArray,
            '/detections',
            self.detection_callback,
            10
        )

        self.pub = self.create_publisher(String, '/arm_command', 10)

        self.busy = False
        self.last_pick_time = 0.0

        mode = "DRY RUN (no arm movement)" if self.dry_run else "LIVE"
        self.get_logger().info(
            f'PickAndPlaceNode ready — mode: {mode} — '
            f'targets: {TARGET_CLASSES}'
        )

    def detection_callback(self, msg: Detection2DArray):
        if self.busy:
            return

        now = time.time()
        if now - self.last_pick_time < PICK_COOLDOWN:
            return

        # Find the best matching detection
        best_detection = None
        best_score = 0.0

        for det in msg.detections:
            if not det.results:
                continue
            class_id = det.results[0].hypothesis.class_id
            score = det.results[0].hypothesis.score

            if class_id in TARGET_CLASSES and score > CONFIDENCE_THRESHOLD:
                if score > best_score:
                    best_score = score
                    best_detection = det

        if best_detection is None:
            return

        # Compute horizontal position in pixels
        center_x = best_detection.bbox.center.position.x
        class_id = best_detection.results[0].hypothesis.class_id

        zone = self.get_zone(center_x)

        self.get_logger().info(
            f'Target found: {class_id} ({best_score:.0%}) — '
            f'x={center_x:.0f}px — zone={zone}'
        )

        self.execute_pick_sequence(zone)

    def get_zone(self, center_x: float) -> str:
        if center_x < LEFT_ZONE_MAX:
            return 'left'
        elif center_x > RIGHT_ZONE_MIN:
            return 'right'
        else:
            return 'center'

    def execute_pick_sequence(self, zone: str):
        self.busy = True
        self.last_pick_time = time.time()

        # Select approach pose based on zone
        approach_pose = {
            'left': POSE_APPROACH_L,
            'center': POSE_APPROACH_C,
            'right': POSE_APPROACH_R,
        }[zone]

        sequence = [
            ("Open gripper", GRIPPER_OPEN),
            ("Move to approach", approach_pose),
            ("Lower toward object", {**approach_pose, **POSE_GRAB_OFFSET}),
            ("Close gripper", GRIPPER_CLOSED),
            ("Lift object", {**approach_pose, "s5": 100}),
            ("Return home", {**POSE_HOME, "s5": 100}),
        ]

        for step_name, pose in sequence:
            self.get_logger().info(f'  -> {step_name}: {pose}')
            if not self.dry_run:
                self.send_arm_command(pose)
                time.sleep(1.5)  # wait for smooth move to complete
            else:
                time.sleep(0.3)  # faster simulation in dry run

        self.get_logger().info('Pick sequence complete.')
        self.busy = False

    def send_arm_command(self, pose: dict):
        msg = String()
        msg.data = json.dumps(pose)
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = PickAndPlaceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
