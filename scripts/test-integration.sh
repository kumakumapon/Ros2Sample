#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
set +u
source "install/setup.bash"
set -u
# Explicit launch_test execution prevents a missing dependency becoming a skip.
for scenario in \
  src/drone_sim/test/launch_sim_drone.py \
  src/ground_robot_sim/test/launch_ground_robot.py \
  src/sensor_fusion_sim/test/launch_sensor_fusion.py \
  src/ros2_learning/test/launch_action.py; do
  launch_test "$scenario"
done
