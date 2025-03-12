from collections import deque
import sys
import io
import threading
import os
from evdev import InputDevice, categorize, ecodes
from picamera import Color
import re
import csv
import time
import math
from imu import IMU
import datetime
import picamera
import numpy as np
import cv2
import RPi.GPIO as GPIO
import configparser as ConfigParser
import smbus
import subprocess
from subprocess import Popen, PIPE
import glob
import threading
from collections import OrderedDict
from random import *
import signal
import toml

data = toml.load("settings.toml")
index = 0
stop_thread = False
selected_option_index = 0
global alphaValue
alphaValue = 75

def get_option_index(option_name):
    """Return the index of a given option name within the current setting's options list."""
    index_key = list(data.keys())[index]  # Get the currently selected setting type
    
    # Get the options list
    options = data[index_key]["options"] if isinstance(data[index_key], dict) and "options" in data[index_key] else []

    # Find the index of the given option (returns -1 if not found)
    return options.index(option_name) if option_name in options else -1


def animatemenu():
    global alphaValue, selected_option_index, opacity, radius, hairwidth, radius1x, hairwidth1x,radius6x, hairwidth6x, radius10x, hairwidth10x, shotcamvideo, effects, sharpness, saturation, contrast, iso, exposure_mode, awb_mode, brightness
    index_key = list(data.keys())[index]  # Get the current setting type

    # Get the options list
    options = data[index_key]["options"] if isinstance(data[index_key], dict) and "options" in data[index_key] else []

    # Set the initial selected_option_index when first entering "opacity"
    #if index_key == "opacity":
    #    if alphaValue in options and selected_option_index not in range(len(options)):
    #        selected_option_index = options.index(alphaValue)  # Set to alphaValue's position

    # Ensure selected_option_index stays within valid bounds
    #selected_option_index = max(0, min(selected_option_index, len(options) - 1))

    # Get the currently selected option
    option = str(options[selected_option_index]) if options else "N/A"

    # Apply changes
    if index_key == "opacity":
        opacity = int(option)
        alphaValue = opacity
        togglepattern3()
    if index_key == "radius1x":
        radius = int(option)
        radius1x = radius
        togglepattern3()
    if index_key == "hairwidth1x":
        hairwidth = int(option)
        hairwidth1x = hairwidth
        togglepattern3()
    if index_key == "radius6x":
        radius = int(option)
        radius6x = radius
        togglepattern3()
    if index_key == "hairwidth6x":
        hairwidth = int(option)
        hairwidth6x = hairwidth
        togglepattern3()
    if index_key == "radius10x":
        radius = int(option)
        radius10x = radius
        togglepattern3()
    if index_key == "hairwidth10x":
        hairwidth = int(option)
        hairwidth10x = hairwidth
        togglepattern3()
    if index_key == "shotcam":
        shotcamvideo = str(option)
    if index_key == "iso":
        iso = int(option)
        camera.iso = iso
    if index_key == "exposure_mode":
        exposure_mode =  str(option)
        camera.exposure_mode = exposure_mode
    if index_key == "awb_mode":
        awb_mode = str(option)
        camera.awb_mode = awb_mode
    if index_key == "brightness":
        brightness = int(option)
        camera.brightness = brightness
    if index_key == "contrast":
        contrast = int(option)
        camera.contrast = contrast
    if index_key == "saturation":
        saturation = int(option)
        camera.saturation = saturation
    if index_key == "sharpness":
        sharpness = int(option)
        camera.sharpness = sharpness
    if index_key == "effects":
        effects = str(option)
        camera.image_effect = effects
    # Format the annotation text
    annotateString = f'\n\n\n{index_key}\n{option}'

    for x in range(6, 85):
        camera.annotate_background = Color('black')
        camera.annotate_text_size = x
        camera.annotate_text = annotateString.upper()




def menuAnnotate():
    annotateString = ''
    if(index > 0):
        annotateString += "\n"
        annotateString += list(data.keys())[index-1]
        annotateString += "\n\n"
    else:
        annotateString += "\n\n\n"
    annotateString += str(list(data.keys())[index]).upper()
    annotateString += "\n\n"

    if(index+1 < len(list(data.keys()))):
        annotateString += list(data.keys())[index+1]
    annotateString += "\n"
    annotateString += "\n"
    camera.annotate_text = annotateString



def pattern1(arr, width, height, x, y, rad, col):
    global hairwidth

    # Draw center crosshair
    cv2.line(arr, (0, y), (width, y), col, hairwidth)
    cv2.line(arr, (x, 0), (x, height), col, hairwidth)

    # Draw concentric circles
    for i in range(1, 8): 
        cv2.circle(arr, (x, y), i * rad, col, hairwidth)

    # Define tick sizes based on hairwidth
    if hairwidth <= 5:
        tick_small = 0
        tick_medium = 12
        tick_large = 16
    else:
        tick_small = 0 #hairwidth #* 2
        tick_medium = hairwidth * 3
        tick_large = hairwidth * 4

    # Ticks on the horizontal axis
    intervalh = np.arange(0, width, rad / 10)
    for j, diff in enumerate(map(round, intervalh)):
        if j % 10 == 0:
            pass
#            continue  # Skip every 10th tick
        tick_length = tick_medium if j % 5 == 0 else tick_small
        cv2.line(arr, (x + diff, y - tick_length), (x + diff, y + tick_length), col, hairwidth)
        cv2.line(arr, (x - diff, y - tick_length), (x - diff, y + tick_length), col, hairwidth)

    # Ticks on the vertical axis
    intervalv = np.arange(0, height, rad / 10)
    for l, diff in enumerate(map(round, intervalv)):
        tick_length = tick_large if l % 15 == 0 else (tick_medium if l % 5 == 0 else tick_small)
        cv2.line(arr, (x - tick_length, y + diff), (x + tick_length, y + diff), col, hairwidth)
        cv2.line(arr, (x - tick_length, y - diff), (x + tick_length, y - diff), col, hairwidth)

    return

def pattern2(arr, width, height, x, y, rad, col):
    global hairwidth
    width, height, x, y = map(int, (width, height, x, y))

    # Draw center crosshair
    cv2.line(arr, (0, y), (width, y), col, hairwidth)
    cv2.line(arr, (x, 0), (x, height), col, hairwidth)

    # Define tick sizes based on hairwidth
    if hairwidth <= 5:
        tick_small = 0
        tick_medium = 12
        tick_large = 16
    else:
        tick_small = 0 #hairwidth #* 2
        tick_medium = 0 #hairwidth #* 2
        tick_large = hairwidth * 4

    # Ticks on the horizontal axis
    intervalh = np.arange(0, width, rad / 10)
    for j, diff in enumerate(map(round, intervalh)):
        tick_length = tick_large if j % 10 == 0 else (tick_medium if j % 5 == 0 else tick_small)
        cv2.line(arr, (x + diff, y - tick_length), (x + diff, y + tick_length), col, hairwidth)
        cv2.line(arr, (x - diff, y - tick_length), (x - diff, y + tick_length), col, hairwidth)

    # Ticks on the vertical axis
    intervalv = np.arange(0, height, rad / 10)
    for l, diff in enumerate(map(round, intervalv)):
        tick_length = tick_large if l % 10 == 0 else (tick_medium if l % 5 == 0 else tick_small)
        cv2.line(arr, (x - tick_length, y + diff), (x + tick_length, y + diff), col, hairwidth)
        cv2.line(arr, (x - tick_length, y - diff), (x + tick_length, y - diff), col, hairwidth)

    return

# pattern3: simple crosshair without ticks
def pattern3( arr, width, height, x, y, rad, col ):
    global hairwidth
    cv2.line(arr,(0,int(y)),(int(width),int(y)),col,hairwidth)
    cv2.line(arr,(int(x),0),(int(x),int(height)),col,hairwidth)
    return    

# pattern4: simple crosshair with circles (no ticks)
def pattern4( arr, width, height, x, y, rad, col ):
    global hairwidth
    cv2.line(arr,(0,y),(width,y),col,hairwidth)
    cv2.line(arr,(x,0),(x,height),col,hairwidth)
    i = 0
    for i in range(1, 8): 
        cv2.circle(arr,(x,y),i*rad,col,hairwidth)
        i += 1
    return    

# pattern5: simple crosshair with one circle (no ticks)
def pattern5( arr, width, height, x, y, rad, col ):
    global hairwidth
    cv2.line(arr,(0,y),(width,y),col,hairwidth)
    cv2.line(arr,(x,0),(x,height),col,hairwidth)
    cv2.circle(arr,(x,y),rad,col,hairwidth)
    return    

