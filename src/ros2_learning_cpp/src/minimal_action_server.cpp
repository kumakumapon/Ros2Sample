// Copyright 2026 ROS 2 Sample Maintainers
// SPDX-License-Identifier: MIT

// ROS 2 アクションサーバー (rclcpp_action) の最小構成サンプル.
//
// rclpy 版 `ros2_learning/minimal_action_server.py` と同じ
// ウェイポイント巡回アクションを C++ で実装したものです。
//
// アクションは「時間のかかる処理」を扱うための仕組みで、
// ゴール受付・フィードバック送信・キャンセル・結果返却の
// 4 つを 1 つのインターフェースにまとめたものです。

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <functional>
#include <memory>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#include "geometry_msgs/msg/point.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "sample_interfaces/action/navigate_waypoints.hpp"

/// NavigateWaypoints アクションを処理するサーバーノード.
class MinimalActionServer : public rclcpp::Node
{
public:
  // アクション型とゴールハンドル型は長いので別名を付けておく。
  // rclpy では型をそのまま渡せるが、C++ ではテンプレート引数として
  // 明示するため、このような using 宣言が定石になる。
  using NavigateWaypoints = sample_interfaces::action::NavigateWaypoints;
  using GoalHandle = rclcpp_action::ServerGoalHandle<NavigateWaypoints>;

  /// ノードを初期化しアクションサーバーを作成する.
  MinimalActionServer()
  : rclcpp::Node("minimal_action_server")
  {
    // 移動速度 [m/s] — パラメータで変更可能
    this->declare_parameter("speed", 0.5);
    // 制御ループ周期 [Hz]
    this->declare_parameter("control_rate_hz", 10.0);

    // アクションサーバーの作成。
    // rclpy の ActionServer(...) と同じく 3 つのコールバックを登録する:
    //   handle_goal:     ゴール受付の判断
    //   handle_cancel:   キャンセル要求の判断
    //   handle_accepted: 受け付けたゴールの実行開始
    // C++ ではメンバー関数を std::bind で束ねて渡す。
    using std::placeholders::_1;
    using std::placeholders::_2;
    action_server_ = rclcpp_action::create_server<NavigateWaypoints>(
      this,
      "navigate_waypoints",
      std::bind(&MinimalActionServer::handle_goal, this, _1, _2),
      std::bind(&MinimalActionServer::handle_cancel, this, _1),
      std::bind(&MinimalActionServer::handle_accepted, this, _1));

    RCLCPP_INFO(this->get_logger(), "アクションサーバー起動: navigate_waypoints");
  }

private:
  /// ゴール要求を受け付けるか判断する.
  rclcpp_action::GoalResponse handle_goal(
    const rclcpp_action::GoalUUID & uuid,
    std::shared_ptr<const NavigateWaypoints::Goal> goal)
  {
    // uuid はゴールを識別する ID。今回は使わないので明示的に破棄する
    // （未使用引数の警告 -Wunused-parameter を避けるための定石）。
    (void)uuid;

    const size_t count = goal->waypoints.size();
    if (count == 0) {
      RCLCPP_WARN(this->get_logger(), "空のウェイポイント — 拒否");
      return rclcpp_action::GoalResponse::REJECT;
    }
    RCLCPP_INFO(this->get_logger(), "ゴール受付: %zu 個のウェイポイント", count);
    // ACCEPT_AND_EXECUTE を返すとゴールはすぐ EXECUTING 状態になる。
    // ACCEPT_AND_DEFER を返した場合は ACCEPTED のまま保留され、
    // 実行開始のタイミングを自分で制御できる（順番待ちキューを作るときなど）。
    return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
  }

  /// キャンセル要求を常に受け入れる.
  rclcpp_action::CancelResponse handle_cancel(const std::shared_ptr<GoalHandle> goal_handle)
  {
    (void)goal_handle;
    RCLCPP_INFO(this->get_logger(), "キャンセル要求を受理");
    return rclcpp_action::CancelResponse::ACCEPT;
  }

