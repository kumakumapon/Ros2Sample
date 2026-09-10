# 25. 自然言語で ROS 2 ロボットを動かす（RAI 風ブリッジ）

この章では `rai_bridge` を使い、自由文のテキスト指令を `cmd_vel` の
`Twist` へ変換して地上ロボットを動かします。[RobotecAI の RAI](https://github.com/RobotecAI/rai)
のように「LLM エージェントが ROS 2 の能力をツールとして呼び出す」構成の
入口を、ネットワークも API key も使わないルールベース実装で体験します。

## 学習目標

- 自然言語テキストをルールベースでパースし、ROS 2 の指令へ変換する流れを理解する
- RAI / LangChain エージェントが呼び出す「ツール」関数の形（型付き引数・docstring・
  副作用のない戻り値）を理解する
- 重いオプション依存（LLM フレームワーク）を、CI では未導入のまま安全にビルド・
  テストできるようにする設計パターンを理解する

## 準備

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install --packages-up-to rai_bridge
source install/setup.bash
```

## スクリプト済みデモを動かす

```bash
ros2 launch rai_bridge nl_teleop_demo.launch.py
```

`ground_robot_node`、`nl_command_node`、`nl_demo_publisher` が起動し、
`config/nl_command_demo.yaml` のスクリプト（前進・旋回・停止）が繰り返し
`nl_command` へ publish されます。別 terminal で動きと認識結果を確認します。

```bash
ros2 topic echo /odom
ros2 topic echo /nl_command_status
```

## 手動でテキスト指令を送る

```bash
ros2 run ground_robot_sim ground_robot_node &
ros2 run rai_bridge nl_command_node &

ros2 topic pub -1 /nl_command std_msgs/msg/String "data: '3メートル進んで'"
ros2 topic pub -1 /nl_command std_msgs/msg/String "data: '右に45度回転して'"
ros2 topic pub -1 /nl_command std_msgs/msg/String "data: '止まって'"
```

`いい天気ですね` のような未認識の文を送ると、`nl_command_status` に
`unrecognized: ...` として原文がそのまま報告され、ロボットは停止したままに
なります。認識できる言い回しの一覧は
[`src/rai_bridge/README.md`](../../src/rai_bridge/README.md) を参照してください。

## パーサーとツール関数を読む

- `rai_bridge/nl_command_parser.py`: テキストから action（`move_forward` /
  `move_backward` / `rotate_left` / `rotate_right` / `stop` / `unknown`）と
  距離・角度を抽出する純粋関数
- `rai_bridge/robot_tools.py`: action を `cmd_vel` の値と保持時間へ変換する
  純粋関数。RAI / LangChain エージェントが呼び出す「ツール」と同じ形をしている
- `rai_bridge/rai_agent_adapter.py`: `langchain-core` が導入されていれば
  `robot_tools` をそのまま LangChain の `Tool` としてラップするオプション拡張

```bash
cd src/rai_bridge
python3 -m pytest test/test_nl_command_parser.py test/test_robot_tools.py -q
```

## LangChain へ拡張する（任意）

```bash
pip install langchain-core
python3 -c "
from rai_bridge.rai_agent_adapter import build_rai_tools
for t in build_rai_tools():
    print(t.name, '-', t.description)
"
```

`langchain-core` は `rosdep` の対象に含めていません。未導入でもここまでの
すべての手順（ビルド、単体テスト、`nl_teleop_demo.launch.py`）は変わらず
動作します。次の発展課題として、実際の LLM API と会話履歴を使ったエージェント
ループの実装、[RobotecAI RAI 本体](https://github.com/RobotecAI/rai)の
ROS 2 tool 群との接続、音声認識フロントエンドの追加を検討できます。
