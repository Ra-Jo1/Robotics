from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess


def generate_launch_description():
    return LaunchDescription([

        # Camera node — captures webcam, publishes /camera/image_raw
        Node(
            package='robot_perception',
            executable='camera_node',
            name='camera_node',
            output='screen',
        ),

        # YOLO node — detects objects, publishes /detections
        Node(
            package='robot_perception',
            executable='yolo_node',
            name='yolo_node',
            output='screen',
        ),

        # Mecanum driver — bridges /cmd_vel to Arduino Mega (wheels)
        Node(
            package='robot_bringup',
            executable='mecanum_driver_node',
            name='mecanum_driver',
            output='screen',
            parameters=[{
                'port': '/dev/ttyACM0',
                'baudrate': 115200,
            }]
        ),

        # Arm node — bridges /arm_command to Arduino Adeept (arm)
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

        # Pick and place — decision brain
        Node(
            package='robot_arm',
            executable='pick_and_place_node',
            name='pick_and_place_node',
            output='screen',
            parameters=[{
                'dry_run': False,
            }]
        ),

        # Teleop keyboard — manual robot control
        Node(
            package='teleop_twist_keyboard',
            executable='teleop_twist_keyboard',
            name='teleop',
            output='screen',
            prefix='xterm -e',
            remappings=[('/cmd_vel', '/cmd_vel_raw')],
        ),

	# Obstacle avoidance — filters /cmd_vel_raw → /cmd_vel
	Node(
    	    package='robot_bringup',
    	    executable='obstacle_avoidance_node',
    	    name='obstacle_avoidance_node',
    	    output='screen',
	),

        # RViz2 — camera visual feed with YOLO annotations
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
        ),

    ])
