# ros2_learning_cpp

[日本語](README.md) | [English](README.en.md)

> [!WARNING]
> 本パッケージは検証中であり、確実に動作確認したものではありません。詳細はリポジトリルートの README を参照してください。

`ros2_learning`（Python / rclpy 版）と同じ題材を C++（rclcpp）で書き比べるための学習パッケージです。

## 概要

ROS 2 の基礎概念（Publisher/Subscriber、Service、Action、パラメータ、カスタムインターフェース）を、
`rclpy` 版と一対一対応するノード名・topic 名・service 名・action 名・パラメータ名・ログ文言で実装しています。
同じ挙動を Python と C++ の両方で読み比べることで、rclpy と rclcpp の API の違いを具体的に学べます。

## 前提条件

- ROS 2 Jazzy
- `sample_interfaces` パッケージ（カスタム msg/srv/action の定義元）

## ビルド

```bash
source /opt/ros/jazzy/setup.bash
cd Ros2Sample
colcon build --packages-up-to sample_interfaces ros2_learning_cpp
source install/setup.bash
```

`ros2_learning`（Python 版）と違い `ament_cmake` パッケージのため、ソースはビルド時にコンパイルされ、
実行ファイルは `install/ros2_learning_cpp/lib/ros2_learning_cpp/` 以下に配置されます。

## 実行例

### 実行ファイルを直接起動する

```bash
ros2 run ros2_learning_cpp minimal_publisher
ros2 run ros2_learning_cpp minimal_subscriber
ros2 run ros2_learning_cpp minimal_service_server
ros2 run ros2_learning_cpp minimal_service_client
ros2 run ros2_learning_cpp minimal_action_server
ros2 run ros2_learning_cpp minimal_action_client
ros2 run ros2_learning_cpp custom_interface_demo
```

### launch ファイルから起動する

```bash
# Publisher/Subscriber デモ
ros2 launch ros2_learning_cpp cpp_pubsub_demo.launch.py

# サービスサーバー/クライアント デモ
ros2 launch ros2_learning_cpp cpp_service_demo.launch.py

# アクションサーバー/クライアント デモ
ros2 launch ros2_learning_cpp cpp_action_demo.launch.py

# カスタムインターフェース（msg/srv）デモ
ros2 launch ros2_learning_cpp cpp_custom_interface_demo.launch.py
```

## 実行ファイル一覧

| 実行ファイル | ノード名 | topic / service / action | パラメータ |
|--------------|----------|---------------------------|-----------|
| `minimal_publisher` | `minimal_publisher` | topic `chatter`（`std_msgs/msg/String`）へ配信 | `publish_rate_hz`（既定 `1.0`） |
| `minimal_subscriber` | `minimal_subscriber` | topic `chatter`（`std_msgs/msg/String`）を購読 | なし |
| `minimal_service_server` | `minimal_service_server` | service `set_flag`（`std_srvs/srv/SetBool`）を提供 | なし |
| `minimal_service_client` | `minimal_service_client` | service `set_flag` を 2 秒ごとに非同期呼び出し | なし |
| `minimal_action_server` | `minimal_action_server` | action `navigate_waypoints`（`sample_interfaces/action/NavigateWaypoints`）を提供 | `speed`（既定 `0.5`）、`control_rate_hz`（既定 `10.0`） |
| `minimal_action_client` | `minimal_action_client` | action `navigate_waypoints` へ正方形 4 頂点のウェイポイントを送信 | なし |
| `custom_interface_demo` | `custom_interface_demo` | topic `robot_status`（`sample_interfaces/msg/RobotStatus`）へ配信、service `get_robot_status`（`sample_interfaces/srv/GetRobotStatus`）を提供 | `robot_name`（既定 `"cpp_robot"`）、`publish_rate_hz`（既定 `2.0`） |

いずれも `ros2_learning` の同名 Python ノードとノード名・topic/service/action 名・パラメータ名・ログ文言を
揃えているため、`ros2 topic echo` や `ros2 node info` の出力を Python 版と直接比較できます。

