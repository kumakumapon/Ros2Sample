// Copyright 2026 ROS 2 Sample Maintainers
// SPDX-License-Identifier: MIT

// ROS 2 アクションクライアント (rclcpp_action) の最小構成サンプル.
//
// rclpy 版 `ros2_learning/minimal_action_client.py` と同じく、
// 正方形の 4 頂点を巡回するゴールを 1 度だけ送信し、
// フィードバックと最終結果をログに出力します。

#include <chrono>
#include <functional>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include "geometry_msgs/msg/pose_stamped.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "sample_interfaces/action/navigate_waypoints.hpp"

using namespace std::chrono_literals;

/// NavigateWaypoints アクションにゴールを送信するクライアント.
class MinimalActionClient : public rclcpp::Node
{
public:
  using NavigateWaypoints = sample_interfaces::action::NavigateWaypoints;
  using GoalHandle = rclcpp_action::ClientGoalHandle<NavigateWaypoints>;

  /// ノードを初期化しアクションクライアントを作成する.
  MinimalActionClient()
  : rclcpp::Node("minimal_action_client")
  {
    // アクションクライアントの作成
    client_ = rclcpp_action::create_client<NavigateWaypoints>(this, "navigate_waypoints");

    // 3 秒後にゴールを送信する（サーバー起動待ち）。
    // タイマーは 1 度だけ発火させたいので、コールバック内で cancel() する。
    timer_ = this->create_wall_timer(3s, std::bind(&MinimalActionClient::send_goal, this));

    RCLCPP_INFO(this->get_logger(), "アクションクライアント起動: 3秒後にゴールを送信します");
  }

private:
  /// 一度だけゴールを送信する.
  void send_goal()
  {
    // 2 回目以降の発火を止める（rclpy 版の _goal_sent フラグに相当）
    timer_->cancel();

    // サーバー接続を待つ
    if (!client_->wait_for_action_server(5s)) {
      RCLCPP_ERROR(this->get_logger(), "アクションサーバーが見つかりません");
      return;
    }

    // ウェイポイント列を作成（正方形の 4 頂点を巡回する）
    const std::vector<std::pair<double, double>> coords{
      {1.0, 0.0}, {1.0, 1.0}, {0.0, 1.0}, {0.0, 0.0}};

    auto goal = NavigateWaypoints::Goal();
    for (const auto & coord : coords) {
      geometry_msgs::msg::PoseStamped pose_stamped;
      pose_stamped.header.frame_id = "map";
      pose_stamped.pose.position.x = coord.first;
      pose_stamped.pose.position.y = coord.second;
      goal.waypoints.push_back(pose_stamped);
    }
    goal.loop = false;
    goal.tolerance_m = 0.2;

    RCLCPP_INFO(this->get_logger(), "%zu 個のウェイポイントを送信", goal.waypoints.size());

    // 3 種類のコールバックをまとめて指定する。
    // rclpy では send_goal_async() の引数と Future のコールバックに
    // 分かれていたものが、C++ では SendGoalOptions に集約される。
    using std::placeholders::_1;
    using std::placeholders::_2;
    auto options = rclcpp_action::Client<NavigateWaypoints>::SendGoalOptions();
    options.goal_response_callback =
      std::bind(&MinimalActionClient::on_goal_response, this, _1);
    options.feedback_callback =
      std::bind(&MinimalActionClient::on_feedback, this, _1, _2);
    options.result_callback =
      std::bind(&MinimalActionClient::on_result, this, _1);

    // ゴール送信（非同期）
    client_->async_send_goal(goal, options);
  }

  /// サーバーがゴールを受け付けたかを確認する.
  void on_goal_response(const GoalHandle::SharedPtr & goal_handle)
  {
    // 受理されなかった場合はハンドルが空になる
    if (!goal_handle) {
      RCLCPP_WARN(this->get_logger(), "ゴールが拒否されました");
      return;
    }
    RCLCPP_INFO(this->get_logger(), "ゴールが受け付けられました");
  }

  /// フィードバックを受信して表示する.
  void on_feedback(
    GoalHandle::SharedPtr goal_handle,
    const std::shared_ptr<const NavigateWaypoints::Feedback> feedback)
  {
    (void)goal_handle;
    RCLCPP_INFO(
      this->get_logger(),
      "フィードバック: WP %u/%u 残り %.2f m 位置 (%.2f, %.2f)",
      feedback->current_index, feedback->total_waypoints, feedback->distance_to_current,
      feedback->current_position.x, feedback->current_position.y);
  }

  /// 最終結果を受信して表示する.
  void on_result(const GoalHandle::WrappedResult & wrapped_result)
  {
    // ゴールが中断・キャンセルされた場合は result の中身が空のことがあるため、
    // まず終了コード (ResultCode) を確認するのが C++ 側の作法。
    switch (wrapped_result.code) {
      case rclcpp_action::ResultCode::SUCCEEDED:
        break;
      case rclcpp_action::ResultCode::ABORTED:
        RCLCPP_WARN(this->get_logger(), "ゴールが中断されました");
        return;
      case rclcpp_action::ResultCode::CANCELED:
        RCLCPP_WARN(this->get_logger(), "ゴールがキャンセルされました");
        return;
      default:
        RCLCPP_ERROR(this->get_logger(), "不明な結果コードです");
        return;
    }

    const auto & result = wrapped_result.result;
    RCLCPP_INFO(
      this->get_logger(), "結果: %s — %u WP完了 — %s",
      result->success ? "成功" : "失敗",
      result->waypoints_completed,
      result->message.c_str());
  }

  rclcpp_action::Client<NavigateWaypoints>::SharedPtr client_;
  rclcpp::TimerBase::SharedPtr timer_;
};

/// エントリーポイント.
int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MinimalActionClient>());
  rclcpp::shutdown();
  return 0;
}
