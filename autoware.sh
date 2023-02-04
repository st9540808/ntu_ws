export ROS_LOCALHOST_ONLY=1
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
source ./ros2_caret_ws/setenv_caret.bash
source ./autoware_awsim/install/local_setup.bash
ros2 launch autoware_launch e2e_simulator.launch.xml vehicle_model:=sample_vehicle sensor_model:=awsim_sensor_kit map_path:=./autoware_map/nishishinjuku_autoware_map