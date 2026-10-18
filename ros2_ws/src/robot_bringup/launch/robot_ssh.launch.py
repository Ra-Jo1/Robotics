
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

        # Arm node
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

        # PS4 joystick driver
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            output='screen',
            parameters=[{'device_id': 0}]
        ),

        # PS4 joystick teleoperation
        Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_twist_joy',
            output='screen',
            parameters=[
                '/home/jo/Robotics/ros2_ws/src/robot_bringup/config/ps4_joy.yaml'
            ],
            remappings=[
                ('/cmd_vel', '/cmd_vel_raw')
            ]
        ),
    ])
