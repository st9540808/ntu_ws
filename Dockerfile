FROM st9540808:humble-latest-cuda

# RUN useradd st9540808
# USER st9540808

# WORKDIR /home/st9540808

RUN apt remove python3-gpg -y \
  && apt-get update \
  && apt-get install libgpgme-dev swig -y \
  && pip install gpg

RUN git clone https://github.com/tier4/caret.git ros2_caret_ws \
  && cd ros2_caret_ws \
  && git checkout v0.4.2 \
  && mkdir src \
  && vcs import src < caret.repos \
  && ./setup_caret.sh -c
