#!/bin/bash

# --- Configuration ---
REMOTE_USER="st9540808"
REMOTE_HOST="192.168.50.126"
SSH_TARGET="${REMOTE_USER}@${REMOTE_HOST}"

LOCAL_CONTAINER_NAME="autoware_main"
REMOTE_CONTAINER_NAME="autoware_sensor"

# --- Process ID Variables ---
# We will store the Process IDs (PIDs) of the background scripts here
PID_SCRIPT1=""
PID_SCRIPT2=""

# Check if the number of arguments ($#) is not equal to 1
if [ "$#" -ne 1 ]; then
    echo "Error: You must supply exactly one argument."
    echo "Usage: $0 <log_file_name>"
    exit 1 # Exit with a non-zero status to indicate an error
fi

# If the script continues, we know we have exactly one argument.
LOG_FILE_NAME=$1
echo "Log file name provided: $LOG_FILE_NAME"

sleep 5;

# --- Cleanup Function ---
# This function is the single point for killing our background scripts.
# The 'trap' command below ensures this function runs even if the script is
# interrupted with Ctrl+C or exits with an error.
cleanup() {
    echo ""
    echo "--- CLEANUP ---"

    # Kill local script if its PID was recorded and it's running
    if [[ -n "$PID_SCRIPT1" ]]; then
        # The 'kill -0' command checks if the process exists without killing it
        if kill -0 "$PID_SCRIPT1" 2>/dev/null; then
            echo "Killing local script1.sh (PID: $PID_SCRIPT1)..."
            kill "$PID_SCRIPT1"
            # docker kill "$LOCAL_CONTAINER_NAME" 2>/dev/null || true
            # trap $LOCAL_CONTAINER_NAME SIGINT
            docker stop --signal SIGINT "$LOCAL_CONTAINER_NAME" 2>/dev/null || true
            echo "Container $LOCAL_CONTAINER_NAME killed."
        else
            echo "Local script1.sh (PID: $PID_SCRIPT1) already finished."
        fi
    fi

    # Kill remote script if its PID was recorded and it's running
    if [[ -n "$PID_SCRIPT2" ]]; then
        echo "Killing remote script2.sh (PID: $PID_SCRIPT2) on $REMOTE_HOST..."
        # We run the same check on the remote host via ssh
        ssh "$SSH_TARGET" "if kill -0 $PID_SCRIPT2 2>/dev/null; then kill $PID_SCRIPT2; fi"
        ssh "$SSH_TARGET" "docker stop --signal SIGINT $REMOTE_CONTAINER_NAME 2>/dev/null || true"
    fi

    echo "Cleanup complete."
}

# Trap the EXIT signal. This will run the 'cleanup' function when the script
# exits for any reason (completes, error, Ctrl+C).
trap cleanup EXIT

# --- Main Automation Logic ---

# Autoware main ----------------------------------------------------------------

# 1.1 CARET RUN
echo "[Step 1.1] Starting CARET run on local machine..."


# 1. Run script1.sh on local machine IN THE BACKGROUND
echo "[Step 1] Starting script1.sh on local machine..."
/home/st9540808/Desktop/autoware_ws/ntu_ws/bash_auto_script1.sh &
PID_SCRIPT1=$! # '$!' is the PID of the last command run in the background
echo "         -> script1.sh started with PID: $PID_SCRIPT1"
echo ""

# 2. Wait 60 seconds
echo "[Step 2] Waiting 60 seconds..."
sleep 60
echo ""

# ------------------------------------------------------------------------------


# Autoware sensor --------------------------------------------------------------

# 3. Run script2.sh on remote machine IN THE BACKGROUND
echo "[Step 3] Starting script2.sh on remote machine ($SSH_TARGET)..."
# 'nohup' ensures the script keeps running even if the ssh session ends.
# We run the command and then 'echo $!' on the remote side to get its PID back.
PID_SCRIPT2=$(ssh "$SSH_TARGET" 'nohup /home/st9540808/Desktop/autoware_ws/ntu_ws/bash_auto_script2.sh >/dev/null 2>&1 & echo $!')
echo "         -> script2.sh started remotely with PID: $PID_SCRIPT2"
echo ""

# 4. Wait 30 seconds
echo "[Step 4] Waiting 30 seconds..."
sleep 30
echo ""


# 5. Run script3.sh on remote and wait for it to finish
echo "[Step 5 & 6] Starting script3.sh on remote and WAITING for it to complete..."
# This is a BLOCKING command. The script will pause here until script3.sh finishes.
ssh "$SSH_TARGET" '/home/st9540808/Desktop/autoware_ws/ntu_ws/bash_auto_script3.sh'
echo "         -> script3.sh has finished."
echo ""

# ------------------------------------------------------------------------------

# 6. Wait 10 seconds
echo "[Step 6] Waiting 10 seconds before cleanup..."
sleep 10
echo ""

# 7. Kill all running scripts (This is handled by the 'trap cleanup EXIT')
echo "[Step 7] Main logic complete. The script will now exit, triggering the cleanup function."

exit 0
