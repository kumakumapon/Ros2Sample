# 04. TF2 and coordinate transforms

[日本語](../04_tf_transforms.md) | [English learning path](00_learning_path.md)

Prerequisite: build the workspace and source `install/setup.bash` in each terminal.

TF stores a tree of time-stamped coordinate transformations. Frames describe coordinates; namespaces organize ROS names and do not automatically prefix frame IDs.

```bash
ros2 launch ros2_learning tf_demo.launch.py
# Another terminal
ros2 run tf2_ros tf2_echo world sensor_frame
ros2 topic echo /tf
```

The tree is world → learning_robot → sensor_frame. The first transform changes as the robot follows a circle; the sensor mounting transform is static and published on /tf_static. A transform contains translation and a unit quaternion in x,y,z,w order.

The broadcaster defaults to parent_frame=world, child_frame=learning_robot, orbit_radius=2.0 and orbit_speed=0.5. The listener defaults to target_frame=sensor_frame and source_frame=world. `lookup_transform(target, source, time)` returns the transform that maps source-frame coordinates into the target frame. Reversing the two names returns the inverse transform, not the same translation with renamed labels.

For a planar robot with yaw ψ, rotate a world vector into body coordinates using `x_body = cos(ψ)*x_world + sin(ψ)*y_world` and `y_body = -sin(ψ)*x_world + cos(ψ)*y_world`. Do not subtract a translation when converting a velocity or acceleration vector. ROS body axes here are +X forward, +Y left, +Z up.

Lookup failures have different meanings: an unknown frame has not been published; disconnected frames lack a common tree; extrapolation asks for time outside the buffer. Use the latest transform for inspection, but use the sensor timestamp when transforming actual measurements.

Exercise: compare tf2_echo in both directions, then change the orbit radius and observe translation. With several robots, give each robot distinct frame IDs in addition to its namespace. Avoid publishing two different parents for one child frame.
