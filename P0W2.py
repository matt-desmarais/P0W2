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

# pattern1: Bruker style crosshair with circles and ticks
def pattern1( arr, width, height, x, y, rad, col ):
    global hairwidth
    cv2.line(arr,(0,y),(width,y),(col),(hairwidth))
    cv2.line(arr,(x,0),(x,height),col,hairwidth)
    i = 0
    for i in range(1, 8): 
        cv2.circle(arr,(x,y),i*rad,col,hairwidth)
        i += 1
    # ticks on the horizontal axis:
    intervalh = np.arange(0,width,float(rad)/10)
    j = 0
    for i in intervalh:
        # make every 5th tick longer, omit every 10th tick:
        diff = int(round(i))
        if j%5 == 0:    
            if not j%10 == 0:
                cv2.line(arr,(x+diff,y-4),(x+diff,y+4),col,hairwidth)
                cv2.line(arr,(x-diff,y-4),(x-diff,y+4),col,hairwidth)
        else:
            cv2.line(arr,(x+diff,y-2),(x+diff,y+3),col,hairwidth)
            cv2.line(arr,(x-diff,y-2),(x-diff,y+3),col,hairwidth)
        j += 1
    # ticks on the vertical axis:
    intervalv = np.arange(0,height,float(rad)/10)
    l = 0
    for k in intervalv:
        # make every 5th and 10th tick longer:
        diff = int(round(k))
        if l%5 == 0:    
            if l%10 == 0:
                cv2.line(arr,(x-6,y+diff),(x+6,y+diff),col,hairwidth)
                cv2.line(arr,(x-6,y-diff),(x+6,y-diff),col,hairwidth)
            else:
                cv2.line(arr,(x-4,y+diff),(x+4,y+diff),col,hairwidth)
                cv2.line(arr,(x-4,y-diff),(x+4,y-diff),col,hairwidth)
        else:
            cv2.line(arr,(x-2,y+diff),(x+2,y+diff),col,hairwidth)
            cv2.line(arr,(x-2,y-diff),(x+2,y-diff),col,hairwidth)
        l += 1
    return    

# pattern2: simple crosshair with ticks
def pattern2( arr, width, height, x, y, rad, col ):
    global hairwidth
    width = int(width)
    height = int(height)
    x = int(x)
    y = int(y)
    # cv2.circle(arr,(x,y),rad,col,1)
    cv2.line(arr,(0,int(y)),(int(width),int(y)),col,hairwidth)
    cv2.line(arr,(int(x),0),(int(x),int(height)),col,hairwidth)
    # ticks on the horizontal axis:
    intervalh = np.arange(0,width,float(rad)/10)
    j = 0
    for i in intervalh:
        # make every 5th and 10th tick longer:
        diff = int(round(i))
        if j%5 == 0:    
            if j%10 == 0:
                cv2.line(arr,(x+diff,y-6),(x+diff,y+6),col,hairwidth)
                cv2.line(arr,(x-diff,y-6),(x-diff,y+6),col,hairwidth)
            else:
                cv2.line(arr,(x+diff,y-4),(x+diff,y+4),col,hairwidth)
                cv2.line(arr,(x-diff,y-4),(x-diff,y+4),col,hairwidth)
        else:
            cv2.line(arr,(x+diff,y-2),(x+diff,y+3),col,hairwidth)
            cv2.line(arr,(x-diff,y-2),(x-diff,y+3),col,hairwidth)
        j += 1
    # ticks on the vertical axis:
    intervalv = np.arange(0,height,float(rad)/10)
    l = 0
    for k in intervalv:
        # make every 5th and 10th tick longer:
        diff = int(round(k))
        if l%5 == 0:    
            if l%10 == 0:
                cv2.line(arr,(x-6,y+diff),(x+6,y+diff),col,hairwidth)
                cv2.line(arr,(x-6,y-diff),(x+6,y-diff),col,hairwidth)
            else:
                cv2.line(arr,(x-4,y+diff),(x+4,y+diff),col,hairwidth)
                cv2.line(arr,(x-4,y-diff),(x+4,y-diff),col,hairwidth)
        else:
            cv2.line(arr,(x-2,y+diff),(x+2,y+diff),col,hairwidth)
            cv2.line(arr,(x-2,y-diff),(x+2,y-diff),col,hairwidth)
        l += 1
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
    cv2.line(arr,(x-10,y),(x+10,y),col,hairwidth)
    cv2.line(arr,(x,y-10),(x,y+10),col,hairwidth)
    return

