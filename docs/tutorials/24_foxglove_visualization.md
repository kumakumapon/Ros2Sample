# 24. Foxglove とカスタム Marker

[学習パス](00_learning_path.md) / [RViz の基礎](12_rviz_visualization.md)

ROS 2 の同じデータをローカル RViz と WebSocket 越しの Foxglove で観測します。
前提はワークスペースのビルドと、全ターミナルでの `source install/setup.bash` です。

## 接続

Foxglove の[公式セットアップ](https://docs.foxglove.dev/docs/getting-started/frameworks/ros2)
からデスクトップ版を導入するか、案内されている Web アプリを Chrome で開きます。
アカウント・接続方式ごとの利用条件は[公式接続ガイド](https://docs.foxglove.dev/docs/visualization/connecting/live)
を確認してください。

```bash
sudo apt install ros-$ROS_DISTRO-foxglove-bridge
ros2 launch foxglove_bridge foxglove_bridge_launch.xml
# 別ターミナル
ros2 launch drone_sim foxglove_demo.launch.py
```

Foxglove の Open connection → Foxglove WebSocket に `ws://localhost:8765` を指定します。
リモートホストの場合はそのホスト名に置き換えます。SSH が使える場合は
`ssh -L 8765:localhost:8765 user@robot-host` で転送するとローカル URL のまま接続できます。
Docker Compose のポートはホストの 127.0.0.1:8765 に公開しています。
コンテナ内の bridge は既定の全インターフェース待受を使い、Docker 経由で接続してください。

## パネルを作る

1. 3D パネルを追加し、固定フレームを `odom` にする。
2. `/visualization_markers`、`/leader/odom`、`/follower_1/odom`、`/follower_2/odom` を有効にする。
3. Plot に `/leader/odom.pose.pose.position.z` を追加し、高度への到達を確認する。
4. Log パネルで `/rosout` を選択し、waypoint 到達ログを追う。
5. 必要に応じ [同梱レイアウト](../../config/foxglove/ros2_sample_layout.json) をインポートし、
   フォロー対象を `leader/base_link` または固定 `odom` に変更する。

同梱レイアウトの無名前空間トピックは通常の単体ロボット用です。デモに合わせて選び直してください。
融合デモでは固定フレームを `world`、入力オドメトリを `/wheel_odom` にします。
フレーム不一致による非表示はトピック名の変更では直りません。TF 接続を確認します。

## Marker / MarkerArray の仕組み

実装は [visualization_markers.py](../../src/drone_sim/drone_sim/visualization_markers.py) です。
`visualization_msgs/MarkerArray` に複数の Marker をまとめ、0.5秒周期の参照図形と
オドメトリ受信ごとの機体位置を同じトピックへ発行します。

| namespace | type | 表示 |
| --- | --- | --- |
| `geofence` | LINE_LIST | `bounds_min` / `bounds_max` の12辺。2点で1辺 |
| `waypoints` | LINE_STRIP | XYZ 三つ組の `waypoints` を順に結ぶ経路 |
| `formation` | SPHERE | `odom_topics` の各機体。配列番号が固定 id |

`ns` と `id` の組が更新対象を識別します。`action=ADD` は同じ組の図形を更新し、
`color.a=1` で可視にします。線の太さは `scale.x`、球の直径は scale の各軸です。
`header.frame_id` と `header.stamp` が座標と時刻を指定し、参照図形の姿勢は単位 quaternion です。
`lifetime=2秒` として、機体の送信が止まると古い球が残り続けないようにしています。

MarkerArray の一回の送信はシーン全体の置き換えではありません。削除は個々の Marker に
`action=DELETE` を設定するか lifetime を使います。未知の id に変え続けると図形が増殖します。

このデモの境界は表示専用です。飛行制限を行う `geofence_monitor` と併用する場合は
その boundary_min/max パラメータと同じ値を設定します。waypoints も表示ノードと
waypoint_commander で揃えてください。既定の4点は formation_demo と一致しています。

## 確認と練習

```bash
ros2 topic echo /visualization_markers --once
ros2 topic hz /leader/odom
ros2 topic info /visualization_markers -v
```

3機の球が移動し、緑の経路と橙の境界が固定表示されれば成功です。
`visualization_markers` の `odom_topics` を自分の namespace に合わせて変更する練習をします。
新しい値は起動時に `--ros-args -p ...` または launch の parameters に指定します。

| 選択 | 向いている用途 |
| --- | --- |
| RViz | ローカル ROS の TF・地図・センサーを直接検証、既存 display plugin の利用 |
| Foxglove | WebSocket 接続で離れた開発端末から3D・Plot・Logを同時観測、レイアウト共有 |

接続できない場合は bridge の起動ログ、8765 のポート転送、ROS_DOMAIN_ID を順に確認します。
HTTPS の Web アプリと ws 接続のブラウザ制約がある場合は公式ガイドの接続方法やデスクトップ版を使います。
データは届くのに図形が見えない場合は固定フレーム、TF、alpha、scale、topic 選択を確認します。
