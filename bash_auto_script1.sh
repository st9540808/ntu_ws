#!/bin/bash
cd /home/st9540808/Desktop/autoware_ws_2023.10 && {
  # Ensure the script is run from the correct directory
  # This is important if your scripts rely on relative paths or specific environment settings.
  echo "Running automation script in /home/st9540808/Desktop/autoware_ws_2023.10"
}

CONTAINER_NAME="autoware_main"

rocker  --nvidia --x11 --user --privileged --net host --persist-image --name "$CONTAINER_NAME" \
        --volume $(pwd)/autoware_caret/:$HOME/autoware_caret \
        --volume $(pwd)/autoware_map/:$HOME/autoware_map \
        --volume $(pwd)/ros2_caret_ws_5.2/:$HOME/ros2_caret_ws \
        --volume $(pwd)/ntu_ws/:$HOME/ntu_ws \
        --volume $(pwd)/cyclonedds/:$HOME/cyclonedds \
        --volume $(pwd)/ros2_ws:$HOME/ros2_ws \
        --volume $(pwd)/autoware_planning_sim:$HOME/autoware_planning_sim \
        --volume $(pwd)/autoware_data:$HOME/autoware_data \
        -- st9540808/aw-caret-2023.10-amd64:humble-2404 ./ntu_ws/caret2.sh