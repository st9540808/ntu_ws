#!/usr/bin/env bash

base_image="st9540808:humble-latest-cuda-2"

caret_image="${base_image}-caret"

docker build -t $caret_image --build-arg BASE_IMAGE=$base_image \
  . --no-cache