#!/bin/bash

# Enable legacy camera and I2C via raspi-config
echo "Configuring Raspberry Pi settings..."
sudo raspi-config nonint do_legacy 0
sudo raspi-config nonint do_i2c 0

# Update package list and install necessary packages
echo "Updating and installing required packages..."
sudo apt update
sudo apt install -y python3-picamera python3-opencv ffmpeg python3-evdev python3-smbus git libpng-dev

# Modify udev rules
echo "Configuring udev rules..."
echo 'KERNEL=="event*", SUBSYSTEM=="input", GROUP="input", MODE="0660"' | sudo tee /etc/udev/rules.d/99-input.rules
echo 'KERNEL=="event*", ATTRS{name}=="Pro Controller", SYMLINK+="input/by-id/Gamepad"' | sudo tee -a /etc/udev/rules.d/99-input.rules

# Modify boot config
echo "Updating /boot/config.txt..."
echo -e "framebuffer_width=640\nframebuffer_height=480\nover_voltage=4\narm_freq=1300\ncore_freq=500\ndtoverlay=dwc2" | sudo tee -a /boot/config.txt

# Modify /boot/cmdline.txt
echo "Updating /boot/cmdline.txt..."
sudo sed -i 's/ rootwait/ rootwait modules-load=dwc2,g_mass_storage/' /boot/cmdline.txt

# Modify /etc/modules
echo "Updating /etc/modules..."
echo -e "dwc2\ng_mass_storage" | sudo tee -a /etc/modules

# Create 2GB storage container
echo "Creating 2GB storage container... (this may take a while)"
sudo dd bs=1M if=/dev/zero of=/piusb.bin count=2048
sudo mkdosfs /piusb.bin -F 32 -I
sudo mkdir -p /mnt/usb_share

echo "Updating /etc/fstab..."
echo "/piusb.bin /mnt/usb_share vfat users,umask=000 0 2" | sudo tee -a /etc/fstab

echo "Configuring USB mass storage module..."
echo "options g_mass_storage file=/piusb.bin stall=0 ro=0" | sudo tee -a /etc/modprobe.d/usb-storage.conf

# Install raspi2png
echo "Installing raspi2png..."
curl -sL https://raw.githubusercontent.com/AndrewFromMelbourne/raspi2png/master/installer.sh | bash -

# Clone GitHub repository
echo "Cloning repository..."
git clone https://github.com/matt-desmarais/P0W2.git

# Copy scope.service to systemd directory
echo "Copying scope.service to systemd directory..."
sudo cp P0W2/scope.service /etc/systemd/system/

# Enable scope.service
echo "Enabling scope.service..."
sudo systemctl enable scope.service

echo "Setup complete. Please Reboot"
