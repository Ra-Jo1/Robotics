import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/jo/Documents/GitHub/Robotics/ros2_ws/install/robot_arm'
