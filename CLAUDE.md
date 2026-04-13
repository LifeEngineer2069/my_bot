# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Platform

| | |
|---|---|
| **Hardware** | Jetson Orin (ARM64, JetPack 6.1) |
| **OS** | Ubuntu 22.04 |
| **ROS** | ROS 2 Humble |
| **Simulator** | Ignition Gazebo 6 (Fortress) — NOT Gazebo classic |
| **Gazebo packages** | `ros_gz_*` (`ros_gz_sim`, `ros_gz_bridge`) — `ros-humble-gazebo-ros-pkgs` is NOT available on ARM64 Humble |

## Workspace Layout

The package lives directly at `dev_ws/my_bot/` (no `src/` subdirectory). All `colcon` commands run from `dev_ws/`.

```
dev_ws/
├── build/          # generated
├── install/        # generated
├── log/            # generated
└── my_bot/
    ├── description/   # URDF/XACRO robot model
    ├── launch/        # ROS 2 launch files
    ├── worlds/        # Ignition Gazebo SDF world files
    ├── config/        # controller YAML, RViz config, joystick config
    └── scripts/       # Python utility nodes
```

## Common Commands

```bash
cd ~/dev_ws

# Build (symlink-install = xacro/launch changes are live without rebuild)
colcon build --symlink-install
source install/setup.bash

# --- Simulation ---
ros2 launch my_bot launch_sim.launch.py                        # default world
ros2 launch my_bot launch_sim.launch.py world:=test_arena      # pick a world

# --- Real Robot ---
sudo chmod 666 /dev/ttyUSB0 /dev/ttyACM0
ros2 launch my_bot launch_robot.launch2.py

# --- Teleop (both modes) ---
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/diff_cont/cmd_vel_unstamped
ros2 launch my_bot joystick.launch.py

# --- Utilities ---
ros2 launch my_bot rsp.launch.py              # robot_state_publisher only
ros2 run joint_state_publisher_gui joint_state_publisher_gui
rviz2 -d $(ros2 pkg prefix my_bot)/share/my_bot/config/view_bot.rviz
```

## Hardware

| Component | Interface | Details |
|---|---|---|
| Drive | Arduino Nano on `/dev/ttyACM0` | `diffdrive_arduino` plugin, 57600 baud, open-loop PWM, no encoders |
| LiDAR | D500 (LDROBOT STL-19P) on `/dev/ttyUSB0` | `ldlidar_stl_ros2` driver, 230400 baud, frame: `laser_frame` |
| Camera | CSI (ArduCam IMX219) at `/dev/video0` | `gscam` node, v4l2src → videoconvert pipeline (nvvidconv cannot handle RG10 from v4l2), auto-launched in real robot mode |

## Architecture

**Description-only package** — no custom C++ nodes. All runtime behavior comes from standard ROS 2 tools configured via URDF/XACRO and launch files.

### Control Mode Switch

`robot.urdf.xacro` includes one of two control XACRO files based on the `use_ros2_control` argument. `rsp.launch.py` also passes `sim_mode` (= `use_sim_time`) to xacro to select the hardware plugin within `ros2_control.xacro`.

| | Simulation | Real Robot |
|---|---|---|
| `use_ros2_control` | `true` | `true` |
| `sim_mode` | `true` | `false` |
| XACRO included | `ros2_control.xacro` | `ros2_control.xacro` |
| Hardware plugin | `ign_ros2_control/IgnitionSystem` | `diffdrive_arduino/DiffDriveArduino` |
| cmd_vel topic | `/diff_cont/cmd_vel_unstamped` | `/diff_cont/cmd_vel_unstamped` |

`gazebo_control.xacro` (native Ignition DiffDrive plugin) is NOT used in normal operation. It exists as a fallback if `use_ros2_control:=false` is passed.

### Robot Model (`description/`)

- `robot.urdf.xacro` — root file; xacro args: `use_ros2_control` (default `true`), `sim_mode` (default `false`)
- `robot_core.xacro` — chassis geometry, 2 driven wheels (continuous joints), 4 fixed caster spheres. **Left wheel axis must be `xyz="0 0 -1"`** (not `0 0 1`) for correct DiffDrive direction in Ignition. Caster wheels use `mu=0` friction so the robot can spin in place.
- `inertial_macros.xacro` — reusable inertia tensor macros
- `ros2_control.xacro` — ros2_control hardware block; `sim_mode=false` → `diffdrive_arduino`, `sim_mode=true` → `ign_ros2_control/IgnitionSystem`. Also declares the Gazebo plugin `libign_ros2_control-system.so` (loaded by Ignition; ignored on real robot). Config files: `my_controller.yaml` + `gaz_ros2_ctl_use_sim.yaml`
- `gazebo_control.xacro` — native Ignition DiffDrive plugin (fallback, not normally used)
- `lidar.xacro` — Ignition `gpu_lidar` sensor. **Requires `<render_engine>ogre2</render_engine>` in the world's Sensors plugin** (ogre1 makes gpu_lidar publish all-inf). Uses `<gz_frame_id>laser_frame</gz_frame_id>` for correct ROS frame_id.
- `camera1.xacro` — camera model (sensor geometry + Ignition camera plugin)

