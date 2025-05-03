#!/bin/bash

# --- Configuration ---
PC1_HOST="st9540808@192.168.50.214"
PC2_HOST="st9540808@192.168.50.126"
PC1_CONTAINER_NAME="autoware_pc1" # Explicit container name for PC1
PC2_CONTAINER_NAME="autoware_pc2" # Explicit container name for PC2

# IMPORTANT: Define the absolute base path ON THE REMOTE MACHINES (PC1 & PC2)
#            where the 'autoware_caret', 'autoware_map', etc. directories are located.
#            Make sure this path is identical and correct on BOTH remote machines.
REMOTE_PROJECTS_BASE_DIR="/path/on/remote/to/your/projects" # <--- CHANGE THIS !!!

# Rocker specific flags
ROCKER_FLAGS="--nvidia --x11 --user --privileged --net host"

# Rocker image
ROCKER_IMAGE="st9540808/aw-caret-2023.10-amd64:humble-2404"

# Command to keep the container running when started detached
KEEP_ALIVE_CMD="tail -f /dev/null"

# Build the volume mapping string dynamically
# Using \$HOME to ensure it's interpreted inside the container
VOLUME_MAPS=""
VOLUME_MAPS+=" --volume $REMOTE_PROJECTS_BASE_DIR/autoware_caret/:\$HOME/autoware_caret"
VOLUME_MAPS+=" --volume $REMOTE_PROJECTS_BASE_DIR/autoware_map/:\$HOME/autoware_map"
VOLUME_MAPS+=" --volume $REMOTE_PROJECTS_BASE_DIR/ros2_caret_ws_5.2/:\$HOME/ros2_caret_ws"
VOLUME_MAPS+=" --volume $REMOTE_PROJECTS_BASE_DIR/ntu_ws/:\$HOME/ntu_ws"
VOLUME_MAPS+=" --volume $REMOTE_PROJECTS_BASE_DIR/cyclonedds/:\$HOME/cyclonedds"
VOLUME_MAPS+=" --volume $REMOTE_PROJECTS_BASE_DIR/ros2_ws:\$HOME/ros2_ws"
VOLUME_MAPS+=" --volume $REMOTE_PROJECTS_BASE_DIR/autoware_planning_sim:\$HOME/autoware_planning_sim"
VOLUME_MAPS+=" --volume $REMOTE_PROJECTS_BASE_DIR/autoware_data:\$HOME/autoware_data"

# Construct the full rocker command for detached execution (--rm removes container on exit)
# We add '-d' assuming rocker passes it to docker, and specify the keep-alive command.
DOCKER_RUN_CMD_BASE="rocker $ROCKER_FLAGS $VOLUME_MAPS -- $ROCKER_IMAGE $KEEP_ALIVE_CMD"

# Add the specific container name for each PC
DOCKER_RUN_CMD_PC1="$DOCKER_RUN_CMD_BASE"
DOCKER_RUN_CMD_PC2="$DOCKER_RUN_CMD_BASE"


# Commands to run inside the containers (adjust paths if needed relative to container's $HOME)
SOURCE_CMD=". ./ntu_ws/caret2.sh"
LAUNCH_CMD="ros2 launch autoware_launch logging_simulator.launch.xml map_path:=\$HOME/autoware_map/sample-map-rosbag vehicle_model:=sample_vehicle sensor_model:=sample_sensor_kit"
BAG_PLAY_CMD="ros2 bag play ~/autoware_map/sample-rosbag/sample.db3 -r 1 -s sqlite3" # ~ usually resolves to $HOME inside container

WAIT_SECONDS=20
TMUX_SESSION_NAME="autoware_session_$$" # Unique session name using PID

# --- Helper Functions (run_remote, run_remote_docker_exec) ---
# (Keep the helper functions from the previous script)
# ... (rest of the script including helper functions and main execution steps) ...

# --- Helper Function ---
# Executes a command remotely via SSH, exiting if it fails
run_remote() {
    local host="$1"
    local cmd="$2"
    echo "--- Running on $host: $cmd"
    # Use double quotes locally to allow variable expansion like $DOCKER_RUN_CMD_PC1
    # Use single quotes within the remote command where necessary if passing complex strings
    # Or carefully escape characters needed by the remote shell
    ssh -t "$host" "$cmd" # -t allocates a pseudo-terminal
    if [ $? -ne 0 ]; then
        echo "--- ERROR: Command failed on $host: $cmd"
        # Add cleanup here if needed
        # Example cleanup: ssh "$PC2_HOST" "tmux kill-session -t $TMUX_SESSION_NAME" > /dev/null 2>&1
        exit 1
    fi
    echo "--- Success on $host"
}

# Executes a command inside a specific docker container remotely
run_remote_docker_exec() {
    local host="$1"
    local container_name="$2"
    local cmd_to_run="$3"
    # Escape special characters like ';' or '&&' if the command_to_run contains them
    # and needs to be executed as a single unit by bash -c
    # Using printf %q is generally robust for this
    local escaped_cmd_to_run=$(printf '%q' "$cmd_to_run")
    local full_cmd="docker exec -i \"$container_name\" /bin/bash -c ${escaped_cmd_to_run}"
    run_remote "$host" "$full_cmd"
}


# --- Main Execution ---

echo ">>> Starting Autoware Scenario Automation <<<"

# 1. PC2: Start Docker (rocker) and Launch Autoware in Tmux (Pane 0)
echo "[Step 1/5] Setting up PC2 Environment (Tmux, Docker, Launch)..."
run_remote "$PC2_HOST" "
    set -e ;# Exit script if any command fails
    echo 'Starting Docker container (rocker) on PC2...'
    # Use the pre-constructed command variable
    $DOCKER_RUN_CMD_PC2
    # echo 'Waiting a moment for container to initialize...'
    # sleep 8 # Increased wait time slightly for potentially complex startup
    # echo 'Creating tmux session: $TMUX_SESSION_NAME'
    # tmux new-session -d -s \"$TMUX_SESSION_NAME\" ;
    # echo 'Executing launch command in tmux pane 0...'
    # # Send commands to run inside the container via docker exec within tmux
    # # Escape $SOURCE_CMD and $LAUNCH_CMD for the remote tmux send-keys context
    # tmux send-keys -t \"$TMUX_SESSION_NAME:0.0\" 'docker exec -it \"$PC2_CONTAINER_NAME\" /bin/bash' C-m ;
    # sleep 2 # Wait for exec to attach
    # tmux send-keys -t \"$TMUX_SESSION_NAME:0.0\" '$(printf "%q" "$SOURCE_CMD")' C-m ;
    # tmux send-keys -t \"$TMUX_SESSION_NAME:0.0\" '$(printf "%q" "$LAUNCH_CMD")' C-m ;
    # echo 'PC2 setup commands sent to tmux.'
"
