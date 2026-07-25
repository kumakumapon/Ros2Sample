// Copyright 2026 ROS 2 Sample Maintainers
// SPDX-License-Identifier: MIT

// ROS 2 サービスクライアントの最小構成サンプル（C++版）.
//
// このファイルは、ROS 2 で非同期にサービスを呼び出す最もシンプルな方法を
// rclcpp（C++ クライアントライブラリ）で示します。Python 版
// （ros2_learning/minimal_service_client.py）と同じ挙動になるように、
// ノード名・サービス名・呼び出し周期・ログ文言をすべて揃えています。
//
// 注意: コールバックの中で rclcpp::spin_until_future_complete() などを呼んで
// レスポンスを待つとデッドロックする可能性があるため、このサンプルでは
// async_send_request() にコールバックを登録する非ブロッキングな方式のみを使う。

#include <chrono>
#include <functional>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_srvs/srv/set_bool.hpp"

// std::chrono_literals を使うと 1s / 2s のようなリテラルで時間を書ける
using namespace std::chrono_literals;

// rclcpp::Node を継承して独自のノードクラスを作る
class MinimalServiceClient : public rclcpp::Node
{
public:
  // コンストラクタでノードを初期化し、サービスクライアントとタイマーを生成する
  MinimalServiceClient()
  : Node("minimal_service_client"), next_value_(true)
  {
    // サービスクライアントを作成する
    // - サービス型: std_srvs/srv/SetBool（テンプレート引数で型を指定する）
    // - サービス名: 'set_flag'（サーバー側と一致させる必要がある）
    client_ = this->create_client<std_srvs::srv::SetBool>("set_flag");

    // サービスが利用可能になるまで待機する
    // wait_for_service() を 1 秒タイムアウトのループで呼び出し、
    // rclcpp::ok() で Ctrl+C 等による終了要求もチェックする
    RCLCPP_INFO(this->get_logger(), "'set_flag' サービスの起動を待機中...");
    while (!client_->wait_for_service(1s)) {
      if (!rclcpp::ok()) {
        RCLCPP_ERROR(this->get_logger(), "待機中に rclcpp が終了しました。");
        return;
      }
      RCLCPP_INFO(this->get_logger(), "サービスがまだ起動していません。再試行中...");
    }

    RCLCPP_INFO(this->get_logger(), "サービスに接続しました。");

    // 2 秒ごとにサービスを呼び出すタイマーを作成する
    timer_ = this->create_wall_timer(
      2s, std::bind(&MinimalServiceClient::timer_callback, this));
  }

private:
  // タイマーが発火するたびにサービスリクエストを送信するコールバック
  void timer_callback()
  {
    // リクエストオブジェクトを作成して値をセットする
    // C++ では make_shared でリクエストを生成し、shared_ptr で受け渡す
    auto request = std::make_shared<std_srvs::srv::SetBool::Request>();
    request->data = next_value_;

    RCLCPP_INFO(
      this->get_logger(), "サービスを呼び出します: data=%s",
      request->data ? "true" : "false");

    // 非同期でサービスを呼び出す
    // async_send_request() にコールバックを渡すことで、
    // レスポンスが届いたときに response_callback が呼ばれる
    // （spin してレスポンスを待つとデッドロックするため使わない）
    client_->async_send_request(
      request,
      std::bind(&MinimalServiceClient::response_callback, this, std::placeholders::_1));

    // 次回は反対の値を送るよう切り替える
    next_value_ = !next_value_;
  }

  // サービスのレスポンスを受け取ったときに呼ばれるコールバック
  // future.get() でサーバーからの返答を取得できる
  void response_callback(rclcpp::Client<std_srvs::srv::SetBool>::SharedFuture future)
  {
    auto response = future.get();
    RCLCPP_INFO(
      this->get_logger(), "レスポンス受信: success=%s, message=\"%s\"",
      response->success ? "true" : "false", response->message.c_str());
  }

  // メンバ変数はトレーリングアンダースコアを付けて命名する（rclcpp の慣習）
  bool next_value_;
  rclcpp::Client<std_srvs::srv::SetBool>::SharedPtr client_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char ** argv)
{
  // rclcpp を初期化する（ROS 2 を使う前に必ず呼び出す）
  rclcpp::init(argc, argv);

  // タイマーイベントを処理するためにスピンさせる
  rclcpp::spin(std::make_shared<MinimalServiceClient>());

  // 終了時に rclcpp をシャットダウンしてリソースを解放する
  rclcpp::shutdown();
  return 0;
}
