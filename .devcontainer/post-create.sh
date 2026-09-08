#!/usr/bin/env bash
set -euo pipefail
cd /workspace/Ros2Sample
set +u
source "/opt/ros/${ROS_DISTRO:?ROS_DISTRO must be set}/setup.bash"
set -u
bash scripts/rosdep-install.sh "$ROS_DISTRO"
bash scripts/build.sh