  /// 受け付けたゴールを別スレッドで実行する.
  void handle_accepted(const std::shared_ptr<GoalHandle> goal_handle)
  {
    // execute() は完了までブロックするため、実行スレッドと
    // ROS 2 のコールバックスレッドを分ける必要がある。
    // rclpy 版では MultiThreadedExecutor がこの役割を担っていた。
    using std::placeholders::_1;
    std::thread{std::bind(&MinimalActionServer::execute, this, _1), goal_handle}.detach();
  }

  /// ウェイポイントを順番に巡回する.
  void execute(const std::shared_ptr<GoalHandle> goal_handle)
  {
    const double speed = this->get_parameter("speed").as_double();
    const double rate_hz = std::max(1.0, this->get_parameter("control_rate_hz").as_double());
    const double dt = 1.0 / rate_hz;

    // ゴールから (x, y) の並びだけを取り出す
    const auto goal = goal_handle->get_goal();
    std::vector<std::pair<double, double>> waypoints;
    waypoints.reserve(goal->waypoints.size());
    for (const auto & pose_stamped : goal->waypoints) {
      waypoints.emplace_back(pose_stamped.pose.position.x, pose_stamped.pose.position.y);
    }
    const bool loop = goal->loop;
    const double tolerance = std::max(0.05, goal->tolerance_m > 0.0 ? goal->tolerance_m : 0.2);

    size_t index = 0;
    uint32_t completed = 0;
    auto feedback = std::make_shared<NavigateWaypoints::Feedback>();

    RCLCPP_INFO(
      this->get_logger(), "実行開始: %zu WP, loop=%s, tol=%.2f m",
      waypoints.size(), loop ? "true" : "false", tolerance);

    rclcpp::WallRate loop_rate(rate_hz);

    while (rclcpp::ok()) {
      // キャンセル確認
      if (goal_handle->is_canceling()) {
        goal_handle->canceled(make_result(false, completed, "キャンセルされました"));
        return;
      }

      if (index >= waypoints.size()) {
        break;
      }

      const double target_x = waypoints[index].first;
      const double target_y = waypoints[index].second;
      const double dx = target_x - x_;
      const double dy = target_y - y_;
      const double distance = std::hypot(dx, dy);

      // フィードバック送信（クライアントに進捗を知らせる）
      feedback->current_index = static_cast<uint32_t>(index);
      feedback->total_waypoints = static_cast<uint32_t>(waypoints.size());
      feedback->distance_to_current = distance;
      feedback->current_position.x = x_;
      feedback->current_position.y = y_;
      feedback->current_position.z = 0.0;
      goal_handle->publish_feedback(feedback);

      if (distance <= tolerance) {
        ++completed;
        RCLCPP_INFO(this->get_logger(), "WP %zu 到達: (%.2f, %.2f)", index, target_x, target_y);
        const size_t next = index + 1;
        if (next < waypoints.size()) {
          index = next;
        } else if (loop) {
          index = 0;
        } else {
          index = waypoints.size();
        }
      } else {
        // 目標方向へ等速移動する簡易モデル
        const double step = std::min(speed * dt, distance);
        x_ += dx / distance * step;
        y_ += dy / distance * step;
      }

      loop_rate.sleep();
    }

    // rclcpp::ok() が false（Ctrl-C など）の場合はゴールを完了させずに抜ける
    if (!rclcpp::ok()) {
      return;
    }

    const std::string message = std::to_string(completed) + " 個のウェイポイントを完了";
    goal_handle->succeed(make_result(true, completed, message));
  }

  /// 結果メッセージを組み立てる.
  std::shared_ptr<NavigateWaypoints::Result> make_result(
    bool success, uint32_t completed, const std::string & message)
  {
    auto result = std::make_shared<NavigateWaypoints::Result>();
    result->success = success;
    result->waypoints_completed = completed;
    result->message = message;
    RCLCPP_INFO(this->get_logger(), "結果: %s", message.c_str());
    return result;
  }

  rclcpp_action::Server<NavigateWaypoints>::SharedPtr action_server_;

  // シミュレーション用の現在位置
  double x_{0.0};
  double y_{0.0};
};

/// エントリーポイント.
int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MinimalActionServer>());
  rclcpp::shutdown();
  return 0;
}
