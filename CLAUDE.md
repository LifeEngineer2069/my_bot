# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Workspace Layout

This is a ROS 2 workspace. The package lives at `dev_ws/src/my_bot/` and all `colcon` commands must be run from `dev_ws/`.

```
dev_ws/
├── build/        # generated
├── install/      # generated
├── log/          # generated
└── src/my_bot/
    ├── description/   # URDF/XACRO robot model
    ├── launch/        # ROS 2 launch files
    ├── worlds/        # Gazebo world SDF files
    └── config/        # RViz and misc config
```

## Common Commands

```bash
cd ~/dev_ws

# Build
colcon build --symlink-install

# Source the workspace after building
source install/setup.bash

# Run tests / linting
colcon test
colcon test --packages-select my_bot

# Launch robot state publisher only (no sim)
ros2 launch my_bot rsp.launch.py

# Launch full Gazebo simulation
ros2 launch my_bot launch_sim.launch.py

# Interactive joint control (for RViz visualization)
ros2 run joint_state_publisher_gui joint_state_publisher_gui
```

## Architecture

**This is a description-only package** — no custom C++ nodes or Python scripts. All runtime behavior comes from standard ROS 2 tools configured via URDF and launch files.

### Robot Model (`description/`)

The XACRO files compose into a single URDF:

- `robot.urdf.xacro` — root file, includes the others
- `robot_core.xacro` — chassis geometry + 2 driven wheels (left/right, continuous joints) + 4 fixed caster spheres
- `inertial_macros.xacro` — reusable macros for computing inertia tensors
- `gazebo_control.xacro` — configures the `libgazebo_ros_diff_drive` plugin (wheel sep: 0.184 m, max torque: 100 Nm, max vel: 10 m/s, publishes `/odom`)
- `lidar.xacro` — LIDAR sensor (incomplete/in progress)

### Launch Flow (`launch/`)

`launch_sim.launch.py` orchestrates:
1. Includes `rsp.launch.py` with `use_sim_time:=true`
2. Starts `robot_state_publisher` (reads URDF, publishes `/robot_description` and TF)
3. Starts Gazebo
4. Spawns robot entity from `/robot_description` topic

`rsp.launch.py` accepts `use_sim_time` argument (default `false` for hardware, `true` for sim).

### Key ROS Topics / Frames

| Topic/Frame | Source | Purpose |
|---|---|---|
| `/robot_description` | robot_state_publisher | URDF string |
| `/odom` | diff_drive plugin | Wheel odometry |
| `base_link` | URDF | Robot base frame |
| `odom` | diff_drive plugin | Odometry reference frame |

### Worlds (`worlds/`)

Three custom SDF environments: `project_map1.sdf`, `project_map2.sdf`, `project_map3.sdf`. To switch worlds, edit the world path argument in `launch_sim.launch.py`.