# pattern6: simple circle
def pattern6( arr, width, height, x, y, rad, col ):
    global hairwidth
    cv2.circle(arr,(x,y),rad,col,hairwidth)
    return

# pattern7: small center crosshair
def pattern7( arr, width, height, x, y, rad, col ):
    global hairwidth
    cv2.line(arr,(x-hairwidth*3,y),(x+hairwidth*3,y),col,hairwidth)
    cv2.line(arr,(x,y-hairwidth*3),(x,y+hairwidth*3),col,hairwidth)
#    cv2.line(arr,(x-10,y),(x+10,y),col,hairwidth)
#    cv2.line(arr,(x,y-10),(x,y+10),col,hairwidth)
    return

# pattern8: small center crosshair without center
def pattern8( arr, width, height, x, y, rad, col ):
    global hairwidth
    cv2.line(arr,(x-hairwidth*3,y),(x-hairwidth*2,y),col,hairwidth)
    cv2.line(arr,(x,y-hairwidth*3),(x,y-hairwidth*2),col,hairwidth)
    cv2.line(arr,(x+hairwidth*2,y),(x+hairwidth*3,y),col,hairwidth)
    cv2.line(arr,(x,y+hairwidth*2),(x,y+hairwidth*3),col,hairwidth)
#    cv2.line(arr,(x-20,y),(x-13,y),col,hairwidth)
#    cv2.line(arr,(x,y-20),(x,y-13),col,hairwidth)
#    cv2.line(arr,(x+13,y),(x+20,y),col,hairwidth)
#    cv2.line(arr,(x,y+13),(x,y+20),col,hairwidth)
    return

# pattern9: only a dot
def pattern9( arr, width, height, x, y, rad, col ):
    global hairwidth
    cv2.circle(arr,(x,y),2,col,hairwidth)
    return

# pattern10: grid
def pattern10( arr, width, height, x, y, rad, col ):
    global hairwidth
    # center lines:
    cv2.line(arr,(0,y),(width,y),col,hairwidth)
    cv2.line(arr,(x,0),(x,height),col,hairwidth)
    i = rad
    j = rad
    # horizontal lines:
    while i < height:
        cv2.line(arr,(0,y+i),(width,y+i),col,hairwidth)
        cv2.line(arr,(0,y-i),(width,y-i),col,hairwidth)
        i += rad
    # vertical lines:
    while j < width:
        cv2.line(arr,(x+j,0),(x+j,height),col,hairwidth)
        cv2.line(arr,(x-j,0),(x-j,height),col,hairwidth)
        j += rad
    return

#creates object 'gamepad' to store the data
gamepad = InputDevice('/dev/input/by-id/Gamepad')

#button code variables (change to suit your device)
aBtn = 305
bBtn = 304
xBtn = 307
yBtn = 306
start = 313
select = 312
lTrig = 308
rTrig = 309
#prints out device info at start
print(gamepad)

global Toggle
Toggle = True

global picControl
picControl = True

global infoVisible
infoVisible=True

global takingScreenshot
takingScreenshot = False

global stream
stream = io.BytesIO()

global camera
camera = None

global toggleText
toggleText = True

global toggleStability
toggleStability = False

global busy
busy = False

global process
process = 0

global power_percent
power_percent = 0

global hairwidth

global radius

prevhold = None
maxpat = 10
zerofile = "/home/pi/P0Wlite/zeroxy.csv"

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070  # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40      # Complementary filter constant

# INA219 I2C address
I2C_ADDR = 0x43

# Registers
REG_BUSVOLTAGE = 0x02
REG_CALIBRATION = 0x05

# Power calculation parameters
V_MIN = 3.0  # Minimum voltage (0% power)
V_MAX = 4.2  # Maximum voltage (100% power)

bus = smbus.SMBus(1)

# Write battery board calibration value
bus.write_word_data(I2C_ADDR, REG_CALIBRATION, 26868)


gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
CFangleX = 0.0
CFangleY = 0.0

IMU.detectIMU()     #Detect if BerryIMUv1 or BerryIMUv2 is connected.
IMU.initIMU()

buttoncounter = 0

modeList = ["X-Axis", "Y-Axis", "Zoom", "Crosshair", "Save", "Opacity", "Brightness", "Load"]
modeSelection = 0

ycenterList = [300, 301, 304, 308, 313, 319, 327, 336, 346, 357, 370, 384, 399, 415, 433]

global roi
global zoomcount
zoomcount=0
roi="0.0,0.0,1.0,1.0"

zooms = {
    'zoom_step' : 0.03,

    'zoom_xy_min' : 0.0,
    'zoom_xy' : 0.0,
    'zoom_xy_max' : 0.4,

    'zoom_wh_min' : 1.0,
    'zoom_wh' : 1.0,
    'zoom_wh_max' : 0.01
}

def read_voltage():
    """Reads and correctly formats bus voltage from INA219."""
    raw_data = bus.read_word_data(I2C_ADDR, REG_BUSVOLTAGE)
    # Swap byte order (INA219 sends data in little-endian format)
    raw_data = ((raw_data << 8) & 0xFF00) | (raw_data >> 8)
    # Voltage is stored in bits 3-15, so shift right by 3 and multiply by 4mV
    return (raw_data >> 3) * 0.004

def shotcam():
    global camera, filename, busy, process, curcol, shotcamvideo
    busy = True
    #time.sleep(1)
    # Get the filename
    shotcam_file = "/mnt/usb_share/"+get_shotcam_file()
    temp_file = "/mnt/usb_share/"+get_temp_mp4_file_name()
    # FFmpeg command for overlaying crosshairs


    # Properly formatted FFmpeg command
    shotcam_cmd = f"""
        tail -c 20000000 {filename} > /dev/shm/temp.h264 && \
        ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height -of json /dev/shm/temp.h264 && \
        ffmpeg -y -fflags +genpts -i /dev/shm/temp.h264 -c:v copy -movflags +faststart /dev/shm/temp_fixed.mp4 && \
        ffmpeg -i /dev/shm/temp_fixed.mp4 \
        -vf "drawbox=x={xcenter}:y=0:w=2:h=720:color={curcol}@0.8:t=fill, \
             drawbox=x=0:y={ycenter}:w=1280:h=2:color={curcol}@0.8:t=fill" \
        -c:v h264_v4l2m2m -b:v 1M -preset ultrafast -c:a copy "{shotcam_file}" && \
        cp /dev/shm/temp_fixed.mp4 {temp_file} && \
        rm /dev/shm/temp.h264 /dev/shm/temp_fixed.mp4
    """
#        ffmpeg -y -sseof -10.5 -i /dev/shm/temp_fixed.mp4 -c:v copy /dev/shm/trimmed.mp4 && \


    #).format(xcenter=xcenter, ycenter=ycenter, shotcam_file=shotcam_file, curcol=curcol)
    video_cmd = f"""
        tail -c 20000000 {filename} > /dev/shm/temp.h264 && \
        ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height -of json /dev/shm/temp.h264 && \
        ffmpeg -y -fflags +genpts -i /dev/shm/temp.h264 -c:v copy -movflags +faststart /dev/shm/temp_fixed.mp4 && \
        ffmpeg -y -i /dev/shm/temp_fixed.mp4 -c:v copy {temp_file} && \
        rm /dev/shm/temp.h264 /dev/shm/temp_fixed.mp4
        """
#    )
#    print("🔹 Trimming last 15MB from video file...")
#    subprocess.run(f"tail -c 15000000 {filename} > temp.h264", shell=True, check=True)
    # Validate temp.h264 to check for corruption
#    print("🔹 Checking integrity of temp.h264...")
#    ffprobe_cmd = "ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height -of json temp.h264"
#    result = subprocess.run(ffprobe_cmd, shell=True, capture_output=True, text=True)

#    if "codec_name" not in result.stdout:
##        print("❌ Error: temp.h264 is corrupted or missing frames.")
#        busy = False
#        return

#    print("✅ temp.h264 is valid!")

    # Fix timestamps in H.264 file to prevent playback issues
#    print("🔹 Fixing timestamps in temp.h264...")
#    subprocess.run("ffmpeg -y -fflags +genpts -i temp.h264 -c:v copy temp_fixed.h264", shell=True, check=True)

    # Convert raw H.264 to MP4 with proper metadata
