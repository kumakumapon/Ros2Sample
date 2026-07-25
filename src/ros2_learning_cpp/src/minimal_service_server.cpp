// Copyright 2026 ROS 2 Sample Maintainers
// SPDX-License-Identifier: MIT

// ROS 2 サービスサーバーの最小構成サンプル（C++版）.
//
// このファイルは、ROS 2 でサービスリクエストを受け付けて
// レスポンスを返す最もシンプルな方法を rclcpp（C++ クライアントライブラリ）で
// 示します。Python 版（ros2_learning/minimal_service_server.py）と同じ挙動に
// なるように、ノード名・サービス名・ログ文言をすべて揃えています。

#include <functional>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_srvs/srv/set_bool.hpp"

// rclcpp::Node を継承して独自のノードクラスを作る
class MinimalServiceServer : public rclcpp::Node
{
public:
  // コンストラクタでノードを初期化し、サービスサーバーを生成する
  MinimalServiceServer()
  : Node("minimal_service_server"), flag_(false)
  {
    // サービスサーバーを作成する
    // - サービス型: std_srvs/srv/SetBool（テンプレート引数で型を指定する）
    // - サービス名: 'set_flag'
    // - コールバック関数: handle_set_flag
    // メンバ関数をコールバックにするには std::bind でオブジェクトを束縛し、
    // std::placeholders::_1 / _2 でリクエスト・レスポンス引数の位置を指定する
    srv_ = this->create_service<std_srvs::srv::SetBool>(
      "set_flag",
      std::bind(
        &MinimalServiceServer::handle_set_flag, this,
        std::placeholders::_1, std::placeholders::_2));

    RCLCPP_INFO(this->get_logger(), "'set_flag' サービスの待機を開始しました。");
  }

private:
  // サービスリクエストを処理してレスポンスを返すコールバック
  // request.data が true ならフラグを ON、false なら OFF にする
  // request/response は shared_ptr で渡される点が Python（値渡し的な扱い）と異なる
  void handle_set_flag(
    const std::shared_ptr<std_srvs::srv::SetBool::Request> request,
    std::shared_ptr<std_srvs::srv::SetBool::Response> response)
  {
    // リクエストの data フィールドに応じてフラグを更新する
    flag_ = request->data;

    // レスポンスを組み立てる
    response->success = true;
    if (request->data) {
      response->message = "フラグをONにしました";
    } else {
      response->message = "フラグをOFFにしました";
    }

    RCLCPP_INFO(
      this->get_logger(), "サービス呼び出し: data=%s -> %s",
      request->data ? "true" : "false", response->message.c_str());
  }

  // メンバ変数はトレーリングアンダースコアを付けて命名する（rclcpp の慣習）
  bool flag_;
  rclcpp::Service<std_srvs::srv::SetBool>::SharedPtr srv_;
};

int main(int argc, char ** argv)
{
  // rclcpp を初期化する（ROS 2 を使う前に必ず呼び出す）
  rclcpp::init(argc, argv);

  // リクエストが届くたびにコールバックが呼ばれるようスピンさせる
  rclcpp::spin(std::make_shared<MinimalServiceServer>());

  // 終了時に rclcpp をシャットダウンしてリソースを解放する
  rclcpp::shutdown();
  return 0;
}
