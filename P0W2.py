import io
import threading
import os, sys, inspect
# realpath() will make the script run, even if you symlink it
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
# to include modules from a subfolder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"include")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)
from evdev import InputDevice, categorize, ecodes
from picamera import Color
import re
import csv
import time
import math
import IMU
import datetime
import picamera
import numpy as np
import cv2
import RPi.GPIO as GPIO
import patterns
import configparser as ConfigParser
import smbus
import subprocess
from subprocess import Popen, PIPE
import glob
import threading
from collections import OrderedDict
from random import *
import signal
from LSM6DSL import *

prevhold = None

#creates object 'gamepad' to store the data
gamepad = InputDevice('/dev/input/by-id/Gamepad')

#button code variables (change to suit your device)
aBtn = 305
bBtn = 304
xBtn = 307
yBtn = 306
#up = 'ABS_Y'
#down = 'ABS_Y'
#left = 'ABS_X'
#right = 'ABS_X'
start = 313
select = 312
lTrig = 308
rTrig = 309
#prints out device info at start
print(gamepad)

#ycenter = 1280/2
#xcenter = 720/2

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

zerofile = "/home/pi/P0Wlite/zeroxy.csv"

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070  # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40      # Complementary filter constant

bus = smbus.SMBus(1)

INTERRUPT_PIN = 4

#Used to write to the IMU
def writeByte(device_address,register,value):
    bus.write_byte_data(device_address, register, value)

writeByte(LSM6DSL_ADDRESS,LSM6DSL_CTRL1_XL,0b01100000)                 #ODR_XL = 416 Hz, FS_XL = +/- 2 g
writeByte(LSM6DSL_ADDRESS,LSM6DSL_TAP_CFG,0b10001110)                  #Enable interrupts and tap detection on X, Y, Z-axis
writeByte(LSM6DSL_ADDRESS,LSM6DSL_TAP_THS_6D,0b1100100)    # 0b10001100)               #Set tap threshold
writeByte(LSM6DSL_ADDRESS,LSM6DSL_INT_DUR2,0b01111111)                 #Set Duration, Quiet and Shock time windows
writeByte(LSM6DSL_ADDRESS,LSM6DSL_WAKE_UP_THS,0b10000000)              #Double-tap enabled 
writeByte(LSM6DSL_ADDRESS,LSM6DSL_MD1_CFG,0b00001000)                  #Double-tap interrupt driven to INT1 pin

gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
CFangleX = 0.0
CFangleY = 0.0

IMU.detectIMU()     #Detect if BerryIMUv1 or BerryIMUv2 is connected.
IMU.initIMU()  

magXmin =  159
magYmin =  -482
magZmin =  -2149
magXmax =  1488
magYmax =  677
magZmax =  -1796

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


