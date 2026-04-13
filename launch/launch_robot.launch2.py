# REAL ROBOT launch — ros2_control + diffdrive_arduino + D500 LiDAR
# use_ros2_control:=true → ros2_control.xacro (Arduino hardware plugin)
# For simulation use: launch_sim.launch.py

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessStart

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command


def _check_device(path, label):
    if not os.path.exists(path):
        raise RuntimeError(
            f'\n\n'
            f'  DEVICE NOT FOUND: {path} ({label})\n'
            f'  Is the hardware plugged in?\n'
            f'  Fix: sudo chmod 666 /dev/ttyUSB0 /dev/ttyACM0\n'
        )
    if not os.access(path, os.R_OK | os.W_OK):
        raise RuntimeError(
            f'\n\n'
            f'  PERMISSION DENIED: {path} ({label})\n'
            f'  Fix: sudo chmod 666 /dev/ttyUSB0 /dev/ttyACM0\n'
        )


def launch_setup(context, *args, **kwargs):

    _check_device('/dev/ttyACM0', 'Arduino / drive controller')
    _check_device('/dev/ttyUSB0', 'D500 LiDAR')

    package_name = 'my_bot'

    pkg_path = get_package_share_directory(package_name)
    xacro_file = os.path.join(pkg_path, 'description', 'robot.urdf.xacro')
    controller_params_file = os.path.join(pkg_path, 'config', 'my_controller.yaml')

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            pkg_path, 'launch', 'rsp.launch.py'
        )]),
        launch_arguments={'use_ros2_control': 'true'}.items()
    )

    robot_description = ParameterValue(
        Command(['xacro ', xacro_file, ' use_ros2_control:=true sim_mode:=false']),
        value_type=str
    )

    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            {'robot_description': robot_description},
            controller_params_file
        ],
        output='screen'
    )

    delayed_controller_manager = TimerAction(period=3.0, actions=[controller_manager])

    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_cont'],
        output='screen'
    )

    joint_broad_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_broad'],
        output='screen'
    )

    delayed_diff_drive_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[diff_drive_spawner],
        )
    )

    delayed_joint_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[joint_broad_spawner],
        )
    )

    camera = Node(
        package='gscam',
        executable='gscam_node',
        name='camera',
        output='screen',
        parameters=[{
            'camera_name': 'camera',
            'frame_id': 'camera_link_optical',
            'gscam_config': (
                'nvarguscamerasrc sensor-id=0 ! '
                'video/x-raw(memory:NVMM),width=1280,height=720,framerate=15/1 ! '
                'nvvidconv ! '
                'queue max-size-buffers=1 leaky=2 ! '
                'videoconvert ! '
                'video/x-raw,format=RGB'
            ),
            'sync_sink': False,
        }],
        remappings=[
            ('camera/image_raw', '/camera'),
            ('camera/camera_info', '/camera_info'),
        ]
    )

    ldlidar = Node(
        package='ldlidar_stl_ros2',
        executable='ldlidar_stl_ros2_node',
        name='ldlidar',
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

    return [
        rsp,
        ldlidar,
        camera,
        delayed_controller_manager,
        delayed_diff_drive_spawner,
        delayed_joint_broad_spawner,
    ]


def generate_launch_description():
    return LaunchDescription([
        OpaqueFunction(function=launch_setup),
    ])
