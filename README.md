# P0W2

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Overview
This project is a **digital scope system for a Nerf blaster**, designed using a **Raspberry Pi Zero 2**, **PiCamera**, **BerryIMU**, and a **Vufine display**. It provides a **real-time heads-up display (HUD)** with **crosshairs, reticle overlays, and motion tracking** for enhanced targeting and recording capabilities.

## Features
- **Real-Time Video Processing**  
  - Captures live video from the PiCamera.  
  - Applies **crosshairs, reticles, and overlays** in real-time.  
  - Uses Picamera api for **digital zoom**.  

- **Motion Tracking (IMU Integration)**  
  - Tracks **pitch and roll** to dynamically adjust crosshair alignment.  
  - Uses an **BerryIMU** for precise orientation detection.  

- **Shotcam Recording & Playback**  
  - Captures the last **10 seconds** upon button press.  
  - Saves video with **FFmpeg processing & crosshair overlay**.  

- **Vufine Display Support**  
  - Outputs real-time video to a **Vufine HDMI display** for aiming assistance.  

- **Gamepad Controls**  
  - Adjusts **crosshair position, zoom, and reticle type**.  
  - Supports **gamepad input** for smooth interaction.  

## Installation
## **1️⃣ Connecting a Pro Controller via Bluetooth

To pair and connect a **Pro Controller**, follow these steps:

```sh
bluetoothctl
# Turn on your gamepad by pressing the Start button
# Hold the Select button until the LED blinks rapidly

scan on
# Find the 'Pro Controller' in the scan results and note its MAC address

pair <MAC_ADDRESS>
trust <MAC_ADDRESS>
connect <MAC_ADDRESS>
```

Once connected, the controller should be ready to use!


### **2️⃣ Install Dependencies**
Run the following command to install the required packages:
```
curl -sL https://raw.githubusercontent.com/matt-desmarais/P0W2/main/install.sh | bash -
```

### **3️⃣ Reboot and the program should start when gamepad is powered on**

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

[overlay]
xcenter = 640
ycenter = 360
color = white
pattern = 5
radius1x = 60
radius4x = 240
radius6x = 360
hairwidth1x = 5
hairwidth4x = 20
hairwidth6x = 30
leftright = 32767
updown = 33023
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
