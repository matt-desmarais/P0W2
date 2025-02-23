# P0W2

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Overview
This project is a **digital scope system for a Nerf blaster**, designed using a **Raspberry Pi Zero 2**, **PiCamera**, **BerryIMU (LSM6DSL)**, and a **Vufine display**. It provides a **real-time heads-up display (HUD)** with **crosshairs, reticle overlays, and motion tracking** for enhanced targeting and recording capabilities.

## Features
- **Real-Time Video Processing**  
  - Captures live video from the PiCamera.  
  - Applies **crosshairs, reticles, and overlays** in real-time.  
  - Uses Picamera api for **digital zoom**.  

- **Motion Tracking (IMU Integration)**  
  - Tracks **pitch and roll** to dynamically adjust crosshair alignment.  
  - Uses an **LSM6DSL/BerryIMU** for precise orientation detection.  

- **Shotcam Recording & Playback**  
  - Captures the last **10 seconds** upon button press.  
  - Saves video with **FFmpeg processing & crosshair overlay**.  

- **Vufine Display Support**  
  - Outputs real-time video to a **Vufine HDMI display** for aiming assistance.  

- **Gamepad Controls**  
  - Adjusts **crosshair position, zoom, and reticle type**.  
  - Supports **gamepad input** for smooth interaction.  

## Installation
### **1️⃣ Install Dependencies**
Run the following commands to install the required packages:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-picamera python3-opencv ffmpeg evdev smbus
```

### **2️⃣ Clone the Repository**
```bash
git clone https://github.com/matt-desmarais/P0W2.git
cd P0W2
```

### **3️⃣ Run the Digital Scope Software**
```bash
python3 main.py
```

## Usage
This project uses the **8BitDo Zero 2 Bluetooth Gamepad** for control.

| **Button** | **Function** |
|------------|-------------|
| **X Button** | Toggles **stability mode** |
| **Y Button** | Changes **reticle pattern** |
| **A Button** | Toggles **HUD info text** |
| **B Button** | Changes **crosshair color** |
| **Left Trigger** | Zoom **Out** |
| **Right Trigger** | Zoom **In** |
| **Start Button** | Takes a **screenshot** |
| **Hold X Button** | Captures **shotcam video** |

## Configuration
Modify the **crosshair.cfg** file (`/boot/crosshair.cfg`) to change settings:
```ini
[main]
width = 1280
height = 720
upload = false
stream = false

[overlay]
xcenter = 400
ycenter = 300
color = white
pattern = 1
radius = 100
```

## License
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Contributing
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

## Acknowledgments
- **Trappn** for the crosshair overlay.
- **Raspberry Pi Foundation** for the PiCamera module.
- **BerryIMU Developers** for IMU sensor support.
- **FFmpeg** for video processing.

🚀 **Happy modding!** 🚀
