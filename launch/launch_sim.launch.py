import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node


def generate_launch_description():

    # !!! MAKE SURE YOU SET THE PACKAGE NAME CORRECTLY !!!
    package_name='my_bot' #<--- Robot Name

    world_file = os.path.join(get_package_share_directory(package_name), 'worlds', 'my_world.sdf')

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Include the Gazebo launch file, provided by the ros_gz_sim package (Ignition Gazebo)
    # --render-engine ogre uses OGRE1 instead of OGRE2 (more compatible with Jetson)
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
                launch_arguments={'gz_args': '-r ' + world_file + ' --render-engine ogre'}.items(),
             )

    # Spawn the robot entity using ros_gz_sim
    spawn_entity = Node(package='ros_gz_sim', executable='create',
                        arguments=['-name', 'my_bot',
                                   '-topic', 'robot_description'],
                        output='screen')

    # Bridge ROS 2 <-> Ignition topics
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@ignition.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage@ignition.msgs.Pose_V',
            '/scan@sensor_msgs/msg/LaserScan@ignition.msgs.LaserScan',
        ],
        output='screen'
    )

    # Launch them all!
    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        bridge,
    ])
