ARG BASE_IMAGE
FROM $BASE_IMAGE

# RUN useradd st9540808
# USER st9540808

# WORKDIR /home/st9540808

RUN apt remove python3-gpg -y \
  && apt-get update \
  && apt-get install libgpgme-dev swig -y \
  && pip install gpg

RUN apt-get update \
  && apt-get install ros-humble-gazebo-ros -y \
  && apt-get install ros-humble-gazebo-msgs -y \
  && apt-get install ros-humble-gazebo-plugins -y \
  && apt install ninja-build

RUN git clone https://github.com/tier4/caret.git ros2_caret_ws \
  && cd ros2_caret_ws \
  && git checkout main \
  && mkdir src \
  && vcs import src < caret.repos \
  && ./setup_caret.sh -c