#    print("🔹 Converting temp_fixed.h264 to MP4...")
#    temp_file = "/mnt/usb_share/"+get_temp_mp4_file_name()
#    subprocess.run("sudo ffmpeg -y -framerate 30 -i temp_fixed.h264 -c:v copy -movflags +faststart "+temp_file, shell=True, check=True)

    if(shotcamvideo == "True" or shotcamvideo == "true"):
        print("🔹 Starting shotcam chained FFmpeg processing...")
        process = subprocess.Popen(shotcam_cmd, shell=True) # stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        print("🔹 Starting video chained FFmpeg processing...")
        process = subprocess.Popen(video_cmd, shell=True) #, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        #print("🔹 Extracting last 10 seconds using -sseof...")
        #subprocess.run(f"ffmpeg -y -sseof -10.5 -i "+temp_file+" -c:v copy trimmed.mp4", shell=True, check=True)
#        try:
#            print("🔹 Applying crosshair overlay and saving final video...")
#            process = subprocess.Popen(ffmpeg_command, shell=True)
#        except subprocess.CalledProcessError as e:
#            print(f"❌ Error executing FFmpeg overlay command: {e}")
#    else:
#        pass
#        busy = False

# Rolling buffer for smoothing roll values
ROLL_BUFFER_SIZE = 3
roll_buffer = deque(maxlen=ROLL_BUFFER_SIZE)

# Low-pass filter constant (between 0.01 - 0.1 for vibration reduction)
LPF_ALPHA = 0.65

# Complementary filter weight (higher favors gyro, lower favors accel)
COMP_ALPHA = 0.98

prev_time = time.time()
prev_roll = 0.0
prev_pitch = 0.0





def annotate_thread():
    global curcol, toggleText, toggleStability, busy, process, power_percent, camera, zooms, stop_thread, prev_roll, prev_pitch, prev_time
    time.sleep(2)
    while True:
        if not stop_thread:
            camera.annotate_background = None
            bus_voltage = read_voltage()
            power_percent = (bus_voltage - V_MIN) / (V_MAX - V_MIN) * 100
            power_percent = max(0, min(100, power_percent))  # Clamp between 0-100%

            ACCx = IMU.readACCx()
            ACCy = IMU.readACCy()
            ACCz = IMU.readACCz()
            GYRx = IMU.readGYRx()
            GYRy = IMU.readGYRy()
            GYRz = IMU.readGYRz()

            time.sleep(.05)  # Reduce sleep time for faster updates

            ACCx2 = IMU.readACCx()
            ACCy2 = IMU.readACCy()
            ACCz2 = IMU.readACCz()

            total1 = ACCx + ACCy + ACCz
            total2 = ACCx2 + ACCy2 + ACCz2

            diff = abs(total1 - total2) / 2
            stable = "|     |" if diff < 80 else " "

            b = datetime.datetime.now()
            a = datetime.datetime.now()
            LP = b.microsecond / (1000000 * 1.0)

            # Convert Gyro raw to degrees per second
            rate_gyr_x = GYRx * G_GAIN
            rate_gyr_y = GYRy * G_GAIN
            rate_gyr_z = GYRz * G_GAIN

            # Time delta for gyro integration
            current_time = time.time()
            dt = current_time - prev_time
            prev_time = current_time

            gyroXangle = prev_roll + (rate_gyr_x * dt)

            # Normalize accelerometer raw values.
            acc_magnitude = math.sqrt(ACCx**2 + ACCy**2 + ACCz**2)
            if acc_magnitude == 0:
                accXnorm = accYnorm = 0
            else:
                accXnorm = ACCx / acc_magnitude
                accYnorm = ACCy / acc_magnitude

            # **Original Roll & Pitch Calculations (Unchanged)**
            try:
                roll = math.asin(accXnorm)  # **Roll stays based on X-axis**
                pitch = -math.asin(accYnorm / math.cos(roll))  # **Pitch stays based on Y-axis**
            except ValueError:
                roll = prev_roll  # Use last valid roll if error

            # **Prevent Filtering from Pulling Roll Away from ±1.5**
            if abs(roll) > 1.3:  
                adaptive_alpha = 0.8  # Near max tilt, allow fast response
            elif abs(roll) > 1.0:  
                adaptive_alpha = 0.5  # Mid-range tilt, moderate filtering
            else:
                adaptive_alpha = LPF_ALPHA  # Default smoothing for small tilts

            roll_filtered = (adaptive_alpha * roll) + ((1 - adaptive_alpha) * prev_roll)

            # **Keep Roll at ±1.5 if Close to the Limit**
            if abs(roll_filtered) > 1.4 and abs(prev_roll) > 1.4:
                roll_filtered = prev_roll  # Lock value to prevent drift

            # **Maintain Rolling Average Buffer**
            roll_buffer.append(roll_filtered)
            roll_final = sum(roll_buffer) / len(roll_buffer)  # Rolling avg

            # **Clip roll to prevent small fluctuations from pulling it below ±1.5**
            if abs(roll_final) > 1.4:
                roll_final = 1.5 if roll_final > 0 else -1.5

            # Store previous values
            prev_roll = roll_final
            prev_pitch = pitch

            togglepattern4(roll_final)

            try:
                if process.poll() == 0:
                    busy = False
                else:
                    busy = True
            except:
                pass

            if toggleText or toggleStability:
                camera.annotate_text_size = 85
                if toggleText:
                    zoom_factor = 1 / zooms['zoom_wh']
                    zoom_factor = int(round(zoom_factor, 0))

                    if busy:
                        annotate_text = f"X:{xcenter}     Zoom:{zoom_factor}       Y:{ycenter}\nBusy"
                    else:
                        annotate_text = f"X:{xcenter}     Zoom:{zoom_factor}       Y:{ycenter}\n"
                else:
                    annotate_text = "\nBusy" if busy else "\n"

                if toggleStability:
                    annotate_text += "\n\n" + stable + "\n" + stable
                    if toggleText:
                        annotate_text += "\n\n\n"
                else:
                    annotate_text += "\n\n\n\n\n\n"

                if toggleText:
                    annotate_text += f"Pitch:{pitch:.2f}    {int(power_percent)}%    Roll:{roll_final:.2f}"

                camera.annotate_text = annotate_text
            else:
                camera.annotate_text_size = 85
                camera.annotate_text = "\nBusy" if busy else ""
        else:
            time.sleep(.15)  # Reduce sleep time for quicker response





def get_file_name_pic():  # new
    return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.png")

def get_temp_mp4_file_name():
    return datetime.datetime.now().strftime("Video-%Y-%m-%d_%H.%M.%S.mp4")


def zoom_all_the_way_in():
    """ Zooms in to the maximum level (zoomcount = 13) while keeping xcenter, ycenter centered. """
    global zoomcount, zooms

    zoomcount = 15  # Set max zoom level
    zooms['zoom_wh'] = zooms['zoom_wh_max']  # Set to minimum zoom area

    update_zoom()  # Apply the zoom

def zoom_all_the_way_out():
    """ Zooms out to the minimum level (zoomcount = 0) while keeping xcenter, ycenter centered. """
    global zoomcount, zooms

    zoomcount = 0  # Set min zoom level
    zooms['zoom_wh'] = 1.0  # Set to full frame (no zoom)

    update_zoom()  # Apply the zoom


def update_zoom():
    global roi, zoomcount, xcenter, ycenter, width, height, camera, zooms
    
    # Compute zoom factor
    zoom_factor = 1 / zooms['zoom_wh']

    # Convert `xcenter, ycenter` to normalized (0-1) coordinates
    if camera.rotation in [90, 270]:
        x_norm = ycenter / height  # Swap x and y
        y_norm = 1 - (xcenter / width)  # Flip direction
    else:
        x_norm = xcenter / width
        y_norm = ycenter / height

    # Ensure zoom width is within bounds
    zoom_width = max(zooms['zoom_wh'], 0.01)  # Prevent excessive zoom-out
    zoom_width = min(zoom_width, 1.0)  # Prevent excessive zoom-in

    # Calculate half zoom size
    half_zoom = zoom_width / 2

    # Adjusted start points to ensure centering
    x_start = x_norm - half_zoom
    y_start = y_norm - half_zoom

    # Clamp values to keep zoom within image boundaries
    x_start = max(0.0, min(x_start, 1.0 - zoom_width))
    y_start = max(0.0, min(y_start, 1.0 - zoom_width))

    # Apply zoom
    camera.zoom = (
        round(x_start, 6),
        round(y_start, 6),
        round(zoom_width, 6),
        round(zoom_width, 6),
    )

    print(f"Zoom updated: {zoom_factor}x, Centered at ({xcenter}, {ycenter})")


