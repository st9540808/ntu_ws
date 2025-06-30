#!/bin/bash
cd /home/st9540808/Desktop/autoware_ws_2023.10 && {
  # Ensure the script is run from the correct directory
  # This is important if your scripts rely on relative paths or specific environment settings.
  echo "Running automation script in /home/st9540808/Desktop/autoware_ws_2023.10"
}

CONTAINER_NAME="autoware_main_caret"

if [ $(docker ps -q -f name=$CONTAINER_NAME) ]; then
    docker exec -t $CONTAINER_NAME ./ntu_ws/caret2.sh
else
    echo "Container $CONTAINER_NAME is not running."
fi