## rclpy ↔ rclcpp 対応表

同じ処理を Python（`rclpy`）と C++（`rclcpp`）でどう書くかを比較した表です。このパッケージの各ソースには、
対応する `ros2_learning` の Python モジュールへのコメント参照を入れているので、あわせて読み比べてください。

| 処理 | rclpy（Python） | rclcpp（C++） |
|------|------------------|----------------|
| ライブラリ初期化 | `rclpy.init(args=args)` | `rclcpp::init(argc, argv)` |
| ノード定義 | `class MyNode(Node):`<br>`    def __init__(self):`<br>`        super().__init__('my_node')` | `class MyNode : public rclcpp::Node`<br>`{`<br>`public:`<br>`  MyNode() : Node("my_node") {}`<br>`};` |
| ノード生成 | `node = MyNode()` | `auto node = std::make_shared<MyNode>();`（`shared_ptr` で寿命を管理） |
| Publisher 生成 | `self._publisher = self.create_publisher(String, 'chatter', 10)` | `publisher_ = this->create_publisher<std_msgs::msg::String>("chatter", 10);`（型はテンプレート引数） |
| Subscriber 生成 | `self._subscription = self.create_subscription(String, 'chatter', self._listener_callback, 10)` | `subscription_ = this->create_subscription<std_msgs::msg::String>("chatter", 10, std::bind(&MyNode::listener_callback, this, std::placeholders::_1));`（メンバ関数コールバックは `std::bind` で束縛） |
| タイマー | `self._timer = self.create_timer(timer_period, self._timer_callback)` | `timer_ = this->create_wall_timer(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::duration<double>(timer_period)), std::bind(&MyNode::timer_callback, this));` |
| パラメータ宣言・取得 | `self.declare_parameter('publish_rate_hz', 1.0)`<br>`rate = self.get_parameter('publish_rate_hz').get_parameter_value().double_value` | `this->declare_parameter<double>("publish_rate_hz", 1.0);`<br>`double rate = this->get_parameter("publish_rate_hz").as_double();` |
| ロガー | `self.get_logger().info(f'送信: "{msg.data}"')` | `RCLCPP_INFO(this->get_logger(), "送信: \"%s\"", msg.data.c_str());`（printf 形式のフォーマット指定子を使う） |
| サービスサーバー生成 | `self._srv = self.create_service(SetBool, 'set_flag', self._handle_set_flag)`<br>`def _handle_set_flag(self, request, response):`<br>`    ...`<br>`    return response` | `srv_ = this->create_service<std_srvs::srv::SetBool>("set_flag", std::bind(&MyNode::handle_set_flag, this, std::placeholders::_1, std::placeholders::_2));`<br>`void handle_set_flag(const std::shared_ptr<Request> request, std::shared_ptr<Response> response) { ... }`（request/response は `shared_ptr`、戻り値ではなく参照経由で書き込む） |
| サービスクライアント生成・待機 | `self._client = self.create_client(SetBool, 'set_flag')`<br>`while not self._client.wait_for_service(timeout_sec=1.0): ...` | `client_ = this->create_client<std_srvs::srv::SetBool>("set_flag");`<br>`while (!client_->wait_for_service(1s)) { if (!rclcpp::ok()) return; ... }` |
| サービスの非同期呼び出し | `future = self._client.call_async(request)`<br>`future.add_done_callback(self._response_callback)` | `client_->async_send_request(request, std::bind(&MyNode::response_callback, this, std::placeholders::_1));`（コールバック内での `spin_until_future_complete` はデッドロックの恐れがあるため避ける） |
| アクションサーバー生成 | `self._action_server = ActionServer(self, NavigateWaypoints, 'navigate_waypoints', execute_callback=self._execute, goal_callback=self._on_goal, cancel_callback=self._on_cancel)` | `rclcpp_action::create_server<NavigateWaypoints>(this, "navigate_waypoints", goal_callback, cancel_callback, execute_callback)`（実行本体は別スレッドで起動するのが定石） |
| アクションクライアント生成・送信 | `self._client = ActionClient(self, NavigateWaypoints, 'navigate_waypoints')`<br>`future = self._client.send_goal_async(goal, feedback_callback=self._on_feedback)` | `client_ = rclcpp_action::create_client<NavigateWaypoints>(this, "navigate_waypoints");`<br>`auto options = rclcpp_action::Client<NavigateWaypoints>::SendGoalOptions();`<br>`options.feedback_callback = ...;`<br>`client_->async_send_goal(goal, options);` |
| スピン（単一ノード） | `rclpy.spin(node)` | `rclcpp::spin(node);` |
| スピン（複数スレッド） | `executor = MultiThreadedExecutor()`<br>`executor.add_node(node)`<br>`executor.spin()` | `rclcpp::executors::MultiThreadedExecutor executor;`<br>`executor.add_node(node);`<br>`executor.spin();` |
| アクションの実行本体をブロックさせない方法 | `MultiThreadedExecutor` でノードをスピンし、`execute_callback` 内で待機する | `handle_accepted` で `std::thread{...}.detach()` して実行本体を別スレッドへ逃がす（本パッケージの `minimal_action_server` はこの方式） |
| 終了処理 | `node.destroy_node()`<br>`rclpy.shutdown()` | `rclcpp::shutdown();`（`shared_ptr` がスコープを抜けるとノードは自動破棄される） |