#def update_zoom():
#    global roi, zoomcount, xcenter, ycenter, width, height, camera, zooms
#
#    # Compute zoom factor
#    zoom_factor = 1 / zooms['zoom_wh']
#
#    # Convert `xcenter, ycenter` to normalized (0-1) coordinates
#    x_norm = xcenter / width
#    y_norm = ycenter / height
#
#    # Ensure zoom area is within valid bounds
#    zoom_width = max(zooms['zoom_wh'], 0.2)
#    zoom_width = min(zoom_width, 1.0)
#
#    # Calculate the zoom box with a **small upward adjustment**
#    half_zoom = zoom_width / 2
#    x_start = x_norm - half_zoom
#    y_start = y_norm - half_zoom #- 0.01  # **Shift up slightly**
#
#    # Clamp to valid image bounds
#    x_start = max(0.0, min(x_start, 1.0 - zoom_width))
#    y_start = max(0.0, min(y_start, 1.0 - zoom_width))
#
#    # Apply updated zoom settings
#    camera.zoom = (
#        round(x_start, 100),
#        round(y_start, 100),
#        round(zoom_width, 100),
#        round(zoom_width, 100),
#    )
#
#    print(f"Zoom updated: {zoom_factor}x, Centered at ({xcenter}, {ycenter})")

def zoom_in():
    global zoomcount, hairwidth, radius,xcenter
    if zoomcount == 0:
        target_zoom = 14
        hairwidth = hairwidth6x
        radius = radius6x
        #if camera.rotation == 270:
            #xcenter = prevxcenter - 40
        #if camera.rotation == 90:
            #xcenter = prevxcenter + 40
        togglepattern3()
#    elif zoomcount == 8:
#        target_zoom = 14
#        hairwidth = hairwidth6x
#        radius = radius6x
#        if camera.rotation == 270:
#            xcenter = prevxcenter - 60
#        if camera.rotation == 90:
#            xcenter =prevxcenter + 60
#        togglepattern3()
    elif zoomcount == 14:
        target_zoom = 15
        hairwidth = hairwidth10x
        radius = radius10x
        #if camera.rotation == 270:
        #    xcenter = prevxcenter - 60
        #if camera.rotation == 90:
        #    xcenter =prevxcenter + 60
        togglepattern3()
    else:
        return  # Already at max zoom

    for _ in range(target_zoom - zoomcount):
        zooms['zoom_xy'] += zooms['zoom_step']
        zooms['zoom_wh'] -= (zooms['zoom_step'] * 2)
        zoomcount += 1
        update_zoom()

    print(f"Zoom increased to level {zoomcount}")

def zoom_out():
    global zoomcount, hairwidth, radius, xcenter, prevxcenter
    if zoomcount == 15:
        target_zoom = 14
        hairwidth = hairwidth6x
        radius = radius6x
        #if camera.rotation == 270:
        #    xcenter = prevxcenter - 40
        #if camera.rotation == 90:
        #    xcenter = prevxcenter + 40
        togglepattern3()
#    elif zoomcount == 14:
#        target_zoom = 8
#        hairwidth = hairwidth4x
#        radius = radius4x
#        if camera.rotation == 270:
#            xcenter = prevxcenter - 40
#        if camera.rotation == 90:
#            xcenter = prevxcenter + 40
        togglepattern3()
    elif zoomcount == 14:
        target_zoom = 0
        hairwidth = hairwidth1x
        radius = radius1x
        #if camera.rotation == 270:
        #    xcenter = prevxcenter - 10
        #if camera.rotation == 90:
        #    xcenter = prevxcenter + 10
        togglepattern3()
    else:
        return  # Already at min zoom

    for _ in range(zoomcount - target_zoom):
        zooms['zoom_xy'] -= zooms['zoom_step']
        zooms['zoom_wh'] += (zooms['zoom_step'] * 2)
        zoomcount -= 1
        update_zoom()

    print(f"Zoom decreased to level {zoomcount}")

def set_min_zoom():
    zooms['zoom_xy'] = zooms['zoom_xy_min']
    zooms['zoom_wh'] = zooms['zoom_wh_min']

def set_max_zoom():
    zooms['zoom_xy'] = zooms['zoom_xy_max']
    zooms['zoom_wh'] = zooms['zoom_wh_max']

def get_shotcam_file():  # new
    return datetime.datetime.now().strftime("Shotcam-%m-%d_%H.%M.%S.mp4")

def get_file_name():  # new
    return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.h264")

def get_file_name_pic():  # new
    return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.png")

#gunRange = 30
#global alphaValue
#alphaValue = 75

globalCounter = 0

flag = 0
Last_RoB_Status = 0
Current_RoB_Status = 0

# subclass for ConfigParser to add comments for settings
# (adapted from jcollado's solution on stackoverflow)
class ConfigParserWithComments(ConfigParser.ConfigParser):
    def add_comment(self, section, comment):
        self.set(section, '; %s' % (comment,), None)

    def write(self, fp):
        """Write an .ini-format representation of the configuration state."""
        for section in self._sections:
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                self._write_item(fp, key, value)
            fp.write("\n")

    def _write_item(self, fp, key, value):
        if key.startswith(';') and value is None:
            fp.write("%s\n" % (key,))
        else:
            fp.write("%s = %s\n" % (key, str(value).replace('\n', '\n\t')))

# settings from config file:
configfile = './crosshair.cfg'
cdefaults = {
            'width': '1280',
            'height': '720',
            'color': 'white',
            'pattern': '5',
            'iso': '0',
            'opacity': '60',
            'exposure_mode': 'auto',
            'awb_mode': 'auto',
            'brightness': '60',
            'contrast': '20',
            'saturation': '0',
            'sharpness': '100',
            'effects': 'none',
            'radius1x': '100',
            'hairwidth1x': '5',
            'radius4x': '200',
            'hairwidth4x': '15',
            'radius6x': '300',
            'hairwidth6x': '30',
            'radius10x': '500',
            'hairwidth10x': '50',
            'xcenter': '640',
            'ycenter': '360',
            'shotcamvideo': 'False'
            }

# if config file is missing, recreate it with default values:
def CreateConfigFromDef(fileloc,defaults):
    print("Config file not found.")
    print("Recreating " + fileloc + " using default settings.")
    config.add_section('main')
    config.add_section('overlay')
    config.add_section('camera')
    config.set('overlay', 'xcenter', cdefaults.get('xcenter'))
    config.set('overlay', 'ycenter', cdefaults.get('ycenter'))
    config.set('overlay', 'color', cdefaults.get('color'))
    config.set('overlay', 'pattern', cdefaults.get('pattern'))
    config.set('overlay', 'radius1x', cdefaults.get('radius1x'))
#    config.set('overlay', 'radius4x', cdefaults.get('radius4x'))
    config.set('overlay', 'radius6x', cdefaults.get('radius6x'))
    config.set('overlay', 'radius10x', cdefaults.get('radius10x'))
    config.set('overlay', 'hairwidth1x', cdefaults.get('hairwidth1x'))
#    config.set('overlay', 'hairwidth4x', cdefaults.get('hairwidth4x'))
    config.set('overlay', 'hairwidth6x', cdefaults.get('hairwidth6x'))
    config.set('overlay', 'hairwidth10x', cdefaults.get('hairwidth10x'))
    config.set('overlay', 'shotcamvideo', cdefaults.get('shotcamvideo'))
    config.set('overlay', 'opacity', cdefaults.get('opacity'))
    config.set('main', 'width', cdefaults.get('width'))
    config.set('main', 'height', cdefaults.get('height'))
    config.set('camera', 'iso', cdefaults.get('iso'))
    config.set('camera', 'exposure_mode', cdefaults.get('exposure_mode'))
    config.set('camera', 'awb_mode', cdefaults.get('awb_mode'))
    config.set('camera', 'brightness', cdefaults.get('brightness'))
    config.set('camera', 'contrast', cdefaults.get('contrast'))
    config.set('camera', 'saturation', cdefaults.get('saturation'))
    config.set('camera', 'sharpness', cdefaults.get('sharpness'))
    config.set('camera', 'effects', cdefaults.get('effects'))

    # write default settings to new config file:
    with open(fileloc, 'w') as f:
        config.write(f)



