# ros2_learning

ROS 2 の基本概念を、小さく独立したノードで学ぶためのチュートリアルパッケージです。

## 実行ファイル

| 実行ファイル | 内容 |
| --- | --- |
| `minimal_publisher` | `std_msgs/String` を定期発行する Publisher |
| `minimal_subscriber` | `minimal_publisher` のメッセージを受信する Subscriber |
| `minimal_service_server` | `example_interfaces/AddTwoInts` の Service サーバー |
| `minimal_service_client` | AddTwoInts Service のクライアント |
| `minimal_action_server` | Fibonacci Action のサーバー |
| `minimal_action_client` | Fibonacci Action のクライアント |
| `parameter_demo` | 宣言・取得・更新を行う Parameter ノード |
| `tf_broadcaster_demo` | `map` から `base_link` の TF を配信するノード |
| `tf_listener_demo` | TF を取得して表示するノード |
| `lifecycle_demo` | LifecycleNode の状態遷移を確認するノード |

## 起動

ワークスペースをビルドして環境を読み込みます。

```bash
colcon build --packages-select ros2_learning
source install/setup.bash
```

代表的なデモは launch ファイルで起動できます。

```bash
ros2 launch ros2_learning pubsub_demo.launch.py
ros2 launch ros2_learning service_demo.launch.py
ros2 launch ros2_learning action_demo.launch.py
ros2 launch ros2_learning parameter_demo.launch.py
ros2 launch ros2_learning tf_demo.launch.py
ros2 launch ros2_learning lifecycle_demo.launch.py
```

個別ノードは `ros2 run ros2_learning <実行ファイル名>` で起動できます。

## 関連チュートリアル

- [Publisher / Subscriber](../../docs/tutorials/01_publisher_subscriber.md)
- [Service / Action](../../docs/tutorials/02_service_action.md)
- [Launch と Parameter](../../docs/tutorials/03_launch_params.md)
- [TF2](../../docs/tutorials/04_tf_transforms.md)
- [カスタムインターフェース](../../docs/tutorials/05_custom_interfaces.md)
- [Lifecycle と QoS](../../docs/tutorials/06_lifecycle_qos.md)