# pattern8: small center crosshair without center
def pattern8( arr, width, height, x, y, rad, col ):
    global hairwidth
    cv2.line(arr,(x-20,y),(x-13,y),col,hairwidth)
    cv2.line(arr,(x,y-20),(x,y-13),col,hairwidth)
    cv2.line(arr,(x+13,y),(x+20,y),col,hairwidth)
    cv2.line(arr,(x,y+13),(x,y+20),col,hairwidth)
    return

# pattern9: only a dot
def pattern9( arr, width, height, x, y, rad, col ):
    global hairwidth
    cv2.circle(arr,(x,y),2,col,2)
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
toggleText = False

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
    'zoom_wh_max' : 0.2
}

def read_voltage():
    """Reads and correctly formats bus voltage from INA219."""
    raw_data = bus.read_word_data(I2C_ADDR, REG_BUSVOLTAGE)
    # Swap byte order (INA219 sends data in little-endian format)
    raw_data = ((raw_data << 8) & 0xFF00) | (raw_data >> 8)
    # Voltage is stored in bits 3-15, so shift right by 3 and multiply by 4mV
    return (raw_data >> 3) * 0.004

def shotcam():
    global camera, filename, busy, process, curcol
    busy = True
    # Get the filename
    shotcam_file = "/mnt/usb_share/"+get_shotcam_file()
    # FFmpeg command for overlaying crosshairs
    ffmpeg_command = (
        'sudo ffmpeg -i trimmed.mp4 -vf "drawbox=x={xcenter}:y=0:w=2:h=720:color={curcol}@0.8:t=fill,'
        'drawbox=x=0:y={ycenter}:w=1280:h=2:color={curcol}@0.8:t=fill" -preset ultrafast -c:a copy -threads 1 "{shotcam_file}"'
    ).format(xcenter=xcenter, ycenter=ycenter, shotcam_file=shotcam_file, curcol=curcol)
    print("🔹 Trimming last 5MB from video file...")
    subprocess.run(f"tail -c 15000000 {filename} > temp.h264", shell=True, check=True)
    # Validate temp.h264 to check for corruption
    print("🔹 Checking integrity of temp.h264...")
    ffprobe_cmd = "ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height -of json temp.h264"
    result = subprocess.run(ffprobe_cmd, shell=True, capture_output=True, text=True)

    if "codec_name" not in result.stdout:
        print("❌ Error: temp.h264 is corrupted or missing frames.")
        busy = False
        return

    print("✅ temp.h264 is valid!")

    # Fix timestamps in H.264 file to prevent playback issues
    print("🔹 Fixing timestamps in temp.h264...")
    subprocess.run("ffmpeg -y -fflags +genpts -i temp.h264 -c:v copy temp_fixed.h264", shell=True, check=True)

    # Convert raw H.264 to MP4 with proper metadata
    print("🔹 Converting temp_fixed.h264 to MP4...")
    temp_file = "/mnt/usb_share/"+get_temp_mp4_file_name()
    subprocess.run("sudo ffmpeg -y -framerate 30 -i temp_fixed.h264 -c:v copy -movflags +faststart "+temp_file, shell=True, check=True)


    print("🔹 Extracting last 10 seconds using -sseof...")
    subprocess.run(f"ffmpeg -y -sseof -10.5 -i "+temp_file+" -c:v copy trimmed.mp4", shell=True, check=True)

    try:
        print("🔹 Applying crosshair overlay and saving final video...")
        process = subprocess.Popen(ffmpeg_command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing FFmpeg overlay command: {e}")


def annotate_thread():
    global curcol, toggleText, toggleStability, busy, process, power_percent, camera, zooms
    while True:

        #camera.annotate_foreground = Color(curcol)
        bus_voltage = read_voltage()
        power_percent = (bus_voltage - V_MIN) / (V_MAX - V_MIN) * 100
        power_percent = max(0, min(100, power_percent))  # Clamp between 0-100%

        #print("Load Voltage: {:.3f} V".format(bus_voltage))
        #print("Power Percent: {:.1f}%\n".format(power_percent))



        ACCx = IMU.readACCx()
        ACCy = IMU.readACCy()
        ACCz = IMU.readACCz()
        GYRx = IMU.readGYRx()
        GYRy = IMU.readGYRy()
        GYRz = IMU.readGYRz()
#        MAGx = IMU.readMAGx()
#        MAGy = IMU.readMAGy()
#        MAGz = IMU.readMAGz()

        time.sleep(.1)

        ACCx2 = IMU.readACCx()
        ACCy2 = IMU.readACCy()
        ACCz2 = IMU.readACCz()

        total1 = ACCx + ACCy + ACCz

#        MAGx -= (magXmin + magXmax) /2
#        MAGy -= (magYmin + magYmax) /2
#        MAGz -= (magZmin + magZmax) /2


        total2 = ACCx2 + ACCy2 + ACCz2


        diff = abs(total1-total2)/2
        if  (diff < 80):
            stable = "|     |"
        else:
            stable = " "

        b = datetime.datetime.now()
        a = datetime.datetime.now()
        LP = b.microsecond/(1000000*1.0)

#Convert Gyro raw to degrees per second
        rate_gyr_x =  GYRx * G_GAIN
        rate_gyr_y =  GYRy * G_GAIN
        rate_gyr_z =  GYRz * G_GAIN

        gyroXangle=0
        gyroYangle=0
        gyroZangle=0


#Calculate the angles from the gyro. 
        gyroXangle+=rate_gyr_x*LP
        gyroYangle+=rate_gyr_y*LP
        gyroZangle+=rate_gyr_z*LP

#Calculate heading
#        heading = 180 * math.atan2(MAGy,MAGx)/M_PI

#Only have our heading between 0 and 360
#        if heading < 0:
#            heading += 360

#Normalize accelerometer raw values.
        if(math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)==0):
            print("fuck")
            accXnorm = 0
        else:
            accXnorm = ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
        if(math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)==0):
            print("you")
            accYnorm = 0
        else:
            accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