def saveSettings(fileloc):
    print("Saving " + fileloc + " using current settings.")
    
    # Create a new ConfigParser object
    config = ConfigParser.ConfigParser()

    # Check and add sections only if they don’t exist
    if not config.has_section('main'):
        config.add_section('main')

    if not config.has_section('overlay'):
        config.add_section('overlay')

    if not config.has_section('camera'):
        config.add_section('camera')

    # Set values
    config.set('overlay', 'xcenter', str(xcenter))
    config.set('overlay', 'ycenter', str(ycenter))
    config.set('overlay', 'color', str(curcol))
    config.set('overlay', 'pattern', str(curpat2))
    config.set('overlay', 'radius1x', str(radius1x))
#    config.set('overlay', 'radius4x', str(radius4x))
    config.set('overlay', 'radius6x', str(radius6x))
    config.set('overlay', 'radius10x', str(radius10x))
    config.set('overlay', 'hairwidth1x', str(hairwidth1x))
#    config.set('overlay', 'hairwidth4x', str(hairwidth4x))
    config.set('overlay', 'hairwidth6x', str(hairwidth6x))
    config.set('overlay', 'hairwidth10x', str(hairwidth10x))
    config.set('overlay', 'shotcamvideo', str(shotcamvideo))
    config.set('overlay', 'opacity', str(opacity))
    config.set('main', 'width', str(width))
    config.set('main', 'height', str(height))
    config.set('camera', 'iso', str(iso))
    config.set('camera', 'exposure_mode', str(exposure_mode))
    config.set('camera', 'awb_mode', str(awb_mode))
    config.set('camera', 'brightness', str(brightness))
    config.set('camera', 'contrast', str(contrast))
    config.set('camera', 'saturation', str(saturation))
    config.set('camera', 'sharpness', str(sharpness))
    config.set('camera', 'effects', str(effects))


    # Remove old file before writing a new one
    if os.path.exists(fileloc):
        os.remove(fileloc)

    # Write the new config file
    with open(fileloc, 'w') as f:
        config.write(f)


#def saveSettings(fileloc):
#    print("Savings " + fileloc + " using current settings.")
#    config.add_section('main')
#    config.add_section('overlay')
#    config.set('overlay', 'xcenter', xcenter)
#    config.set('overlay', 'ycenter', ycenter)
#    config.set('overlay', 'color', curcol)
#    config.set('overlay', 'pattern', curpat2)
#    config.set('overlay', 'radius1x', radius1x)
#    config.set('overlay', 'radius4x', radius4x)
#    config.set('overlay', 'radius6x', radius6x)
#    config.set('overlay', 'hairwidth1x', hairwidth1x)
#    config.set('overlay', 'hairwidth4x', hairwidth4x)
#    config.set('overlay', 'hairwidth6x', hairwidth6x)
#    config.set('overlay', 'shotcamvideo', shotcamvideo)
#    config.set('overlay', 'opacity', opacity)
#    config.set('overlay', 'brightness', brightness)
#    config.set('main', 'width', width)
#    config.set('main', 'height', height)
#    # write default settings to new config file:
#    open(fileloc, 'w').close()  # Clears the file
#    with open(fileloc, 'w') as f:
#        config.write(f)

# try to read settings from config file; if it doesn't exist
# create one from defaults & use same defaults for this run:
try:
    with open(configfile) as f:
        config = ConfigParserWithComments(cdefaults)
        config.readfp(f)
except IOError:
    config = ConfigParserWithComments(cdefaults)
    CreateConfigFromDef(configfile,cdefaults)

# retrieve settings from config parser:
width = int(config.get('main', 'width'))
#xcenter = width//2
height = int(config.get('main', 'height'))
#ycenter = height//2
print("Set resolution: " + str(width) + "x" + str(height))
# make sure width is a multiple of 32 and height
# is a multiple of 16:
if (width%32) > 0 or (height%16) > 0:
    print("Rounding down set resolution to match camera block size:")
    width = width-(width%32)
    height = height-(height%16)
    print("New resolution: " + str(width) + "x" + str(height))
    xcenter = (width//2)-1
    ycenter = (height//2)-1
curcol = config.get('overlay', 'color')
curpat2 = int(config.get('overlay', 'pattern'))
xcenter = int(config.get('overlay', 'xcenter'))
ycenter = int(config.get('overlay', 'ycenter'))
radius1x = int(config.get('overlay', 'radius1x'))
#radius4x = int(config.get('overlay', 'radius4x'))
radius6x = int(config.get('overlay', 'radius6x'))
radius10x = int(config.get('overlay', 'radius10x'))

opacity = int(config.get('overlay', 'opacity'))
alphaValue = opacity
hairwidth1x = int(config.get('overlay', 'hairwidth1x'))
#hairwidth4x = int(config.get('overlay', 'hairwidth4x'))
hairwidth6x = int(config.get('overlay', 'hairwidth6x'))
hairwidth10x = int(config.get('overlay', 'hairwidth10x'))
shotcamvideo = str(config.get('overlay', 'shotcamvideo'))

iso = int(config.get('camera', 'iso'))
exposure_mode = str(config.get('camera', 'exposure_mode'))
awb_mode = str(config.get('camera', 'awb_mode'))
brightness = int(config.get('camera', 'brightness'))
contrast = int(config.get('camera', 'contrast'))
saturation = int(config.get('camera', 'saturation'))
sharpness = int(config.get('camera', 'sharpness'))
effects = str(config.get('camera', 'effects'))

print("shotcamvideo: "+shotcamvideo)
#leftright = int(config.get('overlay', 'leftright'))
#updown = int(config.get('overlay', 'updown'))
hairwidth = hairwidth1x
radius = radius1x

#curpat2 = 1
# map colors:
colors = {
        'white': (255,255,255),
        'red': (255,0,0),
        'green': (0,255,0),
        'blue': (0,0,255),
        'yellow': (255,255,0),
        }

# initialize toggle for on/off button and gui state:
togsw = 1
guivisible = 1


counter = 0

# function to call when middle button is pressed (GPIO 23):
def togglepattern(var):
    global togsw,o,curpat2,col,ovl,gui,alphaValue
    # if overlay is inactive, ignore button:
    if togsw == 0:
        print("Pattern button pressed, but ignored --- Crosshair not visible.")
    # if overlay is active, drop it, change pattern, then show it again
    else:
        curpat2 = var
        print("Set new pattern: " + str(curpat2))
        if curpat2 > maxpat:     # this number must be adjusted to number of available patterns!
            curpat2 = 1
        if curpat2 < 1:
            curpat2 = 10
        if guivisible == 0:
            # reinitialize array:
            ovl = np.zeros((height, width, 3), dtype=np.uint8)
            patternswitcher(ovl,0)
            if 'o' in globals():
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(ovl), layer=3, alpha=alphaValue)
        else:
            # reinitialize array
            gui = np.zeros((height, width, 3), dtype=np.uint8)
            #creategui(gui)
            if infoVisible:
                patternswitcher(gui,1)
            elif infoVisible == False:
                patternswitcher(gui,0)
            #patternswitch(gui,1)
            if 'o' in globals():
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(gui), layer=3, alpha=alphaValue)
    return



def togglepattern3():
    global togsw,o,curpat,col,ovl,gui,alphaValue,ycenter,zoomcount, hairwidth
    # if overlay is inactive, ignore button:
    if togsw == 0:
        print("Pattern button pressed, but ignored --- Crosshair not visible.")
    # if overlay is active, drop it, change pattern, then show it again
    else:
        if guivisible == 0:
	    # reinitialize array:
            ovl = np.zeros((height, width, 3), dtype=np.uint8)
            patternswitcherZoomIn(ovl,0)
            if 'o' in globals():
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(ovl), layer=3, alpha=alphaValue)
        else:
            # reinitialize array
            gui = np.zeros((height, width, 3), dtype=np.uint8)
            patternswitcherZoomIn(gui,1)
            if 'o' in globals():
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(gui), layer=3, alpha=alphaValue)
    return


def togglepattern4(roll):
    global togsw,o,curpat,col,ovl,gui,alphaValue,ycenter,xcenter,zoomcount #,camera
    if(roll < -1 and roll >= -1.5 and camera.rotation != 90):
        print("left")
        camera.rotation = 90
        # Get the new resolution
        new_resolution = camera.resolution
        print("New Resolution:", new_resolution)
        update_zoom()
#        print("Resolution: "+str(camera.resolution[0],camera.resolution[1])
        #camera.resolution = (1280, 720)
