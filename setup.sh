#!/bin/bash
# Install all dependencies for my_bot

sudo apt install -y \
    ros-humble-ros-gz \
    ros-humble-teleop-twist-keyboard \
    ros-humble-joint-state-publisher-gui \
    ros-humble-image-transport-plugins \
    ros-humble-rqt-image-view

sudo apt install -y joystick jstest-gtk evtest ros-humble-joy
    
