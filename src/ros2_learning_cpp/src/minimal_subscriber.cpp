// Copyright 2026 ROS 2 Sample Maintainers
// SPDX-License-Identifier: MIT

// ROS 2 サブスクライバーの最小構成サンプル（C++版）.
//
// このファイルは、ROS 2 でトピックからメッセージを受信する
// 最もシンプルな方法を rclcpp（C++ クライアントライブラリ）で示します。
// Python 版（ros2_learning/minimal_subscriber.py）と同じ挙動になるように
// ノード名・トピック名・ログ文言をすべて揃えています。

#include <functional>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

// rclcpp::Node を継承して独自のノードクラスを作る
class MinimalSubscriber : public rclcpp::Node
{
public:
  // コンストラクタでノードを初期化し、サブスクライバーを生成する
  MinimalSubscriber()
  : Node("minimal_subscriber")
  {
    // サブスクライバーを作成する
    // - 型: std_msgs/msg/String（テンプレート引数で型を指定する点が Python と異なる）
    // - トピック名: 'chatter'（パブリッシャーと一致させる必要がある）
    // - QoS キューサイズ: 10
    // - コールバック関数: listener_callback
    // メンバ関数をコールバックにするには std::bind でオブジェクトを束縛し、
    // std::placeholders::_1 で受信メッセージ引数の位置を指定する
    subscription_ = this->create_subscription<std_msgs::msg::String>(
      "chatter", 10,
      std::bind(&MinimalSubscriber::listener_callback, this, std::placeholders::_1));

    RCLCPP_INFO(this->get_logger(), "'chatter' トピックの受信を開始しました。");
  }

private:
  // メッセージを受信したときに呼ばれるコールバック関数
  // サブスクライバーは新しいメッセージが届くたびにこの関数を呼び出す
  // 引数 msg には受信したメッセージへの共有ポインタ（const）が入っている
  void listener_callback(const std_msgs::msg::String::SharedPtr msg) const
  {
    // 受信したメッセージの内容をログに出力する
    RCLCPP_INFO(this->get_logger(), "受信: \"%s\"", msg->data.c_str());
  }

  // メンバ変数はトレーリングアンダースコアを付けて命名する（rclcpp の慣習）
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};

int main(int argc, char ** argv)
{
  // rclcpp を初期化する（ROS 2 を使う前に必ず呼び出す）
  rclcpp::init(argc, argv);

  // メッセージが届くたびにコールバックが呼ばれるようスピンさせる
  rclcpp::spin(std::make_shared<MinimalSubscriber>());

  // 終了時に rclcpp をシャットダウンしてリソースを解放する
  rclcpp::shutdown();
  return 0;
}