#        time.sleep(0.5)
#        if zoomcount == 0:
#            xcenter += 10
#        elif zoomcount == 11:
#            xcenter += 40
#        else:
#            xcenter += 60
#        update_zoom()
#        togglepattern3()
#        camera.resolution = (camera.resolution[0], camera.resolution[1])  # Reapply resolution
    elif(roll > 1 and roll <= 1.5 and camera.rotation != 270):
        print("right")
        camera.rotation = 270
        # Get the new resolution
        new_resolution = camera.resolution
        print("New Resolution:", new_resolution)
        update_zoom()
#        print("Resolution: "+str(camera.resolution)
        #camera.resolution = (1280, 720)
#        time.sleep(0.5)

#        if zoomcount == 0:
#            xcenter -= 10
#        elif zoomcount == 11:
#            xcenter -= 40
#        else:
#            xcenter -= 60

#        update_zoom()
#        togglepattern3()
#        camera.resolution = (camera.resolution[0], camera.resolution[1])  # Reapply resolution
    elif(roll >= -.25 and roll <= .25 and camera.rotation != 180):
        camera.rotation = 180
        #camera.resolution = (1280, 720)
        #camera.rotation = 180
#        time.sleep(0.5)
        print("normal")
        xcenter = prevxcenter
#        update_zoom()
#        togglepattern3()
    else:
        return
#    time.sleep(.25)
    togglepattern3()
    # if overlay is inactive, ignore button:
    if togsw == 0:
        print("Pattern button pressed, but ignored --- Crosshair not visible.")
    # if overlay is active, drop it, change pattern, then show it again
    else:
        if guivisible == 0:
            # reinitialize array:
            ovl = np.zeros((height, width, 3), dtype=np.uint8)
            patternswitcherZoomIn(ovl,0)
            if 'o' in globals():
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(ovl), layer=3, alpha=alphaValue)
        else:
            # reinitialize array
            gui = np.zeros((height, width, 3), dtype=np.uint8)
            patternswitcherZoomIn(gui,1)
            if 'o' in globals():
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(gui), layer=3, alpha=alphaValue)
    return

def clear_screen():
    """Stops the camera preview, waits, and restarts it to clear any artifacts."""
    global camera

    camera.stop_preview()  # Stop current preview
    time.sleep(0.25)        # Wait to ensure it's cleared
    camera.start_preview() # Restart preview
    print("Screen cleared!")
    togglepattern3()

def patternswitcherZoomIn(target,guitoggle):
    global o, zoomcount, ycenter, hairwidth, radius
    # first remove existing overlay:
    if 'o' in globals() and o != None:
