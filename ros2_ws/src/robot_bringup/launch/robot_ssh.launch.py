from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([

        # Mecanum driver — wheels
        Node(
            package='robot_navigation',
            executable='mecanum_driver_node',
            name='mecanum_driver',
            output='screen',
            parameters=[{
                'port': '/dev/ttyACM0',
                'baudrate': 115200,
            }]
        ),

        # Obstacle avoidance
        Node(
            package='robot_navigation',
            executable='obstacle_avoidance_node',
            name='obstacle_avoidance_node',
            output='screen',
        ),

        # Arm node — only if /dev/ttyUSB0 exists
        Node(
            package='robot_arm',
            executable='arm_node',
            name='arm_node',
            output='screen',
            parameters=[{
                'port': '/dev/ttyUSB0',
                'baudrate': 9600,
            }]
        ),

        # Camera node
        Node(
            package='robot_perception',
            executable='camera_node',
            name='camera_node',
            output='screen',
        ),

        # YOLO node
        Node(
            package='robot_perception',
            executable='yolo_node',
            name='yolo_node',
            output='screen',
        ),

        # Pick and place
        Node(
            package='robot_arm',
            executable='pick_and_place_node',
            name='pick_and_place_node',
            output='screen',
            parameters=[{'dry_run': False}]
        ),

    ])
