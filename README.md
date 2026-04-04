## ROS Robot Package for Cyber Waster 


#start up commands to bring up axis locations and shape of robot
cd dev_ws

colcon build --symlink-install

ros2 launch my_bot rsp.launch.py use_sim_time:=true

ros2 run joint_state_publisher_gui joint_state_publisher_gui

ros2 launch ros_gz_sim gz_sim.launch.py gz_args:="-r /home/ros/dev_ws/my_bot/worlds/my_world.sdf --render-engine ogre"

ros2 run teleop_twist_keyboard teleop_twist_keyboard

ros2 topic echo /scan --field ranges --once

# Real robot with D500 LiDAR (STL-19P)
sudo chmod 666 /dev/ttyUSB0
ros2 launch my_bot launch_robot.launch.py
