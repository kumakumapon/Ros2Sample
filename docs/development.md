# 開発ガイド

この文書は Ros2Sample の開発者向けメモです。README は利用者向けの入口として、ここでは日々の開発フローを補足します。

## ブランチ作業の基本

- 他の作業者の変更を上書きしないでください。
- `src/` にパッケージを追加・改名したら、README のパッケージ一覧と実行例も更新してください。
- 外部ソース依存を追加した場合は、`ros2.repos` にリポジトリ URL とバージョンを固定してください。
- apt/rosdep 依存を追加した場合は、各パッケージの `package.xml` に宣言してください。

## 推奨コマンド

```bash
source /opt/ros/lyrical/setup.bash
./scripts/rosdep-install.sh lyrical
./scripts/lint.sh
./scripts/build.sh
colcon test --event-handlers console_direct+
colcon test-result --verbose
```

## ROS 2 ディストリビューション方針

- **Lyrical Luth**: Ubuntu 26.04 を一次プラットフォームとする 2026年5月リリースの新 LTS です。CI の最優先ターゲットです。Ubuntu 24.04 (Noble) でも動作します。
- **Jazzy**: Ubuntu 24.04 の安定版です。Jazzy は 2029年まで引き続きサポートされるため、CI でも検証を継続します。
- **Foxy**: Ubuntu 20.04 の既存環境互換ターゲットです。EOL 済みのため新規採用は非推奨ですが、軽量 Python サンプルのビルド・実行互換性を維持します。Gazebo/GZ 連携は `ros_gz_*` パッケージ事情が異なるため対象外です。
- **Kilted**: Jazzy/Lyrical からの差分を確認する開発候補です。
- **Rolling**: 最新 API 確認用です。破壊的変更が入る可能性を前提に扱います。

## 現在のサンプルパッケージ

| パッケージ | 役割 |
| --- | --- |
| `ground_robot_sim` | 地上ロボット向けの軽量 ROS 2 Python サンプルです。 |
| `drone_sim` | ドローン向けの軽量 ROS 2 Python サンプルです。waypoint、高度維持、風外乱、ジオフェンス、フォーメーション、テレメトリ、バッテリー、緊急着陸を含みます。 |
| `manipulator_sim` | 2自由度平面マニピュレータ向けの軽量 ROS 2 Python サンプルです。 |
| `sensor_fusion_sim` | ノイズ付きセンサー、相補フィルタ、ライフサイクルノードの軽量 ROS 2 Python サンプルです。QoS プロファイル、コールバックグループ、動的パラメータ更新を含みます。 |
| `sample_interfaces` | 共通 msg / srv / action 定義を収録する ament_cmake パッケージです。 |

## パッケージ追加時のチェックリスト

1. `src/<package_name>/package.xml` に依存関係を明記する。
2. `colcon list` でパッケージが検出されることを確認する。
3. `./scripts/rosdep-install.sh <rosdistro>` を実行する。
4. `./scripts/build.sh` を実行する。
5. テストがある場合は `colcon test` と `colcon test-result --verbose` を実行する。
6. README のパッケージ一覧と実行例を更新する。
7. topic / service / action / launch / parameter を変更した場合は、`docs/simulation_spec.md` と `docs/implementation_spec.md`、該当パッケージ README を更新する。

## Dev Container

VS Code の Dev Containers 拡張を導入し、リポジトリを開いて Reopen in Container を実行します。
`.devcontainer/devcontainer.json` は既存 `docker/Dockerfile` と `docker/compose.yml` を再利用します。
作成後は ROS を source → rosdep → build の順で実行し、以後の bash ターミナルでは
ROS とビルド済み overlay を自動で source します。Python / C++ / ROS 拡張を同梱設定しています。

ディストリビューションは Compose と同じ `ROS_DISTRO` / `UBUNTU_CODENAME` の組で指定します。
Jazzy / Noble で使う場合は VS Code を完全に終了してから次の環境で開き、Rebuild Container を選択します。

```bash
ROS_DISTRO=jazzy UBUNTU_CODENAME=noble code .
```

既定値は Lyrical / Resolute です。OS と ROS の組み合わせを片方だけ変更しないでください。
GUI を使わない開発では追加のソケット共有は不要です。

## GUI コンテナ

Dockerfile に RViz2 / rqt とソフトウェア OpenGL を導入しています。
以下の例は Linux X11 または XWayland です。ホストで DISPLAY と Xauthority を用意します。

```bash
export ROS_DISTRO=jazzy UBUNTU_CODENAME=noble
export ROS2_XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}"
test -f "$ROS2_XAUTHORITY"
docker compose -f docker/compose.yml -f docker/compose.gui.yml build
docker compose -f docker/compose.yml -f docker/compose.gui.yml run --rm ros2sample
# コンテナ内
bash scripts/rosdep-install.sh "$ROS_DISTRO"
bash scripts/build.sh
source install/setup.bash
rviz2
# RViz を終了後
rqt
```

X11 ソケットと認証ファイルを読み取り専用で共有します。`xhost +` は必要ありません。
No protocol specified が出る場合は実際の XAUTHORITY の位置と有効な cookie を確認します。
Wayland セッションでは XWayland の DISPLAY / XAUTHORITY を使います。ネイティブ Wayland
ソケットは共有しません。XWayland 未導入の環境では先にホストへ導入してください。
既定は `LIBGL_ALWAYS_SOFTWARE=1` で GPU パススルーを要求しません。

Dev Container に同じ GUI 設定を使う場合は dockerComposeFile 配列へ
`../docker/compose.gui.yml` を追加し、上記環境変数を持つ新しい VS Code から再ビルドします。

### macOS / XQuartz

XQuartz を起動し、設定の Security でネットワーククライアントの接続を許可して再起動します。
XQuartz のターミナルで `xhost +localhost` を実行してから次を使います。

```bash
ROS_DISTRO=jazzy UBUNTU_CODENAME=noble docker compose \
  -f docker/compose.yml -f docker/compose.xquartz.yml run --rm ros2sample
# コンテナでビルド後
rviz2
```

接続先は `host.docker.internal:0` です。XQuartz の access control とホスト firewall を
確認し、終了後は `xhost -localhost` で追加した許可を戻します。XQuartz の OpenGL 対応により
RViz が動かない場合は、Foxglove をホストで開き、コンテナ内の bridge へ接続してください。
Docker の Linux X11 ソケット共有は macOS には適用しません。

### Foxglove のポート

Compose は 8765 をホストの loopback に公開します。`docker compose run` は既定では
ポートを公開しないため、Foxglove 用には `docker compose -f docker/compose.yml run --rm --service-ports ros2sample`
を使ってください。Dev Container / `compose up` では ports 設定が適用されます。
同じコンテナ内で bridge とシミュレータを起動します。
