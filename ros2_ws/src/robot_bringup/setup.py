from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'robot_bringup'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Install launch files
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    entry_points={
	'console_scripts': [
   	    'mecanum_driver_node = robot_bringup.mecanum_driver_node:main',
   	    'obstacle_avoidance_node = robot_bringup.obstacle_avoidance_node:main',
        ],
    },
)
