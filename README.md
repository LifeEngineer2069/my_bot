## ROS Robot Package for Cyber Waster 


#start up commands to bring up axis locations and shape of robot
cd dev_ws

colcon build --symlink-install

ros2 launch my_bot rsp.launch.py

ros2 launch articubot_one rsp.launch.py

ros2 run joint_state_publisher_gui joint_state_publisher_gui

