import datetime
import time
import pigpio
from numpy import interp
import sys
import mysql.connector

#select id from device.map where location = 'kitchen' and name = 'under-cabinet';
#this id device 1
device_id = 1

#variables
currentLight = 0
target = 0;


# hours = [6, 17, 24]

highTrig = False # manual override to flip light to max high
lastPress = datetime.datetime.now()

conn = mysql.connector.connect(user='kitchenPi', password='timecard1', host='192.168.1.4')
c = conn.cursor()

#pins
lightPin = 23
pirPin = 18
switch = 12
indicatorB = 6
indicatorR = 5

#GPIO settings
pi = pigpio.pi()
pi.set_mode(lightPin, pigpio.OUTPUT)
pi.set_mode(switch, pigpio.INPUT)
pi.set_mode(indicatorB, pigpio.OUTPUT)
pi.set_mode(indicatorR, pigpio.OUTPUT)

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
            pi.set_PWM_dutycycle(indicatorR, 20)
            pi.set_PWM_dutycycle(indicatorB, 90)
        elif highTrig == False:
            pi.set_PWM_dutycycle(indicatorR, 0)
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
    # print("result = {}").format(result[id])
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

try:
    while True:

        #read the PIR sensor, if it says high then... set a flag saying so, and record that time
        if pi.read(pirPin):
            pirHigh = 1
            pirHit = datetime.datetime.now()

        #if the pir flag says `yes` then lets fade the light up to what's in the sqlite database by way of these nifty functions
        if pirHigh == 1:
            currentLight, changeTime = FADE(currentLight, result(getIndex(), pirHigh))

        #to prepare to either fade down, or do nothing, we need to check the current time in relation to when we faded up
        now = datetime.datetime.now()
        elapsed = now - pirHit    

        #if the elapsed time is greater than some number, then set the pir flag to low and fade to what we say in the tables
        if elapsed.total_seconds() >= 5: 
            pirHigh = 0
            currentLight, changeTime = FADE(currentLight, result(getIndex(), pirHigh))

        #if the switch goes high, set a global variable saying we're in a new world - the light should be high nomatter what
        #this is a little fragile IMO - we're setting a global variable, which I hear is not a good idea.
        #although the index is 3, the values in the table have a high and a low which will get read, and faded to in the above logic
        #potential fix = only do above logic if the mode is not 3, but is that redundant? 
        if pi.wait_for_edge(switch, pigpio.RISING_EDGE, .01):
            pressed = datetime.datetime.now()
            lastPress = changeMode(pressed)
            currentLight, changeTime = FADE(currentLight, result(getIndex(), pirHigh))

except KeyboardInterrupt:
    print("Keyboard Interrupt, stopping PWM, exiting")
    pi.set_PWM_dutycycle(lightPin, 0)
    pi.stop()
    conn.close()
    sys.exit()
