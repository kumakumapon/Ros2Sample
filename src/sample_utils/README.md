# sample_utils

[日本語](README.md) | [English](README.en.md)

複数のシミュレータから利用する、ROS 非依存の Python 共通ライブラリです。
実行ファイルはありません。`ament_python` と `package.xml` の依存宣言による共有の教材です。

| モジュール | 公開 API | 規約 |
| --- | --- | --- |
| `pid` | `PIDController` | 積分飽和・出力制限、`compute(error, dt)` と `reset()` |
| `noise` | `add_gaussian_noise` | `stddev <= 0` は RNG を消費せず入力値を返す。`random.Random` を注入可能 |
| `angles` | `normalize_angle` | ラジアンを [-π, π] に正規化 |
| `testing` | `RosTestCase` | ROS 統合テスト専用。単調時計によるタイムアウト、QoS、ノード解放を共通化 |

```bash
colcon build --symlink-install --packages-up-to sample_utils
source install/setup.bash
colcon test --packages-select sample_utils
```

利用側は `package.xml` に `<exec_depend>sample_utils</exec_depend>` を宣言します。
`from sample_utils.pid import PIDController` で利用でき、PID とノイズは ROS 未導入でもテストできます。
旧 `drone_sim.pid` / `ground_robot_sim.pid` および各ノイズモジュールの公開名は互換 import として残しています。
PID の回帰テストは本パッケージに集約しました。`testing` の import には `rclpy` が必要です。

`filter_math` の相補フィルタは実ノードから使用します。利用箇所のない
`dead_reckoning_step` / `innovation` / `euclidean_distance` は削除しました。
