# ROS Robot Package for Cyber Waster

---

## Sim vs Real Robot

| | Simulation | Real Robot |
|---|---|---|
| **Launch file** | `launch_sim.launch.py` | `launch_robot.launch2.py` |
| **Control plugin** | Ignition Gazebo DiffDrive (native) | `diffdrive_arduino` via ros2_control |
| **URDF loaded** | `gazebo_control.xacro` | `ros2_control.xacro` |
| **`use_ros2_control`** | `false` (set automatically) | `true` (set automatically) |
| **LiDAR** | Simulated in Gazebo | D500 on `/dev/ttyUSB0` |
| **RViz** | Auto-launched | Run manually |

The switch between modes is handled automatically by the launch files via the `use_ros2_control` arg in `description/robot.urdf.xacro`. You never need to change it manually.

---

## Setup
Install all dependencies on a fresh machine.
!Ensure my_bot file is in dev_ws folder
```bash
cd ~/dev_ws
bash ~/dev_ws/my_bot/setup.sh
colcon build --symlink-install
source install/setup.bash
```

---

## Build
Compile the package and make changes take effect.
```bash
cd ~/dev_ws
colcon build --symlink-install
source install/setup.bash
```

---

## Simulation
Launch Gazebo, spawn the robot, start the ROS-Gazebo bridge, and open RViz — all in one command.
```bash
# Default world (test_arena)
ros2 launch my_bot launch_sim.launch.py

# Pick a world
ros2 launch my_bot launch_sim.launch.py world:=test_arena
ros2 launch my_bot launch_sim.launch.py world:=empty
ros2 launch my_bot launch_sim.launch.py world:=my_world
ros2 launch my_bot launch_sim.launch.py world:=project_map1
ros2 launch my_bot launch_sim.launch.py world:=project_map2
ros2 launch my_bot launch_sim.launch.py world:=project_map3
```

---

## Real Robot

**Terminal 1 — robot core** (LiDAR + drive system + ros2_control)
```bash
sudo chmod 666 /dev/ttyUSB0 /dev/ttyACM0
ros2 launch my_bot launch_robot.launch2.py
```

**Terminal 2 — RViz**
```bash
rviz2 -d $(ros2 pkg prefix my_bot)/share/my_bot/config/view_bot.rviz
```

**Terminal 3 — drive** (pick one)
```bash
# Keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/diff_cont/cmd_vel_unstamped

# Gamepad (hold button 6 to enable, button 7 for turbo)
ros2 launch my_bot joystick.launch.py
```

**Terminal 4 — camera** (optional)
```bash
ros2 run rqt_image_view rqt_image_view
```

---

## Teleop
Drive the robot manually from the keyboard.
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/diff_cont/cmd_vel_unstamped
```

---

## Controller
Drive with a gamepad. Hold **button 6** to enable movement, **button 7** for turbo.
```bash
ros2 launch my_bot joystick.launch.py
```

---

## Camera
View the robot's camera feed.
```bash
ros2 run rqt_image_view rqt_image_view
```

---

## Debug
Useful one-off commands for checking individual parts of the system.
```bash
# Check input devices (joystick, gamepad, etc.)
evtest
jstest-gtk
jstest /dev/input/js0

# Check lidar is publishing
ros2 topic echo /scan --field ranges --once

# Visualise robot model only (no sim)
ros2 launch my_bot rsp.launch.py use_sim_time:=true
ros2 run joint_state_publisher_gui joint_state_publisher_gui
rviz2 -d $(ros2 pkg prefix my_bot)/share/my_bot/config/view_bot.rviz
```

---

Worlds are in `my_bot/worlds/`.