#Calculate :pitch and roll
        try:
            roll = math.asin(accXnorm)
    #print "Pitch: "+str(pitch)
            pitch = -math.asin(accYnorm/math.cos(roll))
    #print "RollL "+str(roll)
    #Calculate the new tilt compensated values
#            magXcomp = MAGx*math.cos(roll)+MAGz*math.sin(roll)
#            magYcomp = MAGx*math.sin(pitch)*math.sin(roll)+MAGy*math.cos(pitch)-MAGz*math.sin(pitch)*math.cos(roll)

    #Calculate tilt compensated heading
#            tiltCompensatedHeading = 180 * math.atan2(magYcomp,magXcomp)/M_PI
        except ValueError:
            print("Value Error")
        #pitchValue = round(pitch, 1)
        #print("PV: "+str(pitchValue))
        #if(pitchValue != 90 and pitchValue != -90 and pitchValue != 180 and pitchValue != -180 and pitchValue !=0):
        #    print("bitch"+str(pitchValue))
        #else:
        #    togglepattern4(pitchValue)
        togglepattern4(roll)
        #camera.annotate_text_size = 85
        try:
            if(process.poll() == 0):
                busy = False
            else:
                busy = True
        except:
            pass
        if(toggleText or toggleStability):
            camera.annotate_text_size = 85
            if(toggleText):
                # Compute zoom factor as a multiple
                zoom_factor = 1 / zooms['zoom_wh']

                # Round to 1 decimal place for readability
                zoom_factor = round(zoom_factor, 1)

                if(busy): # or process.poll() is None):
                    annotate_text = "X:"+str(xcenter)+"     "+"Zoom:"+str(zoom_factor)+"       Y:"+str(ycenter)+"\nBusy"
                else:
                    annotate_text = "X:"+str(xcenter)+"     "+"Zoom:"+str(zoom_factor)+"       Y:"+str(ycenter)+"\n"
            else:
                if(busy): #or process.poll() is None):
                    annotate_text = "\nBusy"
                else:
                    annotate_text = "\n"
            if(toggleStability):
                annotate_text += "\n\n"
                annotate_text += stable+"\n"+stable
                if(toggleText):
                   annotate_text += "\n\n\n"
            else:
                annotate_text += "\n\n\n\n\n\n"
            if(toggleText):
                annotate_text += "Pitch:"+str(pitch)[0:5]+"    "+"{:d}%".format(int(power_percent))+"    Roll:"+str(roll)[0:5]

            camera.annotate_text = annotate_text
        else:
            camera.annotate_text = ""

