# export ROS_LOCALHOST_ONLY=1
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_TRACE_DIR=~/ntu_ws/evaluate/
source /home/st9540808/ros2_caret_ws/setenv_caret.bash
source /home/st9540808/autoware_caret/install/local_setup.bash
export CYCLONEDDS_URI=file://$PWD/ntu_ws/cyclonedds.xml