def shotcam():
    global camera, filename, busy, process
    busy = True

    # Get the filename
    shotcam_file = "/mnt/usb_share/"+get_shotcam_file()

    # FFmpeg command for overlaying crosshairs
    ffmpeg_command = (
        'sudo ffmpeg -i trimmed.mp4 -vf "drawbox=x={xcenter}:y=0:w=2:h=720:color=white@0.8:t=fill,'
        'drawbox=x=0:y={ycenter}:w=1280:h=2:color=white@0.8:t=fill" -preset ultrafast -c:a copy -threads 1 "{shotcam_file}"'
    ).format(xcenter=xcenter, ycenter=ycenter, shotcam_file=shotcam_file)

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
    subprocess.run("sudo ffmpeg -y -framerate 30 -i temp_fixed.h264 -c:v copy -movflags +faststart temp.mp4", shell=True, check=True)


    print("🔹 Extracting last 10 seconds using -sseof...")
    subprocess.run(f"ffmpeg -y -sseof -10 -i temp.mp4 -c:v copy trimmed.mp4", shell=True, check=True)



    try:
        print("🔹 Applying crosshair overlay and saving final video...")
        process = subprocess.Popen(ffmpeg_command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing FFmpeg overlay command: {e}")


def annotate_thread():
    global curcol, toggleText, toggleStability, busy, process
    while True:
        ACCx = IMU.readACCx()
        ACCy = IMU.readACCy()
        ACCz = IMU.readACCz()
        GYRx = IMU.readGYRx()
        GYRy = IMU.readGYRy()
        GYRz = IMU.readGYRz()
        MAGx = IMU.readMAGx()
        MAGy = IMU.readMAGy()
        MAGz = IMU.readMAGz()

        time.sleep(.1)

        ACCx2 = IMU.readACCx()
        ACCy2 = IMU.readACCy()
        ACCz2 = IMU.readACCz()

        total1 = ACCx + ACCy + ACCz

        MAGx -= (magXmin + magXmax) /2
        MAGy -= (magYmin + magYmax) /2
        MAGz -= (magZmin + magZmax) /2


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
        heading = 180 * math.atan2(MAGy,MAGx)/M_PI

#Only have our heading between 0 and 360
        if heading < 0:
            heading += 360

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
            pitch = math.asin(accXnorm)
    #print "Pitch: "+str(pitch)
            roll = -math.asin(accYnorm/math.cos(pitch))
    #print "RollL "+str(roll)
    #Calculate the new tilt compensated values
            magXcomp = MAGx*math.cos(pitch)+MAGz*math.sin(pitch)
            magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)-MAGz*math.sin(roll)*math.cos(pitch)

    #Calculate tilt compensated heading
            tiltCompensatedHeading = 180 * math.atan2(magYcomp,magXcomp)/M_PI
        except ValueError:
            print("Value Error")
        #pitchValue = round(pitch, 1)
        #print("PV: "+str(pitchValue))
        #if(pitchValue != 90 and pitchValue != -90 and pitchValue != 180 and pitchValue != -180 and pitchValue !=0):
        #    print("bitch"+str(pitchValue))
        #else:
        #    togglepattern4(pitchValue)
        togglepattern4(pitch)
        #camera.annotate_text_size = 85
        try:
            if(process.poll() == 0):
                busy = False
            else:
                busy = True
        except:
            pass
#            print("Busy Error")
        if(toggleText or toggleStability):
            camera.annotate_text_size = 85
            if(toggleText):
                if(busy): # or process.poll() is None):
                    annotate_text = "X:"+str(xcenter)+"    "+"Zoom:"+str(zoomcount)+"        Y:"+str(ycenter)+"\nBusy"
                else:
                    annotate_text = "X:"+str(xcenter)+"    "+"Zoom:"+str(zoomcount)+"        Y:"+str(ycenter)+"\n"
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
                annotate_text += "Pitch:"+str(pitch)[0:5]+"             Roll:"+str(roll)[0:5]
            #camera.annotate_foreground = Color(str(curcol))
            camera.annotate_text = annotate_text
        else:
            camera.annotate_text = ""

def get_file_name_pic():  # new
    return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.png")


def update_zoom():
    global roi,zoomcount
    #print "Setting camera to (%s, %s, %s, %s)" % (zooms['zoom_xy'], zooms['zoom_xy'], zooms['zoom_wh'], zooms['zoom_wh'])
    roi = str(zooms['zoom_xy'])[:6], str(zooms['zoom_xy'])[:6], str(zooms['zoom_wh'])[:6], str(zooms['zoom_wh'])[:6]
    roi = str(roi)[1:-1]
    roi = re.sub("'","",roi)
    roi = re.sub(" ","",roi)
    print(roi)
    camera.zoom = (zooms['zoom_xy'], zooms['zoom_xy'], zooms['zoom_wh'], zooms['zoom_wh'])
    #print "Camera at (x, y, w, h) = ", camera.zoom
    print("zoomcount: "+str(zoomcount))

def set_min_zoom():
    zooms['zoom_xy'] = zooms['zoom_xy_min']
    zooms['zoom_wh'] = zooms['zoom_wh_min']

