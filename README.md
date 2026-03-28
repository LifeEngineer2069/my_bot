## ROS Robot Package for Cyber Waster 


#start up commands to bring up axis locations and shape of robot
cd dev_ws

colcon build --symlink-install

ros2 launch my_bot rsp.launch.py

ros2 launch my_bot rsp.launch.py

ros2 run joint_state_publisher_gui joint_state_publisher_gui


others
ros2 launch my_bot rsp.launch.py use_sim_time:=true
ros2 launch gazebo_ros gazebo.launch.py
ros2 run gazebo_ros spawn_entity.py -topic robot_description -entity cyberwaster


