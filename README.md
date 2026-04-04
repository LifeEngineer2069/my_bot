## ROS Robot Package for Cyber Waster

---

## Cheat Sheet

### Build
Compile the package and make changes take effect.
```bash
cd ~/dev_ws
colcon build --symlink-install
source install/setup.bash
```

### Simulation
Launch Gazebo, spawn the robot, start the ROS-Gazebo bridge, and open RViz — all in one command.
```bash
ros2 launch my_bot launch_sim.launch.py

# Pick a world
ros2 launch my_bot launch_sim.launch.py world:=test_arena
ros2 launch my_bot launch_sim.launch.py world:=project_map1
ros2 launch my_bot launch_sim.launch.py world:=project_map2
ros2 launch my_bot launch_sim.launch.py world:=project_map3

#Control the Robot
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### Real Robot
Run on physical hardware with the D500 LiDAR connected via USB.
```bash
sudo chmod 666 /dev/ttyUSB0
ros2 launch my_bot launch_robot.launch.py
```

### Teleop
Drive the robot manually from the keyboard. Open RViz alongside to monitor the robot.
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# Open RViz with the robot config (works on any machine)
rviz2 -d $(ros2 pkg prefix my_bot)/share/my_bot/config/view_bot.rviz
```

### Debug
Useful one-off commands for checking individual parts of the system.
```bash
# Check lidar is publishing
ros2 topic echo /scan --field ranges --once

# Visualise robot model only (no sim)
ros2 launch my_bot rsp.launch.py use_sim_time:=true
ros2 run joint_state_publisher_gui joint_state_publisher_gui
rviz2 -d $(ros2 pkg prefix my_bot)/share/my_bot/config/view_bot.rviz
```

---

Worlds are in `my_bot/worlds/`.