def get_file_name_pic():  # new
    return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.png")

def get_temp_mp4_file_name():
    return datetime.datetime.now().strftime("Temp-%Y-%m-%d_%H.%M.%S.mp4")


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
    x_norm = xcenter / width
    y_norm = ycenter / height

    # Ensure zoom area is within valid bounds
    zoom_width = max(zooms['zoom_wh'], 0.2)
    zoom_width = min(zoom_width, 1.0)

    # Calculate the zoom box with a **small upward adjustment**
    half_zoom = zoom_width / 2
    x_start = x_norm - half_zoom
    y_start = y_norm - half_zoom #- 0.01  # **Shift up slightly**

    # Clamp to valid image bounds
    x_start = max(0.0, min(x_start, 1.0 - zoom_width))
    y_start = max(0.0, min(y_start, 1.0 - zoom_width))

    # Apply updated zoom settings
    camera.zoom = (
        round(x_start, 10),
        round(y_start, 10),
        round(zoom_width, 10),
        round(zoom_width, 10),
    )

    print(f"Zoom updated: {zoom_factor}x, Centered at ({xcenter}, {ycenter})")

def zoom_in():
    global zoomcount, hairwidth, radius
    if zoomcount == 0:
        target_zoom = 12
        hairwidth = hairwidth4x
        radius = radius4x
    elif zoomcount == 12:
        target_zoom = 14
        hairwidth = hairwidth6x
        radius = radius6x
    else:
        return  # Already at max zoom

    for _ in range(target_zoom - zoomcount):
        zooms['zoom_xy'] += zooms['zoom_step']
        zooms['zoom_wh'] -= (zooms['zoom_step'] * 2)
        zoomcount += 1
        update_zoom()

    print(f"Zoom increased to level {zoomcount}")

def zoom_out():
    global zoomcount, hairwidth, radius
    if zoomcount == 14:
        target_zoom = 12
        hairwidth = hairwidth4x
        radius = radius4x
    elif zoomcount == 12:
        target_zoom = 0
        hairwidth = hairwidth1x
        radius = radius1x
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
global alphaValue
alphaValue = 50

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
            'radius1x': '100',
            'hairwidth1x': '5',
            'radius4x': '200',
            'hairwidth4x': '15',
            'radius6x': '300',
            'hairwidth6x': '30',
            'xcenter': '640',
            'ycenter': '360',
            'leftright': '32767',
            'updown': '33023'
            }

# if config file is missing, recreate it with default values:
def CreateConfigFromDef(fileloc,defaults):
    print("Config file not found.")
    print("Recreating " + fileloc + " using default settings.")
    config.add_section('main')
    config.add_section('overlay')
    config.set('overlay', 'xcenter', cdefaults.get('xcenter'))
    config.set('overlay', 'ycenter', cdefaults.get('ycenter'))
    config.set('overlay', 'color', cdefaults.get('color'))
    config.set('overlay', 'pattern', cdefaults.get('pattern'))
    config.set('overlay', 'radius1x', cdefaults.get('radius1x'))
    config.set('overlay', 'radius4x', cdefaults.get('radius4x'))
    config.set('overlay', 'radius6x', cdefaults.get('radius6x'))
    config.set('overlay', 'hairwidth1x', cdefaults.get('hairwidth1x'))
    config.set('overlay', 'hairwidth4x', cdefaults.get('hairwidth4x'))
    config.set('overlay', 'hairwidth6x', cdefaults.get('hairwidth6x'))
    config.set('overlay', 'leftright', cdefaults.get('leftright'))
    config.set('overlay', 'updown', cdefaults.get('updown'))

    config.set('main', 'width', cdefaults.get('width'))
    config.set('main', 'height', cdefaults.get('height'))
    # write default settings to new config file:
    with open(fileloc, 'w') as f:
        config.write(f)

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
radius4x = int(config.get('overlay', 'radius4x'))
radius6x = int(config.get('overlay', 'radius6x'))
hairwidth1x = int(config.get('overlay', 'hairwidth1x'))
hairwidth4x = int(config.get('overlay', 'hairwidth4x'))
hairwidth6x = int(config.get('overlay', 'hairwidth6x'))
leftright = int(config.get('overlay', 'leftright'))
updown = int(config.get('overlay', 'updown'))
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
    elif(roll > 1 and roll <= 1.5 and camera.rotation != 270):
        print("right")
        camera.rotation = 270
    elif(roll >= -1 and roll <= 1 and camera.rotation != 180):
        camera.rotation = 180
        print("normal")
    else:
        return
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

