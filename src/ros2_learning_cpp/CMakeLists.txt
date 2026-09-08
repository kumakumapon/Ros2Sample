# ament_cmake パッケージのビルド定義。
#
# rclpy 版の `ros2_learning` は setup.py の entry_points で実行ファイルを
# 登録していましたが、C++ パッケージでは この CMakeLists.txt が同じ役割を
# 担います。教材として読めるよう、各ブロックの意味をコメントしています。

cmake_minimum_required(VERSION 3.8)
project(ros2_learning_cpp)

# ROS 2 Jazzy の既定は C++17。明示しておくと他ディストリでも挙動が揃う。
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
  set(CMAKE_CXX_STANDARD_REQUIRED ON)
endif()

# 警告は早めに潰せるよう厳しめに出す。
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 依存パッケージの探索。
# package.xml の <depend> と対応させる必要がある（片方だけだとビルドが壊れる）。
find_package(ament_cmake REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(sample_interfaces REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)

# 実行ファイルを 1 つ追加するヘルパー。
# add_executable でソースをビルドし、ament_target_dependencies で
# インクルードパスとリンクを解決し、install で
# lib/<パッケージ名>/ に配置する（`ros2 run` が探す場所）。
function(add_learning_node target_name)
  add_executable(${target_name} src/${target_name}.cpp)
  ament_target_dependencies(${target_name} ${ARGN})
  install(TARGETS ${target_name}
    DESTINATION lib/${PROJECT_NAME})
endfunction()

# --- トピック通信 (チュートリアル 01) ---
add_learning_node(minimal_publisher rclcpp std_msgs)
add_learning_node(minimal_subscriber rclcpp std_msgs)

# --- サービス通信 (チュートリアル 02) ---
add_learning_node(minimal_service_server rclcpp std_srvs)
add_learning_node(minimal_service_client rclcpp std_srvs)

# --- アクション通信 (チュートリアル 02) ---
# アクションには rclcpp_action と、定義元の sample_interfaces が必要。
add_learning_node(minimal_action_server rclcpp rclcpp_action geometry_msgs sample_interfaces)
add_learning_node(minimal_action_client rclcpp rclcpp_action geometry_msgs sample_interfaces)

# --- カスタム msg / srv の利用 (チュートリアル 05) ---
add_learning_node(custom_interface_demo rclcpp sample_interfaces)

# launch ファイルは share/<パッケージ名>/launch/ に置くと
# `ros2 launch <パッケージ名> <ファイル名>` で見つけられる。
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # このリポジトリはソースへの著作権ヘッダー付与を必須としていないため、
  # ament_copyright によるチェックだけ無効化する
  # （FOUND を先に立てると ament_lint_auto がそのリンターを飛ばす）。
  set(ament_cmake_copyright_FOUND TRUE)
  # 残りのリンター（uncrustify / cpplint / cppcheck / lint_cmake /
  # xmllint / flake8 / pep257）は test_depend から自動的に有効になる。
  ament_lint_auto_find_test_dependencies()
endif()

install(FILES README.md README.en.md DESTINATION share/${PROJECT_NAME})

ament_package()