def set_max_zoom():
    zooms['zoom_xy'] = zooms['zoom_xy_max']
    zooms['zoom_wh'] = zooms['zoom_wh_max']

def zoom_out():
    global zoomcount
    if zooms['zoom_xy'] - zooms['zoom_step'] < zooms['zoom_xy_min']:
        set_min_zoom()
        zoomcount=0
    elif(zoomcount <= 10):
        zooms['zoom_xy'] -= zooms['zoom_step']
        zooms['zoom_wh'] += (zooms['zoom_step'] * 2)
        zoomcount = zoomcount -1
        update_zoom()

def zoom_in():
    global zoomcount
    if zooms['zoom_xy'] + zooms['zoom_step'] > zooms['zoom_xy_max']:
        set_max_zoom()
    elif(zoomcount <= 9):
        zooms['zoom_xy'] += zooms['zoom_step']
        zooms['zoom_wh'] -= (zooms['zoom_step'] * 2)
        zoomcount = zoomcount +1
        update_zoom()

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
configfile = '/boot/crosshair.cfg'
cdefaults = {
            'width': '800',
            'height': '600',
            'color': 'white',
            'pattern': '1',
            'radius': '100',
            'xcenter': '400',
            'ycenter': '300',
            'stream': 'false',
            'upload': 'false'
            }

# if config file is missing, recreate it with default values:
def CreateConfigFromDef(fileloc,defaults):
    print("Config file not found.")
    print("Recreating " + fileloc + " using default settings.")
    config.add_section('main')
    config.add_section('overlay')
    config.set('overlay', 'xcenter', cdefaults.get('xcenter'))
    config.set('overlay', 'ycenter', cdefaults.get('ycenter'))
    config.add_comment('overlay', 'color options: white (default), red, green, blue, yellow')
    config.set('overlay', 'color', cdefaults.get('color'))
    config.add_comment('overlay', 'pattern options:')
    config.add_comment('overlay', '1: Bruker style with circles and ticks')
    config.add_comment('overlay', '2: simple crosshair with ticks')
    config.add_comment('overlay', '3: simple crosshair without ticks')
    config.add_comment('overlay', '4: crosshair with circles, no ticks')
    config.add_comment('overlay', '5: crosshair with one circle, no ticks')
    config.add_comment('overlay', '6: only one circle')
    config.add_comment('overlay', '7: small crosshair')
    config.add_comment('overlay', '8: small crosshair without intersection')
    config.add_comment('overlay', '9: only a dot')
    config.add_comment('overlay', '10: grid')
    config.set('overlay', 'pattern', cdefaults.get('pattern'))
    config.add_comment('overlay', 'set radius (in px) for all circles,')
    config.add_comment('overlay', 'also controls grid spacing in Pattern 10')
    config.set('overlay', 'radius', cdefaults.get('radius'))
    config.set('main', 'width', cdefaults.get('width'))
    config.set('main', 'height', cdefaults.get('height'))
    config.add_comment('main', 'uploading and streaming not implemented yet')
    config.set('main', 'upload', cdefaults.get('upload'))
    config.set('main', 'stream', cdefaults.get('stream'))
    # write default settings to new config file:
    with open(fileloc, 'wb') as f:
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
xcenter = width//2
height = int(config.get('main', 'height'))
ycenter = height//2
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
curpat = 1
#xcenter = int(config.get('overlay', 'xcenter'))
#ycenter = int(config.get('overlay', 'ycenter'))
radius = int(config.get('overlay', 'radius'))

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
        curpat2 += var
        print("Set new pattern: " + str(curpat2))
        if curpat2 > patterns.maxpat:     # this number must be adjusted to number of available patterns!
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


