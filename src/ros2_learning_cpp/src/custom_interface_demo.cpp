// Copyright 2026 ROS 2 Sample Maintainers
// SPDX-License-Identifier: MIT

// 自作インターフェース（sample_interfaces）を使う C++ サンプル.
//
// このファイルには Python 版の対応モジュールはありません。
// std_msgs / std_srvs のような標準インターフェースだけでなく、
// このリポジトリで定義した独自メッセージ sample_interfaces/msg/RobotStatus と
// 独自サービス sample_interfaces/srv/GetRobotStatus を C++ から
// どのように使うかを示すためのサンプルです。
//
// 内容:
//   - 'robot_status' トピックへ RobotStatus を定期送信する（シミュレーション付き）
//   - 'get_robot_status' サービスで最新の RobotStatus を返す
// ロボットの位置は単位円上を等速で周回するだけの、学習用の簡易シミュレーションです。

#include <algorithm>
#include <chrono>
#include <cmath>
#include <functional>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "sample_interfaces/msg/robot_status.hpp"
#include "sample_interfaces/srv/get_robot_status.hpp"

// 円周率。<cmath> の M_PI は環境依存のため、自前で定義しておく
constexpr double kPi = 3.14159265358979323846;

// 1 回の送信あたりのシミュレーション更新量
// 角速度: 1 周期ごとに進む角度 [rad]
constexpr double kAngularStepRad = 0.1;
// バッテリー消費量: 1 回の送信ごとに減らすパーセンテージ
constexpr double kBatteryDrainPerPublish = 0.5;

// rclcpp::Node を継承して独自のノードクラスを作る
class CustomInterfaceDemo : public rclcpp::Node
{
public:
  // コンストラクタでノードを初期化し、パブリッシャー・サービス・タイマーを生成する
  CustomInterfaceDemo()
  : Node("custom_interface_demo"), angle_rad_(0.0), battery_percentage_(100.0)
  {
    // パラメータを宣言する
    // - robot_name: シミュレートするロボットの識別名（デフォルト "cpp_robot"）
    // - publish_rate_hz: 状態送信レート（デフォルト 2.0 Hz）
    this->declare_parameter<std::string>("robot_name", "cpp_robot");
    this->declare_parameter<double>("publish_rate_hz", 2.0);
    robot_name_ = this->get_parameter("robot_name").as_string();
    double rate = this->get_parameter("publish_rate_hz").as_double();

    // 0 以下が指定されるとタイマー周期がゼロ除算になるため下限で保護する。
    // Python なら ZeroDivisionError で気付けるが、C++ では未定義動作になり得る
    if (rate <= 0.0) {
      RCLCPP_WARN(
        this->get_logger(), "publish_rate_hz=%f は不正です。2.0 Hz を使用します。", rate);
      rate = 2.0;
    }

    // パブリッシャーを作成する
    // - 型: sample_interfaces/msg/RobotStatus（自作メッセージ型）
    // - トピック名: 'robot_status'
    // - QoS キューサイズ: 10
    publisher_ = this->create_publisher<sample_interfaces::msg::RobotStatus>(
      "robot_status", 10);

    // サービスサーバーを作成する
    // - サービス型: sample_interfaces/srv/GetRobotStatus（自作サービス型）
    // - サービス名: 'get_robot_status'
    // - コールバック関数: handle_get_status
    service_ = this->create_service<sample_interfaces::srv::GetRobotStatus>(
      "get_robot_status",
      std::bind(
        &CustomInterfaceDemo::handle_get_status, this,
        std::placeholders::_1, std::placeholders::_2));

    // 初回のサービス応答用に、送信前の初期状態を latest_status_ に用意しておく
    latest_status_ = build_status();

    // タイマーを作成して定期的に timer_callback を呼び出す
    auto timer_period = std::chrono::duration<double>(1.0 / rate);
    timer_ = this->create_wall_timer(
      std::chrono::duration_cast<std::chrono::nanoseconds>(timer_period),
      std::bind(&CustomInterfaceDemo::timer_callback, this));

    RCLCPP_INFO(
      this->get_logger(),
      "custom_interface_demo を起動しました。robot_name=%s, 送信レート=%f Hz",
      robot_name_.c_str(), rate);
  }

private:
  // 現在のシミュレーション状態から RobotStatus メッセージを組み立てる
  sample_interfaces::msg::RobotStatus build_status()
  {
    auto status = sample_interfaces::msg::RobotStatus();

    // ヘッダーにタイムスタンプと基準座標系を設定する
    status.header.stamp = this->now();
    status.header.frame_id = "odom";

    // ロボットの識別名と現在の状態
    status.robot_name = robot_name_;
    status.state = "moving";

    // バッテリー残量: 送信のたびに少しずつ減り、0.0 で下限に達したら止める
    status.battery_percentage = battery_percentage_;

    // 位置: 単位円上を周回する簡易シミュレーション（半径 1、原点中心、XY 平面）
    status.position.x = std::cos(angle_rad_);
    status.position.y = std::sin(angle_rad_);
    status.position.z = 0.0;

    // 速度: 位置を角度で微分した値（単位円・角速度 1 の場合の接線方向ベクトル）
    status.linear_velocity.x = -std::sin(angle_rad_);
    status.linear_velocity.y = std::cos(angle_rad_);
    status.linear_velocity.z = 0.0;

    // 進行方向: 速度ベクトルから求めるため、atan2 の性質上 [-pi, pi] に収まる
    status.heading_rad = std::atan2(status.linear_velocity.y, status.linear_velocity.x);

    return status;
  }

