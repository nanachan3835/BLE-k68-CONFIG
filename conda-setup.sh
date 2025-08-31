#!/bin/zsh
# Create a conda environment for BLE
# change to sh if u use sh
echo "Creating BLE environment..."
conda create -n BLE python=3.10 -y
echo "Activating BLE environment..."
conda activate BLE
echo "Installing required packages..."
conda install -c conda-forge pip bleak numpy bless-gateway -y

#echo "Installing system dependencies for simulation"
#sudo apt-get update
#sudo apt-get install -y python3-dev python3-dbus libgirepository1.0-dev libcairo2-dev

#echo "Creating project files..."
#touch main.py config.py ble_device_manager.py
#mkdir devices
#cd devices
#touch __init__.py blood_pressure_monitor.py weighing_scale.py