def togglepattern2(channel):
    global togsw,o,curpat2,col,ovl,gui,alphaValue
    # if overlay is inactive, ignore button:
    if togsw == 0:
        print("Pattern button pressed, but ignored --- Crosshair not visible.")
    # if overlay is active, drop it, change pattern, then show it again
    else:
        curpat2 += 1
        print("Set new pattern: " + str(curpat2))
        if curpat2 > 6:     # this number must be adjusted to number of available patterns!
            curpat2 = 1
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
            #patternswitcher(gui,1)
            if 'o' in globals():
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(gui), layer=3, alpha=alphaValue)
    return


def togglepattern3():
    global togsw,o,curpat,col,ovl,gui,alphaValue,ycenter,zoomcount
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
#	    creategui(gui)
            patternswitcherZoomIn(gui,1)
            if 'o' in globals():
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(gui), layer=3, alpha=alphaValue)
    return


def togglepattern4(pitch):
    global togsw,o,curpat,col,ovl,gui,alphaValue,ycenter,xcenter,zoomcount #,camera
    #print(pitch)
    #print(camera.rotation)
    if(pitch < -1 and pitch >= -1.5 and camera.rotation != 90):
        print("left")
        camera.rotation = 90
    elif(pitch > 1 and pitch <= 1.5 and camera.rotation != 270):
        print("right")
        camera.rotation = 270
    elif(pitch >= -1 and pitch <= 1 and camera.rotation != 180):
        camera.rotation = 180
        print("normal")
    else:
#        print("Bullshit")
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
#           creategui(gui)
            patternswitcherZoomIn(gui,1)
            #print("ass"+str(pitch))
            if 'o' in globals():
                camera.remove_overlay(o)
#            if(pitch <= -.75 and pitch >= -1.5 and camera.rotation != -90):
#                print("test1")
#                camera.rotation = -90
#            elif(pitch >= .75 and pitch <= 1.5 and camera.rotation != 90):
#                print("test2")
#                camera.rotation = 90
#            elif(pitch == 0 and camera.rotation != 0):
#                camera.rotation = 0

#            if(pitch == -1.5):
#                camera.rotation = -90
            o = camera.add_overlay(bytes(gui), layer=3, alpha=alphaValue)
    return




# function 
def togglepatternZoomIn():
    global togsw,o,curpat,col,ovl,gui,alphaValue,ycenter,zoomcount
    # if overlay is inactive, ignore button:
    if togsw == 0:
        print("Pattern button pressed, but ignored --- Crosshair not visible.")
        zoom_in()
	#if ycenter < cdefaults.get('ycenter')
	#ycenter = ycenterList[zoomcount]
    # if overlay is active, drop it, change pattern, then show it again
    else:
        if guivisible == 0:
            zoom_in()
	    # reinitialize array:
            ovl = np.zeros((height, width, 3), dtype=np.uint8)
            patternswitcherZoomIn(ovl,0)
            if 'o' in globals():
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(ovl), layer=3, alpha=alphaValue)
        else:
            # reinitialize array
            zoom_in()
            gui = np.zeros((height, width, 3), dtype=np.uint8)
	    #creategui(gui)
            patternswitcherZoomIn(gui,1)
            if('o' in globals()):
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(gui), layer=3, alpha=alphaValue)
    return

# function to call when middle button is pressed (GPIO 23):
def togglepatternZoomOut():
    global togsw,ycenter,o,curpat,col,ovl,gui,alphaValue,zoomcount,ycenterList
    # if overlay is inactive, ignore button:
    #ycenter = ycenterList[zoomcount]
    print(zoomcount)
    #print "shit balls"
    if togsw == 0:
        zoom_out()
        print("Pattern button pressed, but ignored --- Crosshair not visible.")
    # if overlay is active, drop it, change pattern, then show it again
    else:
        if guivisible == 0:
            zoom_out()
            # reinitialize array:
            ovl = np.zeros((height, width, 3), dtype=np.uint8)
            patternswitcherZoomOut(ovl,0)
            if 'o' in globals() and o != None:
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(ovl), layer=3, alpha=alphaValue)
        else:
            zoom_out()
            # reinitialize array
            gui = np.zeros((height, width, 3), dtype=np.uint8)
            #creategui(gui)
            patternswitcherZoomOut(gui,1)
            if 'o' in globals():
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(gui), layer=3, alpha=alphaValue)
    return