#        camera.remove_overlay(o)
        try:
            camera.remove_overlay(o)
        except picamera.PiCameraValueError:
            print("Overlay does not belong to this instance, skipping removal.")
            camera.close()
            sys.exit(0)
            #clear_screen()
            # Create a blank (black/transparent) overlay
            #blank_overlay = np.zeros((height, width, 3), dtype=np.uint8)
            #o = camera.add_overlay(bytes(blank_overlay), layer=3, alpha=255)  # Fully transparent
            #time.sleep(0.1)  # Allow time for the screen to refresh
            #camera.remove_overlay(o)  # Now safely remove it
            #o = None
    if zooms['zoom_xy'] == zooms['zoom_xy_max']:
        print("zoom at max")
    # cycle through possible patterns:
    if curpat2 == 1:
        pattern1(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 2:
        pattern2(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 3:
        pattern3(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 4:
        pattern4(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 5:
        pattern5(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 6:
        pattern6(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 7:
        pattern7(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 8:
        pattern8(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 9:
        pattern9(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 10:
        pattern10(target, width, height, xcenter, ycenter, radius, col)
    # Add the overlay directly into layer 3 with transparency;
    # we can omit the size parameter of add_overlay as the
    # size is the same as the camera's resolution
    o = camera.add_overlay(bytes(target), layer=3, alpha=alphaValue)
    return

def patternswitcherZoomOut(target,guitoggle):
    global o, zoomcount, xcenter, ycenter, ycenterList, radius
    # first remove existing overlay:
    if 'o' in globals() and o != None:
#        camera.remove_overlay(o)
        try:
            camera.remove_overlay(o)
        except picamera.PiCameraValueError:
            print("Overlay does not belong to this instance, skipping removal.")
            camera.close()
            sys.exit(0)
            #clear_screen()
            # Create a blank (black/transparent) overlay
            #blank_overlay = np.zeros((height, width, 3), dtype=np.uint8)
            #o = camera.add_overlay(bytes(blank_overlay), layer=3, alpha=255)  # Fully transparent
            #time.sleep(0.1)  # Allow time for the screen to refresh
            #camera.remove_overlay(o)  # Now safely remove it
            #o = None
    if zooms['zoom_xy'] == zooms['zoom_xy_min']:
        print("zoom at min")
    # cycle through possible patterns:
    if curpat2 == 1:
        pattern2(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 2:
        pattern3(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 3:
        pattern5(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 4:
        pattern6(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 5:
        pattern7(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 6:
        pattern6(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 7:
        pattern7(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 8:
        pattern8(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 9:
        pattern9(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 10:
        pattern10(target, width, height, xcenter, ycenter, radius, col)
    # Add the overlay directly into layer 3 with transparency;
    # we can omit the size parameter of add_overlay as the
    # size is the same as the camera's resolution
    o = camera.add_overlay(bytes(target), layer=3, alpha=alphaValue)
    return

# function to call when low button is pressed (GPIO 18):
def togglecolor():
    global togsw,o,curcol,col,ovl,gui,alphaValue,infoVisible,camera
    # step up the color to next in list
    curcol = colorcycle(colors,curcol)
    # map colorname to RGB value for new color
    col = colormap(curcol)
    # if overlay is inactive, ignore button:
    if togsw == 0:
        print("Color button pressed, but ignored --- Crosshair not visible.")
    # if overlay is active, drop it, change color, then show it again
    else:
        print("Set new color: " + str(curcol) + "  RGB: " + str(col))
        if guivisible == 0:
            # reinitialize array:
            ovl = np.zeros((height, width, 3), dtype=np.uint8)
            patternswitcher(ovl,0)
            if 'o' in globals():
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(ovl), layer=3, alpha=alphaValue)
        else:
            # reinitialize array
            gui = np.zeros((height, width, 3), dtype=np.uint8)
            if infoVisible:
                patternswitcher(gui,1) 
            elif infoVisible == False:
                patternswitcher(gui,0) 
            if 'o' in globals():
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(gui), layer=3, alpha=alphaValue)
    return



#def loadFile():
#    global xcenter, ycenter
#    with open(zerofile) as f:
#        data = dict(filter(None, csv.reader(f)))
#    ycenter = list(data.keys())[0]
#    xcenter = list(data.values())[0]
#    xcenter = int(xcenter)
#    ycenter = int(ycenter)
#    print("X: "+str(xcenter))
#    print("Y: "+str(ycenter))
#    togglepattern3()

#def writeZeroFile(xaxis, yaxis):
#    with open(zerofile, 'w') as file:
#        writer = csv.writer(file)
#        writer.writerow([xaxis, yaxis])

# map text color names to RGB:
def colormap(col):
    return colors.get(col, (255,255,255))    # white is default

# cycle through color list starting from current color:
def colorcycle(self, value, default='white'):
    # create an enumerator for the entries and step it up
    for i, item in enumerate(self):
        if item == value:
            i += 1
            # if end of color list is reached, jump to first in list
            if i >= len(self):
                i = 0
            return list(self.keys())[i]
    # if function fails for some reason, return white
    return default

############################################################

def patternswitcher(target,guitoggle):
    global o, hairwidth, radius
    # first remove existing overlay:
    if 'o' in globals():
        camera.remove_overlay(o)
    # cycle through possible patterns:
    if curpat2 == 1:
        pattern1(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 2:
        pattern2(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 3:
        pattern3(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 4:
        pattern4(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 5:
        pattern5(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 6:
        pattern6(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 7:
        pattern7(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 8:
        pattern8(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 9:
        pattern9(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 10:
        pattern10(target, width, height, xcenter, ycenter, radius, col)
    # Add the overlay directly into layer 3 with transparency;
    # we can omit the size parameter of add_overlay as the
    # size is the same as the camera's resolution
    o = camera.add_overlay(bytes(target), layer=3, alpha=alphaValue)
    return


############################################################

# create array for the overlay:
ovl = np.zeros((height, width, 3), dtype=np.uint8)
font = cv2.FONT_HERSHEY_PLAIN
col = colormap(curcol)
# create array for a bare metal gui and text:
gui = np.zeros((height, width, 3), dtype=np.uint8)
gui1 = ' Nerf Landwarrior'
gui2 = ' Version 1.0'
#gui3 = ' button  = cycle distance'
#gui4 = ' range: '+str(gunRange)
#gui5 = ' s/r     = save/revert settings'

#leftright = 32767
#updown = 33023

prevxcenter = xcenter

with picamera.PiCamera() as camera:
    camera.resolution = (width, height)
    print(stream)
    stream = picamera.PiCameraCircularIO(camera, seconds=10)
    print(stream)
    NewCounter1 = 0
    camera.vflip = True
    camera.hflip = True
    camera.resolution = (width, height)
    camera.framerate = 30
    camera.rotation = 180
    camera.iso = iso
    camera.exposure_mode = exposure_mode
    camera.awb_mode = awb_mode
    camera.brightness = brightness
    camera.sharpness = sharpness
    camera.contrast = contrast
    camera.saturation = saturation
    camera.image_effect = effects
    # Improve exposure and white balance
    camera.exposure_mode = 'auto' #'sports'
    camera.awb_mode = 'auto'
    #camera.annotate_foreground = Color('green')
    filename = get_file_name()
    camera.start_recording(filename)
    # set this to 1 when switching to fullscreen output
    camera.preview_fullscreen = 1
    camera.start_preview()
    togglepattern(curpat2)
    time.sleep(1)
    try:
        t1 = threading.Thread(target=annotate_thread, name='t1')
        t1.start()
        patternswitcher(gui,1)
        for event in gamepad.read_loop():
            if event.type == ecodes.EV_ABS and zoomcount == 0: 
#               camera.annotate_background = Color('white')
                absevent = categorize(event) 
                if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_X':
                    print(absevent.event.value)
                    if(absevent.event.value > 65000 and camera.rotation == 180 and stop_thread):
                        print("Right - Next Option")
                        selected_option_index += 1  # Move to next option
                        # Ensure index wraps around valid range
                        options = data[list(data.keys())[index]]["options"]
                        selected_option_index = max(0, min(selected_option_index, len(options) - 1))
                        animatemenu()
                    elif(absevent.event.value > 65000 and camera.rotation == 180):
                        print("right")
                        xcenter = xcenter +5
                        prevxcenter = xcenter
                        togglepattern3()
                    elif (absevent.event.value < 500 and camera.rotation == 180 and stop_thread):
                        print("Left - Previous Option")
                        selected_option_index -= 1  # Move to previous option
                        # Ensure index wraps around valid range
                        options = data[list(data.keys())[index]]["options"]
                        selected_option_index = max(0, min(selected_option_index, len(options) - 1))
                        animatemenu()
                    elif (absevent.event.value < 500 and camera.rotation == 180):
                        print("left")
                        xcenter = xcenter -5
                        prevxcenter = xcenter
                        togglepattern3()
                        # Ensure index wraps around valid range
                        #options = data[list(data.keys())[index]]["options"]
                        #selected_option_index = max(0, min(selected_option_index, len(options) - 1))
                        #animatemenu()


                if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_Y':
                    print(absevent.event.value)
                    if(absevent.event.value > 65000 and camera.rotation == 180 and stop_thread):
                        print("down")
                        selected_option_index = 0
                        if(index < len(list(data.keys()))-1):
                            index += 1
                        else:
                            index = 0

                        # Preselect the correct index for `radius1x` when switching to "radius1x"
                        if list(data.keys())[index] == "radius1x":
                            options = data["radius1x"]["options"]
                            if radius1x in options:
                                selected_option_index = options.index(radius1x)
                            else:
                                selected_option_index = 0  # Default if not found
                        # Preselect the correct index for `radius1x` when switching to "radius1x"
                        if list(data.keys())[index] == "hairwidth1x":
                            options = data["hairwidth1x"]["options"]
                            if hairwidth1x in options:
                                selected_option_index = options.index(hairwidth1x)
                            else:
                                selected_option_index = 0  # Default if not found



                        # Preselect the correct index for `radius6x` when switching to "radius6x"
                        if list(data.keys())[index] == "radius6x":
                            options = data["radius6x"]["options"]
                            if radius6x in options:
                                selected_option_index = options.index(radius6x)
                            else:
                                selected_option_index = 0  # Default if not found
                        # Preselect the correct index for `radius6x` when switching to "radius6x"
                        if list(data.keys())[index] == "hairwidth6x":
                            options = data["hairwidth6x"]["options"]
                            if hairwidth6x in options:
                                selected_option_index = options.index(hairwidth6x)
                            else:
                                selected_option_index = 0  # Default if not found

                        # Preselect the correct index for `radius10x` when switching to "radius10x"
                        if list(data.keys())[index] == "radius10x":
                            options = data["radius10x"]["options"]
                            if radius10x in options:
                                selected_option_index = options.index(radius10x)
                            else:
                                selected_option_index = 0  # Default if not found
                        # Preselect the correct index for `radius10x` when switching to "radius10x"
                        if list(data.keys())[index] == "hairwidth10x":
                            options = data["hairwidth10x"]["options"]
                            if hairwidth10x in options:
                                selected_option_index = options.index(hairwidth10x)
                            else:
                                selected_option_index = 0  # Default if not found

                        # Preselect the correct index for `iso` when switching to "iso"
                        if list(data.keys())[index] == "shotcam":
                            options = data["shotcam"]["options"]
                            if shotcamvideo in options:
                                selected_option_index = options.index(shotcamvideo)
                            else:
                                selected_option_index = 0  # Default if not found



                        # Preselect the correct index for `iso` when switching to "iso"
                        if list(data.keys())[index] == "iso":
                            options = data["iso"]["options"]
                            if camera.iso in options:
                                selected_option_index = options.index(camera.iso)
                            else:
                                selected_option_index = 0  # Default if not found
                        # Preselect the correct index for `alphaValue` when switching to "opacity"
                        if list(data.keys())[index] == "opacity":
                            options = data["opacity"]["options"]
                            if alphaValue in options:
                                selected_option_index = options.index(opacity)
                                print("OPACITY:"+str(opacity))
                            else:
                                selected_option_index = 0  # Default if not found
                        # Preselect the correct index for `brightness` when switching to "brightness"
                        if list(data.keys())[index] == "brightness":
                            options = data["brightness"]["options"]
                            if brightness in options:
                                selected_option_index = options.index(brightness)
                            else:
                                selected_option_index = 0  # Default if not found
                        # Preselect the correct index for 'contrast' when switching to "contrast"
                        if list(data.keys())[index] == "contrast":
                            options = data["contrast"]["options"]
                            if camera.contrast in options:
                                selected_option_index = options.index(camera.contrast)
                            else:
                                selected_option_index = 0  # Default if not found

                        # Preselect the correct index for 'saturation' when switching to "saturation"
                        if list(data.keys())[index] == "saturation":
                            options = data["saturation"]["options"]
                            if camera.saturation in options:
                                selected_option_index = options.index(camera.saturation)
                            else:
                                selected_option_index = 0  # Default if not found

                        # Preselect the correct index for 'sharpness' when switching to "sharpness"
                        if list(data.keys())[index] == "sharpness":
                            options = data["sharpness"]["options"]
                            if camera.sharpness in options:
                                selected_option_index = options.index(camera.sharpness)
                            else:
                                selected_option_index = 0  # Default if not found

                        # Preselect the correct index for 'effects' when switching to "effects"
                        if list(data.keys())[index] == "effects":
                            options = data["effects"]["options"]
                            if camera.image_effect in options:
                                selected_option_index = options.index(camera.image_effect)
                            else:
                                selected_option_index = 0  # Default if not found


                        # Preselect the correct index for 'exposure_mode' when switching to "exposure_mode"
                        if list(data.keys())[index] == "exposure_mode":
                            options = data["exposure_mode"]["options"]
                            if camera.exposure_mode in options:
                                selected_option_index = options.index(camera.exposure_mode)
                            else:
                                selected_option_index = 0  # Default if not found
                        # Preselect the correct index for 'awb_mode' when switching to "awb_mode"
                        if list(data.keys())[index] == "awb_mode":
                            options = data["awb_mode"]["options"]
                            if camera.awb_mode in options:
                                selected_option_index = options.index(camera.awb_mode)
                            else:
                                selected_option_index = 0  # Default if not found
                        animatemenu()
                    elif(absevent.event.value > 65000 and camera.rotation == 180):
                        print("down")
                        ycenter = ycenter +5
                        togglepattern3()
                    elif (absevent.event.value < 500 and camera.rotation == 180 and stop_thread):
                        print("up")
                        selected_option_index = 0
                        if(index > 0):
                            index -= 1
                        else:
                            index = len(list(data.keys()))-1
                        # Preselect the correct index for `iso` when switching to "iso"
                        if list(data.keys())[index] == "iso":
                            options = data["iso"]["options"]
                            if camera.iso in options:
                                selected_option_index = options.index(camera.iso)
                            else:
                                selected_option_index = 0  # Default if not found
                        # Preselect the correct index for `alphaValue` when switching to "opacity"
                        if list(data.keys())[index] == "opacity":
                            options = data["opacity"]["options"]
                            if alphaValue in options:
                                selected_option_index = options.index(opacity)
                                print("OPACITY:"+str(opacity))
                            else:
                                selected_option_index = 0  # Default if not found
                        # Preselect the correct index for `radius1x` when switching to "radius1x"
                        if list(data.keys())[index] == "radius1x":
                            options = data["radius1x"]["options"]
                            if radius1x in options:
                                selected_option_index = options.index(radius1x)
                            else:
                                selected_option_index = 0  # Default if not found
                        # Preselect the correct index for `radius1x` when switching to "radius1x"
                        if list(data.keys())[index] == "hairwidth1x":
                            options = data["hairwidth1x"]["options"]
                            if hairwidth1x in options:
                                selected_option_index = options.index(hairwidth1x)
                            else:
                                selected_option_index = 0  # Default if not found
                        # Preselect the correct index for `radius6x` when switching to "radius6x"
                        if list(data.keys())[index] == "radius6x":
                            options = data["radius6x"]["options"]
                            if radius6x in options:
                                selected_option_index = options.index(radius6x)
                            else:
                                selected_option_index = 0  # Default if not found
                        # Preselect the correct index for `radius6x` when switching to "radius6x"
                        if list(data.keys())[index] == "hairwidth6x":
                            options = data["hairwidth6x"]["options"]
                            if hairwidth6x in options:
                                selected_option_index = options.index(hairwidth6x)
                            else:
                                selected_option_index = 0  # Default if not found

                        # Preselect the correct index for `radius10x` when switching to "radius10x"
                        if list(data.keys())[index] == "radius10x":
                            options = data["radius10x"]["options"]
                            if radius10x in options:
                                selected_option_index = options.index(radius10x)
                            else:
                                selected_option_index = 0  # Default if not found
                        # Preselect the correct index for `radius10x` when switching to "radius10x"
                        if list(data.keys())[index] == "hairwidth10x":
                            options = data["hairwidth10x"]["options"]
                            if hairwidth10x in options:
                                selected_option_index = options.index(hairwidth10x)
                            else:
                                selected_option_index = 0  # Default if not found
                        # Preselect the correct index for `brightness` when switching to "brightness"
                        if list(data.keys())[index] == "brightness":
                            options = data["brightness"]["options"]
                            if brightness in options:
                                selected_option_index = options.index(brightness)
                            else:
                                selected_option_index = 0  # Default if not found
                        # Preselect the correct index for 'contrast' when switching to "contrast"
                        if list(data.keys())[index] == "contrast":
                            options = data["contrast"]["options"]
                            if camera.contrast in options:
                                selected_option_index = options.index(camera.contrast)
                            else:
                                selected_option_index = 0  # Default if not found

                        # Preselect the correct index for 'saturation' when switching to "saturation"
                        if list(data.keys())[index] == "saturation":
                            options = data["saturation"]["options"]
                            if camera.saturation in options:
                                selected_option_index = options.index(camera.saturation)
                            else:
                                selected_option_index = 0  # Default if not found

                        # Preselect the correct index for 'sharpness' when switching to "sharpness"
                        if list(data.keys())[index] == "sharpness":
                            options = data["sharpness"]["options"]
                            if camera.sharpness in options:
                                selected_option_index = options.index(camera.sharpness)
                            else:
                                selected_option_index = 0  # Default if not found

                        # Preselect the correct index for 'effects' when switching to "effects"
                        if list(data.keys())[index] == "effects":
                            options = data["effects"]["options"]
                            if camera.image_effect in options:
                                selected_option_index = options.index(camera.image_effect)
                            else:
                                selected_option_index = 0  # Default if not found


                        # Preselect the correct index for 'exposure_mode' when switching to "exposure_mode"
                        if list(data.keys())[index] == "exposure_mode":
                            options = data["exposure_mode"]["options"]
                            if camera.exposure_mode in options:
                                selected_option_index = options.index(camera.exposure_mode)
                            else:
                                selected_option_index = 0  # Default if not found
                        # Preselect the correct index for 'awb_mode' when switching to "awb_mode"
                        if list(data.keys())[index] == "awb_mode":
                            options = data["awb_mode"]["options"]
                            if camera.awb_mode in options:
                                selected_option_index = options.index(camera.awb_mode)
                            else:
                                selected_option_index = 0  # Default if not found
                        animatemenu()
                    elif (absevent.event.value < 500 and camera.rotation == 180):
                        print("up")
                        ycenter = ycenter -5
                        togglepattern3()

            if event.value == 0:
                prevhold = None


            #if(prevhold != event.code):
            #    prevhold = None
            if event.value == 1:
                #prevhold = None
                if event.code == start:
                    prevhold = None
                    print("start")
                    print("prevhold: "+str(prevhold))
                    print("busy: "+str(busy))
                    subprocess.Popen(["/usr/bin/raspi2png", "-p", "/mnt/usb_share/" + get_file_name_pic()])
#                    os.system("/usr/bin/raspi2png -p /mnt/usb_share/"+get_file_name_pic())
                if event.code == yBtn:
                    print("Y")
                    togglepattern(curpat2+1)
                if event.code == aBtn:
                    print("A")
                    stop_thread = False
                    camera.annotate_text = ""
                    toggleText = not(toggleText)
                    #for single battery readings
                    #bus_voltage = read_voltage()
                    #power_percent = (bus_voltage - V_MIN) / (V_MAX - V_MIN) * 100
                    #power_percent = max(0, min(100, power_percent))  # Clamp between 0-100%
                if event.code == bBtn:
                    print("B")
                    togglecolor()
#                    camera.annotate_foreground = Color('red')
                if event.code == xBtn:
                    print("X")
                    toggleStability = not toggleStability

            if event.value == 2:
                if event.code == yBtn:
                    print("hY")
                if event.code == aBtn and prevhold != event.code:
                    print("hA")
                    #here
                    toggleText = False
                    toggleStability = False
                    stop_thread = True
                    animatemenu()
                    prevhold = event.code
                if event.code == bBtn:
                    print("hB")
                if event.code == xBtn:
                    print("hX")

#                prevhold = event.code

            if event.value == 1:
                if event.code == select:
                    print("select")
                    saveSettings(configfile)
#                    camera.annotate_text_size = 135
                    camera.annotate_text = "\nSAVED"
                    camera.annotate_text = "\nSAVED"
                    camera.annotate_text = "\nSAVED"
                if event.code == lTrig:
                    print("left bumper")
                    zoom_out()
                    #togglepattern3()
                if event.code == rTrig:
                    print("right bumper")
                    zoom_in()
                    #togglepattern3()
            if event.value == 2 and not busy: #and prevhold != start:
                if event.code == start and prevhold != start:
                    print("hstart")
                    camera.annotate_text = "\nShot Cam"
                    prevhold = event.code
                    busy = True
                    shotcam()
#                    prevhold = event.code
                    #if(shotcamvideo != "True" and shotcamvideo != "true"):
                    #    busy = False
                if event.code == lTrig and zoomcount > 0:
                    print("hleft bumper")
                    zoom_out()
                    #togglepattern3()
                if event.code == rTrig and zoomcount < 15:
                    print("hright bumper")
                    zoom_in()
                    #togglepattern3()
#                prevhold = event.code
                busy = False
        if(prevhold == start):
            prevhold = None

    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
        print("\nExiting Program")
        thread_exit = True  # Signal thread to stop
        t1.join()  # Wait for thread to terminate
    finally:
        camera.close()               # clean up camera
        GPIO.cleanup()               # clean up GPIO
