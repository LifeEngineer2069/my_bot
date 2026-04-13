# ROS Robot Package for Cyber Waster

---

## Sim vs Real Robot

| | Simulation | Real Robot |
|---|---|---|
| **Launch file** | `launch_sim.launch.py` | `launch_robot.launch2.py` |
| **Control plugin** | `gz_ros2_control` (Gazebo hardware) | `diffdrive_arduino` via ros2_control |
| **URDF loaded** | `ros2_control.xacro` (`sim_mode:=true`) | `ros2_control.xacro` |
| **`use_ros2_control`** | `true` (set automatically) | `true` (set automatically) |
| **LiDAR** | Simulated in Gazebo | D500 on `/dev/ttyUSB0` |
| **Camera** | Simulated in Gazebo | gscam auto-launched (`/dev/video0`) |
| **RViz** | Auto-launched | Run manually |

Both modes use ros2_control. The hardware plugin differs: simulation uses `gz_ros2_control` (Gazebo hardware interface); real robot uses `diffdrive_arduino` (Arduino serial). The correct plugin is selected automatically via `use_ros2_control:=true` and `sim_mode` (derived from `use_sim_time`) passed to xacro — you never need to change this manually.

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

## Simulation

**Terminal 1 — sim core** (Gazebo + RViz + bridge + controllers — all in one)
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

**Terminal 2 — drive** (pick one)
```bash
# Keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/diff_cont/cmd_vel_unstamped

# Gamepad (hold button 6 to enable, button 7 for turbo)
ros2 launch my_bot joystick.launch.py
```

---

## Real Robot

**Terminal 1 — robot core** (LiDAR + drive system + ros2_control + camera)
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

**Terminal 4 — camera viewer** (optional, camera node is auto-launched in Terminal 1)
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
View the robot's camera feed (camera node auto-starts with `launch_robot.launch2.py`).
```bash
ros2 run rqt_image_view rqt_image_view
```

Test the raw GStreamer pipeline directly (bypass ROS):
```bash
# Hardware ISP pipeline - uses nvarguscamerasrc (JetPack 6.1)
gst-launch-1.0 nvarguscamerasrc sensor-id=0 ! \
  'video/x-raw(memory:NVMM),width=1280,height=720,framerate=15/1' ! \
  nvvidconv ! videoconvert ! autovideosink

# List available formats
v4l2-ctl --list-formats-ext -d /dev/video0
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

#cam
gst-launch-1.0 nvarguscamerasrc sensor-id=0 ! 'video/x-raw(memory:NVMM),width=1280,height=720,framerate=15/1' ! nvvidconv ! videoconvert ! autovideosink



```

---

Worlds are in `my_bot/worlds/`.
