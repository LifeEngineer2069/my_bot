# SIMULATION launch — Ignition Gazebo + RViz + ros_gz_bridge
# use_ros2_control:=false → gazebo_control.xacro (Ignition native DiffDrive plugin)
# For real robot use: launch_robot.launch2.py

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, OpaqueFunction, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):

    package_name = 'my_bot'

    world_name = LaunchConfiguration('world').perform(context)
    world_file = os.path.join(
        get_package_share_directory(package_name), 'worlds', world_name + '.sdf'
    )

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true', 'use_ros2_control': 'true'}.items()
    )

    gazebo_params_file = os.path.join(get_package_share_directory(package_name), 'config', 'gazebo_params.yaml')

    # Single combined Gazebo process — ogre (not ogre2) avoids NvMapMemAlloc crash on Jetson
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
                launch_arguments={
                    'gz_args': '-r --render-engine ogre ' + world_file,
                    'extra_gazebo_args': '--ros-args --params-file ' + gazebo_params_file
                }.items()
             )

    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(get_package_share_directory(package_name), 'config', 'view_bot.rviz')],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # Spawn the robot entity
    spawn_entity = Node(package='ros_gz_sim', executable='create',
                        arguments=['-name', 'my_bot',
                                   '-topic', '/robot_description',
                                   '-x', '0.0', '-y', '0.0', '-z', '0.1'],
                        output='screen')

    # Bridge ROS 2 <-> Ignition topics
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/camera@sensor_msgs/msg/Image[ignition.msgs.Image',
            '/camera_info@sensor_msgs/msg/CameraInfo[ignition.msgs.CameraInfo',
        ],
        output='screen'
    )

    # odom_to_tf disabled — diff_cont (ros2_control) publishes odom TF directly
    # odom_to_tf = Node(
    #     package='my_bot',
    #     executable='odom_to_tf.py',
    #     parameters=[{'use_sim_time': True}],
    #     output='screen'
    # )

    # Delay spawn so world finishes loading first
    spawn_entity_delayed = TimerAction(period=3.0, actions=[spawn_entity])

    # gz_ros2_control loads+configures controllers from YAML — spawners just activate them
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

    diff_drive_spawner_delayed = TimerAction(period=10.0, actions=[diff_drive_spawner])
    joint_broad_spawner_delayed = TimerAction(period=10.0, actions=[joint_broad_spawner])

    return [
        rsp,
        gazebo,
        rviz,
        spawn_entity_delayed,
        bridge,
        diff_drive_spawner_delayed,
        joint_broad_spawner_delayed,
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value='test_arena',
            description='World to load (test_arena, empty, project_map1, project_map2, project_map3, my_world)'
        ),
        OpaqueFunction(function=launch_setup),
    ])
