#!/bin/bash
# Cleanly restart all robot nodes

echo "Stopping all nodes..."
pkill -f "ros2 launch" 2>/dev/null
pkill -f "ros2 run" 2>/dev/null
sleep 3

echo "Building..."
cd ~/Robotics/ros2_ws
colcon build --packages-select robot_arm robot_bringup robot_navigation robot_perception
source install/setup.bash

echo "Launching..."
ros2 launch robot_bringup robot_ssh.launch.py