### Launch Files (`launch/`)

**`launch_sim.launch.py`** — Full simulation in one command:
1. `rsp.launch.py` with `use_sim_time:=true`, `use_ros2_control:=true`
2. Ignition Gazebo with `--render-engine ogre` (required — OGRE2 crashes Jetson GUI with `NvMapMemAllocInternalTagged` error)
3. RViz (auto-launched)
4. `ros_gz_bridge` bridging `/clock`, `/cmd_vel`, `/odom`, `/scan`, `/camera`, `/camera_info`
5. Robot entity spawned after 3 s delay
6. `diff_cont` + `joint_broad` spawned after 10 s delay

**`launch_robot.launch2.py`** — Full real robot in one command:
1. `rsp.launch.py` with `use_ros2_control:=true` (sim_time defaults to false)
2. `ros2_control_node` (controller_manager) with `my_controller.yaml`
3. `diff_cont` + `joint_broad` spawned on controller_manager start
4. D500 LiDAR node (`ldlidar_stl_ros2`)
5. Camera node (`gscam` v4l2 pipeline)

**`rsp.launch.py`** — Robot state publisher only. Args: `use_sim_time` (default `false`), `use_ros2_control` (default `true`). Passes both to xacro as `use_ros2_control` and `sim_mode`.

**`joystick.launch.py`** — `joy_node` + `teleop_twist_joy`. Remaps `/cmd_vel` → `/diff_cont/cmd_vel_unstamped`. Config in `config/joystick.yaml` (enable button 6, turbo button 7).

**`launch_robot.launch.py`** — Legacy minimal launch (RSP + LiDAR only, no ros2_control). Not used in normal operation.

### Config (`config/`)

- `my_controller.yaml` — controller_manager update rate (30 Hz), `diff_cont` type + params (wheel sep: 0.184 m, radius: 0.0425 m, `use_stamped_vel: false`), `joint_broad` type
- `gaz_ros2_ctl_use_sim.yaml` — sets `use_sim_time: true` for controller_manager in sim
- `joystick.yaml` — joy + teleop_twist_joy parameters
- `view_bot.rviz` — RViz config
- `gazebo_params.yaml` — extra Gazebo node parameters

### Key ROS Topics / Frames

| Topic/Frame | Source | Purpose |
|---|---|---|
| `/robot_description` | robot_state_publisher | URDF string |
| `/diff_cont/cmd_vel_unstamped` | teleop / joystick | Drive commands (both sim and real) |
| `/diff_cont/odom` | diff_drive_controller | Wheel odometry |
| `/scan` | LiDAR driver / Gazebo bridge | Laser scan |
| `/camera` | gscam / Gazebo bridge | Camera image |
| `/clock` | Gazebo bridge (sim only) | Sim time |
| `base_link` | URDF | Robot base frame |
| `odom` | diff_drive_controller | Odometry reference frame |

### Worlds (`worlds/`)

Six SDF environments: `test_arena` (default), `empty`, `my_world`, `project_map1`, `project_map2`, `project_map3`.

Pass with `world:=<name>` to `launch_sim.launch.py`. Worlds need a Sensors system plugin with `<render_engine>ogre2</render_engine>` for gpu_lidar to work (see `lidar.xacro` note above).

## Ignition Fortress Gotchas

- Use `ros_gz_*` packages, never `gazebo_ros` — the latter is for Gazebo classic and is not available on this platform
- GUI launch requires `--render-engine ogre` (OGRE2 crashes with Jetson's EGL/NVMM driver)
- `gpu_lidar` needs ogre2 render engine in the **world SDF** Sensors plugin (server-side ogre2 is fine on Jetson — the crash is GUI-only)
- Do NOT use `<gazebo reference="..."><material>Gazebo/ColorName</material></gazebo>` — Ignition does not support Gazebo classic material names; use URDF `<material><color rgba="..."/>` instead
- Left wheel joint axis: `xyz="0 0 -1"` — using `0 0 1` swaps linear and angular commands
- Caster wheels: set friction `mu=0` or the robot cannot spin in place in Ignition
