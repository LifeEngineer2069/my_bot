import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'my_bot'

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
        )]), launch_arguments={'use_sim_time': 'false'}.items()
    )

    ldlidar = Node(
        package='ldlidar_stl_ros2',
        executable='ldlidar_stl_ros2_node',
        name='ldlidar_stl_ros2',
        output='screen',
        parameters=[
            {'product_name': 'LDLiDAR_STL19P'},
            {'topic_name': 'scan'},
            {'port_name': '/dev/ttyUSB0'},
            {'port_baudrate': 230400},
            {'frame_id': 'laser_frame'},
            {'laser_scan_dir': True},
            {'enable_angle_crop_func': False},
        ]
    )

    return LaunchDescription([rsp, ldlidar])
