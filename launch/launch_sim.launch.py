import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node


def generate_launch_description():

    # !!! MAKE SURE YOU SET THE PACKAGE NAME CORRECTLY !!!
    package_name='my_bot' #<--- Robot Name

    world_file = os.path.join(get_package_share_directory(package_name), 'worlds', 'empty.sdf')

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Gazebo server — physics + sensors, headless (no window = no Jetson crash)
    gazebo_server = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
                launch_arguments={'gz_args': '-r -s ' + world_file}.items(),
             )

    # Spawn the robot entity using ros_gz_sim
    spawn_entity = Node(package='ros_gz_sim', executable='create',
                        arguments=['-name', 'my_bot',
                                   '-topic', 'robot_description'],
                        output='screen')

    # Bridge ROS 2 <-> Ignition topics (/tf is NOT bridged — odom_to_tf handles it)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
        ],
        output='screen'
    )

    # Publish odom -> base_link TF from /odom topic (avoids bridge latency/TF_OLD_DATA)
    odom_to_tf = Node(
        package='my_bot',
        executable='odom_to_tf.py',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # Launch them all!
    return LaunchDescription([
        rsp,
        gazebo_server,
        spawn_entity,
        bridge,
        odom_to_tf,
    ])