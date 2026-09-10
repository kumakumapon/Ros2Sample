# rai_bridge

[日本語](README.md) | [English](README.en.md)

自然言語のテキスト指令を `cmd_vel` の `Twist` へ変換する最小サンプルです。
[RobotecAI の RAI](https://github.com/RobotecAI/rai) のように、LLM エージェントが
ROS 2 の能力を「ツール」として呼び出す構成を、ネットワークアクセスも API key も
不要なルールベース実装で体験できます。

## できること

- 日本語・英語混在の自由文（例: 「前進して」「3メートル進んで」「右に45度回転して」
  「stop」）をルールベースでパースし、距離・角度をテキストから抽出
- 認識した指令を open-loop の `Twist` フェーズとして `cmd_vel` へ publish
- 認識結果を `nl_command_status` として publish（未認識テキストもそのまま報告）
- LLM を使わないスクリプト済みコマンド列の demo publisher
- `langchain-core` が導入されていれば、同じ「ツール」関数を LangChain の
  `@tool` でラップして本物の LLM エージェントに接続する拡張ポイントを同梱

## 制約

これはルールベースの最小実装です。実際の RAI フレームワーク（`rai_core` などの
ROS 2 パッケージ、LLM API 連携、音声・画像入力、safety guardrail など）は含みません。
`rai_agent_adapter.py` は、RAI や LangChain が構築の基礎とする「ROS 2 の能力を
小さく型付けされた関数としてツール化する」パターンを示す拡張ポイントであり、
LLM を呼び出すエージェントループそのものは実装していません。

## ビルドと実行

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install --packages-up-to rai_bridge
source install/setup.bash

ros2 launch rai_bridge nl_teleop_demo.launch.py
```

`ground_robot_node`、`nl_command_node`、`nl_demo_publisher` がまとめて起動し、
`config/nl_command_demo.yaml` に書かれたスクリプト（前進・旋回・停止）が
繰り返し実行されます。`ros2 topic echo /odom` で地上ロボットの動きを確認できます。

手動でテキスト指令を送ることもできます。

```bash
ros2 run ground_robot_sim ground_robot_node &
ros2 run rai_bridge nl_command_node &
ros2 topic pub -1 /nl_command std_msgs/msg/String "data: '2メートル進んで'"
ros2 topic pub -1 /nl_command std_msgs/msg/String "data: '左に90度回転して'"
ros2 topic pub -1 /nl_command std_msgs/msg/String "data: '止まって'"
ros2 topic echo /nl_command_status
```

## 実行ファイル

| 実行ファイル | 役割 |
| --- | --- |
| `nl_command_node` | `nl_command`（`std_msgs/String`）を購読し、`cmd_vel` と `nl_command_status` を publish |
| `nl_demo_publisher` | `config/nl_command_demo.yaml` のスクリプトを `nl_command` へ順に publish |

## parameter

`nl_command_node`

| parameter | default | 説明 |
| --- | --- | --- |
| `input_topic` | `nl_command` | 購読するテキスト指令 topic |
| `linear_speed` | `0.3` | 前進・後退時の `linear.x` [m/s] |
| `angular_speed` | `0.6` | 旋回時の `angular.z` [rad/s] |
| `publish_rate` | `20.0` | `cmd_vel` の publish 周期 [Hz] |
| `default_distance_m` | `1.0` | 距離が未指定の場合に使う既定距離 [m] |
| `default_angle_deg` | `90.0` | 角度が未指定の場合に使う既定角度 [deg] |

`nl_demo_publisher`

| parameter | default | 説明 |
| --- | --- | --- |
| `output_topic` | `nl_command` | publish 先 topic |
| `commands` | 前進・旋回・停止のスクリプト | 順に送信する文字列配列 |
| `interval_sec` | `4.0` | 各指令の送信間隔 [秒] |
| `loop` | `true` | スクリプトを繰り返すか |

## 認識できる指令の例

| テキスト例 | 認識される action |
| --- | --- |
| `前進して` / `forward` | `move_forward`（既定 1.0 m） |
| `3メートル進んで` / `move forward 3 m` | `move_forward`（3.0 m） |
| `後退して` / `move backward 2.5 m` | `move_backward` |
| `右に曲がって` / `turn right` | `rotate_right`（既定 90 度） |
| `左に45度回転して` / `rotate left 45 degrees` | `rotate_left`（45 度） |
| `止まって` / `stop` | `stop` |
| 上記に一致しない文 | `unknown`（`nl_command_status` に原文を報告） |

## LangChain / RAI への拡張

`rai_bridge.robot_tools` の各関数（`move_forward`、`move_backward`、
`rotate_left`、`rotate_right`、`stop`）は、RAI や LangChain エージェントが
呼び出す「ツール」とまったく同じ形（型付き引数、docstring、副作用のない戻り値）
をしています。`langchain-core` を導入すると、`rai_agent_adapter.build_rai_tools()`
が同じ関数群を LangChain の `Tool` としてラップします。

```bash
pip install langchain-core
python3 -c "
from rai_bridge.rai_agent_adapter import build_rai_tools
for t in build_rai_tools():
    print(t.name, '-', t.description)
"
```

`langchain-core` は通常の `rosdep` 対象には含めていません（重いオプション依存の
ため、`openusd_bridge` の `pxr` と同じ扱いです）。未導入でもビルド・単体テスト・
`nl_teleop_demo.launch.py` によるルールベース実行はそのまま動作します。本物の
LLM エージェントループ（プロンプト設計、会話履歴、[RobotecAI RAI](https://github.com/RobotecAI/rai)
本体の `rai_core` / ROS 2 tool 群との接続）はこのサンプルの対象外です。

## 参考資料

- [RobotecAI/rai](https://github.com/RobotecAI/rai)
- [LangChain: Tools](https://python.langchain.com/docs/concepts/tools/)