def patternswitcherZoomIn(target,guitoggle):
    global o, zoomcount, ycenter
    # first remove existing overlay:
    if 'o' in globals() and o != None:
        camera.remove_overlay(o)
    #if guitoggle == 1:
    #    creategui(gui)
    if zooms['zoom_xy'] == zooms['zoom_xy_max']:
        print("zoom at max")
    # cycle through possible patterns:
    if curpat2 == 1:
        patterns.pattern1(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 2:
        patterns.pattern2(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 3:
        patterns.pattern3(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 4:
        patterns.pattern4(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 5:
        patterns.pattern5(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 6:
        patterns.pattern6(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 7:
        patterns.pattern7(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 8:
        patterns.pattern8(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 9:
        patterns.pattern9(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 10:
        patterns.pattern10(target, width, height, xcenter, ycenter, radius, col)
    #if guitoggle == 1:
    #    creategui(gui)
    # Add the overlay directly into layer 3 with transparency;
    # we can omit the size parameter of add_overlay as the
    # size is the same as the camera's resolution
    o = camera.add_overlay(bytes(target), layer=3, alpha=alphaValue)
    #cv2.imwrite('/home/pi/messigray.png', np.getbuffer(gui))
    return

def patternswitcherZoomOut(target,guitoggle):
    global o, zoomcount, xcenter, ycenter, ycenterList
    # first remove existing overlay:
    if 'o' in globals() and o != None:
        camera.remove_overlay(o)
####    if guitoggle == 1:
####        creategui(gui)
    if zooms['zoom_xy'] == zooms['zoom_xy_min']:
        print("zoom at min")
    # cycle through possible patterns:
    if curpat2 == 1:
        patterns.pattern2(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 2:
        patterns.pattern3(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 3:
        patterns.pattern5(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 4:
        patterns.pattern6(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 5:
        patterns.pattern7(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 6:
        patterns.pattern6(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 7:
        patterns.pattern7(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 8:
        patterns.pattern8(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 9:
        patterns.pattern9(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 10:
        patterns.pattern10(target, width, height, xcenter, ycenter, radius, col)
#    if guitoggle == 1:
#        creategui(gui)
    # Add the overlay directly into layer 3 with transparency;
    # we can omit the size parameter of add_overlay as the
    # size is the same as the camera's resolution
    o = camera.add_overlay(bytes(target), layer=3, alpha=alphaValue)
    return


# function to call when low button is pressed (GPIO 18):
def togglecolor():
    global togsw,o,curcol,col,ovl,gui,alphaValue,infoVisible
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
    #    camera.annotate_foreground = curcol
        if guivisible == 0:
            # reinitialize array:
            ovl = np.zeros((height, width, 3), dtype=np.uint8)
            patternswitcher(ovl,0)
            if 'o' in globals():
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(ovl), layer=3, alpha=alphaValue)
        else:
#            camera.annotate_foreground = Color(str(curcol))
            # reinitialize array
            gui = np.zeros((height, width, 3), dtype=np.uint8)
            #creategui(gui)
            if infoVisible:
                patternswitcher(gui,1) 
            elif infoVisible == False:
                patternswitcher(gui,0) 
            if 'o' in globals():
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(gui), layer=3, alpha=alphaValue)
    return


#def takeScreenshot(channel):
#	global takingScreenshot
#	if takingScreenshot == False:
#	    subprocess.Popen("./raspi2png",  cwd='/home/pi/raspi2png')
#	    takingScreenshot = True
#	    time.sleep(20)
#	    #generate filename for dropbox file name
#	    filename = get_file_name_pic()
#
#	    photofile = "/home/pi/Dropbox-Uploader/dropbox_uploader.sh upload /home/pi/raspi2png/snapshot.png /PiGun/"+filename
#	    #runs photofile dropbox upload
#	    subprocess.Popen(photofile, shell=True)
#	    takingScreenshot = False
#
#def rotary_interrupt1(A_or_B):
#	global Rotary_counter1, Current_A1, Current_B1, LockRotary1
#													# read both of the switches
#	Switch_A1 = GPIO.input(Enc_A1)
#	Switch_B1 = GPIO.input(Enc_B1)
#													# now check if state of A or B has changed
#													# if not that means that bouncing caused it
#	if Current_A1 == Switch_A1 and Current_B1 == Switch_B1:		# Same interrupt as before (Bouncing)?
#		return										# ignore interrupt!
#
#	Current_A1 = Switch_A1								# remember new state
#	Current_B1 = Switch_B1								# for next bouncing check
#
#
#	if (Switch_A1 and Switch_B1):						# Both one active? Yes -> end of sequence
#		LockRotary1.acquire()						# get lock 
#		if A_or_B == Enc_B1:							# Turning direction depends on 
#			Rotary_counter1 += 1						# which input gave last interrupt
#		else:										# so depending on direction either
#			Rotary_counter1 -= 1						# increase or decrease counter
#		LockRotary1.release()						# and release lock
#	return											# THAT'S IT


#def markClear(channel):
#        d = OrderedDict()
#        d['value'] = 23
#        d['lat'] = gpsd.fix.latitude
#        d['lon'] = gpsd.fix.longitude
#        d['ele'] = gpsd.fix.altitude
#        print("dump:",json.dumps(d))
#        client.publish('clearlocations',json.dumps(d))

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

def toggleXY(channel):
        global Toggle, zoomcount, ycenter
        if Toggle == True:
        #    camera.annotate_foreground = picamera.Color(y=0, u=0, v=0)
            Toggle = False
        else:
            Toggle = True
        #    camera.annotate_foreground = picamera.Color(y=0.4, u=0, v=0)
        if(Toggle and modeSelection == 4):
            writeZeroFile(xcenter, ycenter)
        if(not(Toggle) and modeSelection == 7):
            loadFile()

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
    global o
    # first remove existing overlay:
    if 'o' in globals():
        camera.remove_overlay(o)
####    if guitoggle == 1:
####        creategui(gui)
    # cycle through possible patterns:
    if curpat2 == 1:
        patterns.pattern1(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 2:
        patterns.pattern2(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 3:
        patterns.pattern3(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 4:
        patterns.pattern4(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 5:
        patterns.pattern5(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 6:
        patterns.pattern6(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 7:
        patterns.pattern7(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 8:
        patterns.pattern8(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 9:
        patterns.pattern9(target, width, height, xcenter, ycenter, radius, col)
    if curpat2 == 10:
        patterns.pattern10(target, width, height, xcenter, ycenter, radius, col)
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



with picamera.PiCamera() as camera:
    camera.resolution = (width, height)
    ##stream = picamera.PiCameraCircularIO(camera, seconds=20)
    #camera.start_recording(stream, format='mjpeg')
    print(stream)
    stream = picamera.PiCameraCircularIO(camera, seconds=10)
    print(stream)
#    global Rotary_counter1, LockRotary, Toggle
#    global alphaValue, xcenter, ycenter
    NewCounter1 = 0
    camera.vflip = True
    camera.hflip = True
    camera.resolution = (width, height)
    camera.framerate = 30
    camera.rotation = 180
    camera.brightness = 60
    #camera.annotate_foreground = Color('green')
    filename = get_file_name()
    #camera.meter_mode='matrix'
    #####RECORDING LINE BELOW
    #camera.contrast = 50
    #####camera.start_recording(stream)
    camera.start_recording(filename)
    # set this to 1 when switching to fullscreen output
    camera.preview_fullscreen = 1
    camera.start_preview()
    togglepattern(4)
    try:
        t1 = threading.Thread(target=annotate_thread, name='t1')
        t1.start()
    #while True:
        patternswitcher(gui,1)
        #time.sleep(2)
        #guivisible = 1
        #togglepatternZoomOut()
        #a = datetime.datetime.now()
        #while True:
#        camera.annotate_text_size = 70
#        annotate_text = "\n\n\n\n\n\n\n"
#        annotate_text += "Pitch:"+str(pitch)[0:5]+" Roll:"+str(roll)[0:5]
#        camera.annotate_text = annotate_text
        for event in gamepad.read_loop():
            #print(stream)
#        while True:
            if event.type == ecodes.EV_ABS: 
#               camera.annotate_background = Color('white')
                absevent = categorize(event) 
                if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_X':
                    print(absevent.event.value)
                    if(absevent.event.value > 32512):
                       print("right")
                       xcenter = xcenter +5
#                       pan_right()
                       togglepattern3()
                       #camera.annotate_text = "\n\n\nRIGHT"
                    elif (absevent.event.value < 32512):
                       print("left")
                       xcenter = xcenter -5
                       togglepattern3()
#                       pan_left()
                       #camera.annotate_text = "\n\n\nLEFT"
                if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_Y':
                    print(absevent.event.value)
                    if(absevent.event.value > 32512):
                   #     togglepatternZoomOut()
                   #     camera.annotate_text = "\n"+str(zoomcount)+"/10\n\nZoom Out"
                        print("down")
                        ycenter = ycenter +5
#                        pan_down()
                        togglepattern3()
                        #camera.annotate_text = "\n\n\nDOWN"
#                        camera.annotate_text = "\n\n\nDOWN"
                    elif (absevent.event.value < 32512):
                   #     togglepatternZoomIn()
                   #     camera.annotate_text = "\n"+str(zoomcount)+"/10\n\nZoom In"
                        print("up")
                        ycenter = ycenter -5
                        togglepattern3()
#                        pan_up()
                        #camera.annotate_text = "\n\n\nUP"
#                        camera.annotate_text = "\n\n\nUP"
            #            togglepattern3()




               #if(prevhold != event.code):
            if event.value == 1:
                if event.code == start:
                    print("start")
                    #camera.annotate_text_size = 85
                    #camera.annotate_text = "\nLOADED XY"
                    #camera.annotate_text = "\nLOADED XY"
                    #camera.annotate_text = "\nLOADED XY"
                    #loadFile()
                    #prevhold = event.code
                    #togglepattern3()
#                    loadFile()
                    os.system("/usr/bin/raspi2png -p /mnt/usb_share/"+get_file_name_pic())
                if event.code == yBtn:
                    print("Y")
                    togglepattern(1)
                if event.code == aBtn:
                    print("A")
                    toggleText = not(toggleText)
#                    togglepattern4(pitch)
                if event.code == bBtn:
                    print("B")
                    togglecolor()
#                    camera.annotate_foreground = Color('red')
                if event.code == xBtn:
                    print("X")
                    toggleStability = not toggleStability
               #    prevhold = event.code

            if event.value == 2:
                if event.code == yBtn:
                    print("hY")
                if event.code == aBtn:
                    print("hA")
                if event.code == bBtn:
                    print("hB")
                if event.code == xBtn and not busy:
                    print("hX")
                    camera.annotate_text = "\nShot Cam"
                    shotcam()
#                    time.sleep(2)
#                prevhold = event.code

            if event.value == 1:
                if event.code == select:
                    print("select")
                    writeZeroFile(ycenter, xcenter)
                    camera.annotate_text_size = 120
                    camera.annotate_text = "\nSAVED"
                    camera.annotate_text = "\nSAVED"
                    camera.annotate_text = "\nSAVED"
#                    loadFile()
#                    xcenter = width//2
#                    ycenter = height//2
#                    togglepattern3()
                if event.code == lTrig:
                    print("left bumper")
                    zoom_out()
                if event.code == rTrig:
                    print("right bumper")
                    zoom_in()
            if event.value == 2 and start != prevhold:
                if event.code == start:
                    print("hstart")
                    #os.system("/usr/bin/raspi2png -p "+get_file_name_pic())
                    #camera.annotate_text_size = 85
                    #camera.annotate_text = "\nSCREENSHOT"
                    #camera.annotate_text = "\nSCREENSHOT"
                    #camera.annotate_text = "\nSCREENSHOT"
#                    loadFile()
#                    prevhold = event.code
#                    togglepattern3()
                if event.code == lTrig:
                    print("hleft bumper")
                    zoom_out()
                if event.code == rTrig:
                    print("hright bumper")
                    zoom_in()
#            time.sleep(.5)
		   #Read the gyroscope and magnetometer values
            ACCx = IMU.readACCx()
            ACCy = IMU.readACCy()
            ACCz = IMU.readACCz()
            GYRx = IMU.readGYRx()
            GYRy = IMU.readGYRy()
            GYRz = IMU.readGYRz()
            MAGx = IMU.readMAGx()
            MAGy = IMU.readMAGy()
            MAGz = IMU.readMAGz()

            #time.sleep(.05)

            ACCx2 = IMU.readACCx()
            ACCy2 = IMU.readACCy()
            ACCz2 = IMU.readACCz()

            total1 = ACCx + ACCy + ACCz

            MAGx -= (magXmin + magXmax) /2
            MAGy -= (magYmin + magYmax) /2
            MAGz -= (magZmin + magZmax) /2


            total2 = ACCx2 + ACCy2 + ACCz2

            diff = abs(total1-total2)/2

            if  (diff < 200):
                #    print("low")
                stable = "|     |"
            else:
                stable = " "


            b = datetime.datetime.now()
            a = datetime.datetime.now()
            LP = b.microsecond/(1000000*1.0)
		#print "Loop Time | %5.2f|" % ( LP ),

		#Convert Gyro raw to degrees per second
            rate_gyr_x =  GYRx * G_GAIN
            rate_gyr_y =  GYRy * G_GAIN
            rate_gyr_z =  GYRz * G_GAIN

		#Calculate the angles from the gyro. 
            gyroXangle+=rate_gyr_x*LP
            gyroYangle+=rate_gyr_y*LP
            gyroZangle+=rate_gyr_z*LP

		#Calculate heading
            heading = 180 * math.atan2(MAGy,MAGx)/M_PI

		#Only have our heading between 0 and 360
            if heading < 0:
                heading += 360

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
		#Calculate pitch and roll
            try:
                pitch = math.asin(accXnorm)
		    #print "Pitch: "+str(pitch)
                roll = -math.asin(accYnorm/math.cos(pitch))
		    #print "RollL "+str(roll)
		    #Calculate the new tilt compensated values
                magXcomp = MAGx*math.cos(pitch)+MAGz*math.sin(pitch)
                magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)-MAGz*math.sin(roll)*math.cos(pitch)

		    #Calculate tilt compensated heading
                tiltCompensatedHeading = 180 * math.atan2(magYcomp,magXcomp)/M_PI
            except ValueError:
                print("Value Error")
        #print(pitch)
        #togglepattern4(pitch)
        ######################
        #camera.annotate_foreground = Color('red') #str(curcol))
        #camera.annotate_text_size = 70
#        annotate_text = "\n\n\n\n\n\n"
        #annotate_text = "X:"+str(xcenter)+"        "+"Y:"+str(ycenter)
#        annotate_text += "\n\n\n\n\n\n"
        #annotate_text += "Pitch:"+str(pitch)[0:5]+" Roll:"+str(roll)[0:5]
        #camera.annotate_text = annotate_text
#ficing






    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
        print("\nExiting Program")
    finally:
        camera.close()               # clean up camera
        GPIO.cleanup()               # clean up GPIO

