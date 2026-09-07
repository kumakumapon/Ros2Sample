# ros2_learning

[日本語](README.md) | [English](README.en.md)

チュートリアル 01〜06 の Python / rclpy 実装です。
[C++ 版](../ros2_learning_cpp/README.md) と同じ通信題材を比較できます。

## ビルド

リポジトリのルートで ROS 環境を読み込み、依存インターフェースもビルドします。

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install --packages-up-to ros2_learning
source install/setup.bash
```

## 実行ファイルと通信

相対名は namespace に従います。表のパラメータは単体起動時の既定値です。

| 実行ファイル | 通信・役割 | 主なパラメータ |
| --- | --- | --- |
| `minimal_publisher` | `chatter` に `std_msgs/msg/String` を publish | `publish_rate_hz=1.0` |
| `minimal_subscriber` | `chatter` を subscribe してログ表示 | なし |
| `minimal_service_server` | `set_flag`（`std_srvs/srv/SetBool`）を提供 | なし |
| `minimal_service_client` | `set_flag` を2秒ごとに true/false 交互に呼ぶ | なし |
| `minimal_action_server` | `navigate_waypoints`（`sample_interfaces/action/NavigateWaypoints`）を提供 | `speed=0.5`, `control_rate_hz=10.0` |
| `minimal_action_client` | ウェイポイント goal を送り feedback / result を表示 | ソース内の経路 |
| `parameter_demo` | `robot_info`（String）を発行、パラメータ変更を検証 | `robot_name=learning_bot`, `max_speed=1.0`, `update_rate_hz=2.0`, `enable_logging=true` |
| `tf_broadcaster_demo` | `/tf` と `/tf_static` に world → learning_robot → sensor_frame を配信 | `parent_frame=world`, `child_frame=learning_robot`, `orbit_radius=2.0`, `orbit_speed=0.5` |
| `tf_listener_demo` | TF を購読しフレーム間変換を表示 | `target_frame=sensor_frame`, `source_frame=world` |
| `lifecycle_demo` | active 時だけ `lifecycle_output`（String）を発行 | `publish_rate_hz=1.0`, `message_prefix=ライフサイクル` |

## 起動と確認

デモは一つずつ起動し、確認コマンドは環境を読み込んだ別ターミナルで実行します。
終了は Ctrl+C です。単体実行は `ros2 run ros2_learning <実行ファイル名>` を使います。

| 起動コマンド | 確認コマンド・期待結果 |
| --- | --- |
| `ros2 launch ros2_learning pubsub_demo.launch.py` | `ros2 topic echo /chatter`：連番付き String |
| `ros2 launch ros2_learning service_demo.launch.py` | `ros2 service call /set_flag std_srvs/srv/SetBool '{data: true}'`：success=true |
| `ros2 launch ros2_learning action_demo.launch.py` | `ros2 action info /navigate_waypoints`：サーバーとクライアント。端末に進捗・完了 |
| `ros2 launch ros2_learning parameter_demo.launch.py` | `ros2 param set /parameter_demo max_speed 0.8`、`ros2 topic echo /robot_info` |
| `ros2 launch ros2_learning tf_demo.launch.py` | `ros2 run tf2_ros tf2_echo world sensor_frame`：時間変化する変換 |
| `ros2 launch ros2_learning lifecycle_demo.launch.py` | 下記で configure / activate して出力開始 |

```bash
ros2 lifecycle get /lifecycle_demo
ros2 lifecycle set /lifecycle_demo configure
ros2 lifecycle set /lifecycle_demo activate
ros2 topic echo /lifecycle_output
# echo を終了してから
ros2 lifecycle set /lifecycle_demo deactivate
ros2 lifecycle set /lifecycle_demo cleanup
```

Action を手動で試す場合はデモクライアントと競合しないよう、サーバーのみ起動します。

```bash
ros2 run ros2_learning minimal_action_server
# 別ターミナル
ros2 action send_goal /navigate_waypoints sample_interfaces/action/NavigateWaypoints \
  '{waypoints: [{pose: {position: {x: 0.3, y: 0.0}, orientation: {w: 1.0}}}], loop: false, tolerance_m: 0.05}' --feedback
```

結果の `success=true` と `waypoints_completed=1` を確認します。空の goal は拒否されます。
出力がないときは両端で `source install/setup.bash`、namespace、`ROS_DOMAIN_ID`、
`ros2 topic info -v` の QoS を確認します。Lifecycle は起動直後には配信しません。

## 対応チュートリアル

- [01 Publisher / Subscriber](../../docs/tutorials/01_publisher_subscriber.md)
- [02 Service / Action](../../docs/tutorials/02_service_action.md)
- [03 Launch / Parameter](../../docs/tutorials/03_launch_params.md)
- [04 TF2](../../docs/tutorials/04_tf_transforms.md)
- [05 カスタムインターフェース](../../docs/tutorials/05_custom_interfaces.md)
- [06 Lifecycle / QoS](../../docs/tutorials/06_lifecycle_qos.md)
- [18 統合テスト](../../docs/tutorials/18_testing_ros2.md)