def patternswitcherZoomIn(target,guitoggle):
    global o, zoomcount, ycenter, hairwidth, radius
    # first remove existing overlay:
    if 'o' in globals() and o != None:
        camera.remove_overlay(o)
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
        camera.remove_overlay(o)
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



def loadFile():
    global xcenter, ycenter
    with open(zerofile) as f:
        data = dict(filter(None, csv.reader(f)))
    ycenter = list(data.keys())[0]
    xcenter = list(data.values())[0]
    xcenter = int(xcenter)
    ycenter = int(ycenter)
    print("X: "+str(xcenter))
    print("Y: "+str(ycenter))
    togglepattern3()

def writeZeroFile(xaxis, yaxis):
    with open(zerofile, 'w') as file:
        writer = csv.writer(file)
        writer.writerow([xaxis, yaxis])

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
    camera.brightness = 60
    #camera.annotate_foreground = Color('green')
    filename = get_file_name()
    camera.start_recording(filename)
    # set this to 1 when switching to fullscreen output
    camera.preview_fullscreen = 1
    camera.start_preview()
    togglepattern(curpat2)
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
                    if(absevent.event.value > leftright):
                       print("right")
                       xcenter = xcenter +5
                       togglepattern3()
                    elif (absevent.event.value < leftright): #32767):
                       print("left")
                       xcenter = xcenter -5
                       togglepattern3()
                if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_Y':
                    print(absevent.event.value)
                    if(absevent.event.value > updown):
                        print("down")
                        ycenter = ycenter +5
                        togglepattern3()
                    elif (absevent.event.value < updown):
                        print("up")
                        ycenter = ycenter -5
                        togglepattern3()




               #if(prevhold != event.code):
            if event.value == 1:
                if event.code == start:
                    print("start")
                    os.system("/usr/bin/raspi2png -p /mnt/usb_share/"+get_file_name_pic())
                if event.code == yBtn:
                    print("Y")
                    togglepattern(curpat2+1)
                if event.code == aBtn:
                    print("A")
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
                if event.code == aBtn:
                    print("hA")
                if event.code == bBtn:
                    print("hB")
                if event.code == xBtn:
                    print("hX")

#                prevhold = event.code

            if event.value == 1:
                if event.code == select:
                    print("select")
                    writeZeroFile(ycenter, xcenter)
#                    camera.annotate_text_size = 135
                    camera.annotate_text = "\nSAVED"
                    camera.annotate_text = "\nSAVED"
                    camera.annotate_text = "\nSAVED"
                if event.code == lTrig:
                    print("left bumper")
                    zoom_out()
                    togglepattern3()
                if event.code == rTrig:
                    print("right bumper")
                    zoom_in()
                    togglepattern3()
            if event.value == 2 and not busy:
                if event.code == start:
                    print("hstart")
                    camera.annotate_text = "\nShot Cam"
                    busy = True
                    shotcam()
                if event.code == lTrig and zoomcount > 0:
                    print("hleft bumper")
                    zoom_out()
                    togglepattern3()
                if event.code == rTrig and zoomcount < 14:
                    print("hright bumper")
                    zoom_in()
                    togglepattern3()

    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
        print("\nExiting Program")
        thread_exit = True  # Signal thread to stop
        t1.join()  # Wait for thread to terminate
    finally:
        camera.close()               # clean up camera
        GPIO.cleanup()               # clean up GPIO
