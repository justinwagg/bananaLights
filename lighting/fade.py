#!/usr/bin/python
import datetime
import time
import pigpio
import sys
import mysql.connector
from password import *
from subprocess import call
import logging

info = logging.getLogger(__name__).info
logging.basicConfig(level=logging.INFO,
                        filename='fade.log', # log to this file
                        format='%(asctime)s %(message)s')

info('Started')

call(['sudo','service','mysql','start'])
info('Going to sleep for 10 seconds while mysql boots')
time.sleep(10)

#this id device 5
device_id = 5

#variables
currentLight = 0
target = 0
pirHitCount = 0

# hours = [6, 17, 24]

highTrig = False # manual override to flip light to max high
lastPress = datetime.datetime.now()

elapsePressed = datetime.datetime.now()-datetime.datetime.now()

conn = mysql.connector.connect(user=user, password=password, host=host)
c = conn.cursor()


#pins
lightPin = 23
pirPin = 18
switchPWR = 16
switch = 12
indicatorB = 6


#GPIO settings
pi = pigpio.pi()
pi.write(switchPWR, 1)
pi.set_mode(lightPin, pigpio.OUTPUT)
pi.set_mode(switch, pigpio.INPUT)
pi.set_mode(indicatorB, pigpio.OUTPUT)

#modes
pirHigh = 0
pirHit = datetime.datetime.now()

try:
    currentLight = pi.get_PWM_dutycycle(lightPin)
except pigpio.error:
    print("couldn't get currentLight")


def getIndex():
    time = datetime.datetime.now()
    # mode = 1

    if(highTrig == False):
        if time.hour >= hours[0] and time.hour < hours[1]:
            mode = 0
        elif time.hour >= hours[1] and time.hour < hours[2]:
            mode = 1
        else:
            mode = 2
    elif(highTrig == True):
        mode = 3

    return mode

def changeMode(pressTime):
    global highTrig
    if((pressTime - lastPress).total_seconds()*1000 >= 200):
        highTrig = not highTrig
        print("debounced, flipping highTrig to {}").format(highTrig)
        print((pressTime - lastPress).total_seconds()*1000)
        # pi.write(indicator, highTrig)
        if highTrig == True:
            pi.set_PWM_dutycycle(indicatorB, 255)
        elif highTrig == False:
            pi.set_PWM_dutycycle(indicatorB, 0)

    return datetime.datetime.now()

def FADE(current, target):
    if target > current:
        #fade up
        for i in range(current, target +1):
#            print('fading up, i = {}').format(i)
            pi.set_PWM_dutycycle(lightPin, i)
            time.sleep(.005)

    elif target < current:
        #fade down
        for i in range(current, target -1, -1):
#            print('fading down, i = {}').format(i)
            pi.set_PWM_dutycycle(lightPin, i)
            time.sleep(.005)

    return target, datetime.datetime.now()

def result(index, id):
    q = ('select rest, high from device{}.mode{} where rowid = (select max(rowid) from device{}.mode{});').format(device_id, index, device_id, index)
    c.execute(q)
    result = c.fetchall()[0]
    return result[id]


def getHours():
    q = ('select h1, h2, h3 from device{}.hours where rowid = (select max(rowid) from device{}.hours);').format(device_id, device_id)
    c.execute(q)
    result = c.fetchall()[0]
    return result

hours = getHours()

#initial set upon start - always set to rest
print('current light is: {}').format(currentLight)
currentLight, changeTime = FADE(currentLight, result(getIndex(), 0))
print('current light is now: {}, changed at {}').format(currentLight, changeTime)
print('mode is currently: {}').format(getIndex())

try:
    while True:
        
        now = datetime.datetime.now() 
       #print('current light is now: {}, changed at {}').format(currentLight, changeTime)
       #print('mode is currently: {}').format(getIndex())

        #read the PIR sensor, if it says high then... set a flag saying so, and record that time
        if pi.read(pirPin):
            pirHigh = 1
            pirHit = datetime.datetime.now()

        #if the pir flag says `yes` then lets fade the light up to what's in the sqlite database by way of these nifty functions
        if pirHigh == 1:
            currentLight, changeTime = FADE(currentLight, result(getIndex(), pirHigh))

        #to prepare to either fade down, or do nothing, we need to check the current time in relation to when we faded up
        elapsed = now - pirHit    
        #print elapsed

        #if the elapsed time is greater than some number, then set the pir flag to low and fade to what we say in the tables
        if elapsed.total_seconds() >= 90 or pirHigh == 0: 
            pirHigh = 0
            currentLight, changeTime = FADE(currentLight, result(getIndex(), pirHigh))

        #if the switch goes high, set a global variable saying we're in a new world - the light should be high nomatter what
        #this is a little fragile IMO - we're setting a global variable, which I hear is not a good idea.
        #although the index is 3, the values in the table have a high and a low which will get read, and faded to in the above logic
        #potential fix = only do above logic if the mode is not 3, but is that redundant? 
        # if pi.wait_for_edge(switch, pigpio.RISING_EDGE, .01):

        #we had a habit of leaving the lights on high - so if the light is high for more than 10 minutes and 
        #there's noone in the room, then turn the light off

        if highTrig:
            elapsePressed = now - pressed

    # if(pi.read(switch) or ( elapsePressed.total_seconds() >= 5 and pirHigh == 0 )):
	if pi.wait_for_edge(switch, pigpio.RISING_EDGE, .01):
    # if( pi.wait_for_edge(switch, pigpio.RISING_EDGE, .01) or ( elapsePressed.total_seconds() >= 5 and pirHigh == 0 ) ):        
            pressed = datetime.datetime.now()
            lastPress = changeMode(pressed)
            currentLight, changeTime = FADE(currentLight, result(getIndex(), pirHigh))
            elapsePressed = pressed - pressed

except KeyboardInterrupt:
    info('Keyboard Interrupt, Stopping PWM, Cleaning Up, Exiting')
    pi.set_PWM_dutycycle(lightPin, 0)
    pi.write(switchPWR, 0)
    pi.stop()
    conn.close()
    sys.exit()