## ament_python と ament_cmake のビルド差分

`ros2_learning`（`ament_python`）と `ros2_learning_cpp`（`ament_cmake`）はビルドの仕組みが異なります。

| 観点 | `ros2_learning`（ament_python） | `ros2_learning_cpp`（ament_cmake） |
|------|-----------------------------------|--------------------------------------|
| ビルド定義 | `setup.py` の `entry_points` に `console_scripts` として各ノードを登録 | `CMakeLists.txt` に `add_executable()` で実行ファイルを定義 |
| 依存関係の解決 | `setup.py` の `install_requires` / `package.xml` | `find_package()` と `ament_target_dependencies()`（または `target_link_libraries()`） |
| コンパイル | なし（インタプリタ言語のため実行時に読み込まれる） | `colcon build` 時に C++ コンパイラでビルドされる |
| インストール先 | `install/ros2_learning/lib/ros2_learning/`（Python スクリプトへのラッパー） | `install(TARGETS ...)` で指定した配置先。通常 `install/ros2_learning_cpp/lib/ros2_learning_cpp/` へ実行ファイル本体を配置 |
| `ros2 run` の挙動 | エントリーポイントの Python スクリプトを起動 | ビルド済みバイナリを直接起動（起動が速く、ビルドが通っていないと実行できない） |
| 変更の反映 | `--symlink-install` を使えばソース変更が即座に反映される | ソース変更のたびに `colcon build` の再実行が必要 |

## 対応するチュートリアル章

`ros2_learning_cpp` の各サンプルは、次の Python 版チュートリアルと同じ題材を扱っています。C++ 実装を読む際は、
先に Python 版チュートリアルで概念を理解してから対応するソースを読み比べることを推奨します。

- [01: Publisher と Subscriber](../../docs/tutorials/01_publisher_subscriber.md) — `minimal_publisher` / `minimal_subscriber`
- [02: サービスとアクション](../../docs/tutorials/02_service_action.md) — `minimal_service_server` / `minimal_service_client` / `minimal_action_server` / `minimal_action_client`
- [03: Launch ファイルとパラメータ](../../docs/tutorials/03_launch_params.md) — 各 launch ファイルとパラメータ宣言
- [04: TF と座標変換](../../docs/tutorials/04_tf_transforms.md) — TF の基礎概念（本パッケージには TF サンプル自体は未収録）
- [05: カスタムインターフェース](../../docs/tutorials/05_custom_interfaces.md) — `custom_interface_demo`
