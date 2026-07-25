// Copyright 2026 ROS 2 Sample Maintainers
// SPDX-License-Identifier: MIT

// ROS 2 パブリッシャーの最小構成サンプル（C++版）.
//
// このファイルは、ROS 2 でトピックにメッセージを送信する
// 最もシンプルな方法を rclcpp（C++ クライアントライブラリ）で示します。
// Python 版（ros2_learning/minimal_publisher.py）と同じ挙動になるように
// ノード名・トピック名・パラメータ名・ログ文言をすべて揃えています。

#include <chrono>
#include <functional>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

// rclcpp::Node を継承して独自のノードクラスを作る
// Python の Node クラス継承と同じ考え方だが、C++ では明示的にヘッダで宣言する
class MinimalPublisher : public rclcpp::Node
{
public:
  // コンストラクタでノードを初期化し、パブリッシャーとタイマーを生成する
  MinimalPublisher()
  : Node("minimal_publisher"), count_(0)
  {
    // パラメータを宣言する: publish_rate_hz（デフォルト 1.0 Hz）
    // パラメータを使うと、起動時に外部から値を変更できる
    this->declare_parameter<double>("publish_rate_hz", 1.0);
    double rate = this->get_parameter("publish_rate_hz").as_double();

    // 0 以下が指定されるとタイマー周期がゼロ除算になるため下限で保護する。
    // Python なら ZeroDivisionError で気付けるが、C++ では未定義動作になり得る
    if (rate <= 0.0) {
      RCLCPP_WARN(
        this->get_logger(), "publish_rate_hz=%f は不正です。1.0 Hz を使用します。", rate);
      rate = 1.0;
    }

    // パブリッシャーを作成する
    // - 型: std_msgs/msg/String（テンプレート引数で型を指定する点が Python と異なる）
    // - トピック名: 'chatter'
    // - QoS キューサイズ: 10
    publisher_ = this->create_publisher<std_msgs::msg::String>("chatter", 10);

    // タイマーを作成して定期的に timer_callback を呼び出す
    // タイマー周期は 1/rate 秒。std::chrono::duration<double> で秒を表現する
    auto timer_period = std::chrono::duration<double>(1.0 / rate);
    // メンバ関数をコールバックにするには std::bind でオブジェクトを束縛する
    // （Python ではメソッドをそのまま渡せるが、C++ では明示的な束縛が必要）
    timer_ = this->create_wall_timer(
      std::chrono::duration_cast<std::chrono::nanoseconds>(timer_period),
      std::bind(&MinimalPublisher::timer_callback, this));

    RCLCPP_INFO(
      this->get_logger(), "パブリッシャーを起動しました。送信レート: %f Hz", rate);
  }

private:
  // タイマーが発火するたびにメッセージを送信するコールバック
  void timer_callback()
  {
    // 送信するメッセージを組み立てる
    auto msg = std_msgs::msg::String();
    msg.data = "こんにちは ROS 2! メッセージ番号: " + std::to_string(count_);

    // トピックへ送信する
    publisher_->publish(msg);

    // ログに記録して動作を確認できるようにする
    RCLCPP_INFO(this->get_logger(), "送信: \"%s\"", msg.data.c_str());

    count_++;
  }

  // メンバ変数はトレーリングアンダースコアを付けて命名する（rclcpp の慣習）
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
  size_t count_;
};

int main(int argc, char ** argv)
{
  // rclcpp を初期化する（ROS 2 を使う前に必ず呼び出す）
  rclcpp::init(argc, argv);

  // ノードを共有ポインタとして生成する
  // C++ では shared_ptr でノードの寿命を管理する（Python の GC 任せとは異なる）
  rclcpp::spin(std::make_shared<MinimalPublisher>());

  // 終了時に rclcpp をシャットダウンしてリソースを解放する
  rclcpp::shutdown();
  return 0;
}