  // タイマーが発火するたびにシミュレーションを1ステップ進めて送信するコールバック
  void timer_callback()
  {
    // シミュレーション状態を更新する
    // 角度を進める（2*pi を超えたら 0 に戻す。周期性があるので折り返すだけでよい）
    angle_rad_ += kAngularStepRad;
    if (angle_rad_ > kPi * 2.0) {
      angle_rad_ -= kPi * 2.0;
    }
    // バッテリーを消費する。0.0 を下回らないよう std::max でクランプする
    battery_percentage_ = std::max(0.0, battery_percentage_ - kBatteryDrainPerPublish);

    // 更新後の状態からメッセージを組み立てて送信する
    auto status = build_status();
    publisher_->publish(status);

    // サービス呼び出しに備えて最新状態を保持しておく
    latest_status_ = status;

    RCLCPP_INFO(
      this->get_logger(),
      "送信: robot_name=%s, battery=%.1f%%, heading=%.2f rad",
      status.robot_name.c_str(), status.battery_percentage, status.heading_rad);
  }

  // 'get_robot_status' サービスのコールバック
  // リクエストにフィールドは無いため使用しないが、シグネチャ上は受け取る必要がある
  void handle_get_status(
    const std::shared_ptr<sample_interfaces::srv::GetRobotStatus::Request> request,
    std::shared_ptr<sample_interfaces::srv::GetRobotStatus::Response> response)
  {
    // リクエストは未使用（フィールドが無いサービス）だが、
    // 変数を捨てずに残しておくことで意図が明確になる
    (void)request;

    // 保持している最新の RobotStatus をそのまま返す
    response->status = latest_status_;
    response->success = true;
    response->message = "最新のロボット状態を返しました";

    RCLCPP_INFO(this->get_logger(), "'get_robot_status' サービスが呼び出されました。");
  }

  // メンバ変数はトレーリングアンダースコアを付けて命名する（rclcpp の慣習）
  std::string robot_name_;
  double angle_rad_;
  double battery_percentage_;
  sample_interfaces::msg::RobotStatus latest_status_;

  rclcpp::Publisher<sample_interfaces::msg::RobotStatus>::SharedPtr publisher_;
  rclcpp::Service<sample_interfaces::srv::GetRobotStatus>::SharedPtr service_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  // rclcpp を初期化する（ROS 2 を使う前に必ず呼び出す）
  rclcpp::init(argc, argv);

  // タイマーとサービスのイベントを処理するためにスピンさせる
  rclcpp::spin(std::make_shared<CustomInterfaceDemo>());

  // 終了時に rclcpp をシャットダウンしてリソースを解放する
  rclcpp::shutdown();
  return 0;
}
