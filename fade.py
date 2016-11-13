import datetime
import time
import pigpio
from numpy import interp
import sys

#variables
currentLight = 0
target = 0;
base = [
    [0, 0],
    [50, 100],
    [0, 50]
]
hours = [6, 17, 24]

#pins
lightPin = 23
pirPin = 18

#GPIO settings
pi = pigpio.pi()
pi.set_mode(lightPin, pigpio.OUTPUT)

currentLight = pi.get_PWM_dutycycle(lightPin)

def getIndex():
    time = datetime.datetime.now()
    # mode = 1
    if time.hour >= hours[0] and time.hour < hours[1]:
        mode = 0
    elif time.hour >= hours[1] and time.hour < hours[2]:
        mode = 1
    else:
        mode = 2
    return mode

def FADE(current, target):
    if target > current:
        #fade up
        for i in range(current, target +1):
            print('fading up, i = {}').format(i)
            pi.set_PWM_dutycycle(lightPin, i)
            time.sleep(.005)

    elif target < current:
        #fade down
        for i in range(current, target -1, -1):
            print('fading down, i = {}').format(i)
            pi.set_PWM_dutycycle(lightPin, i)
            time.sleep(.005)

    return target, datetime.datetime.now()

#initial set upon start - always set to rest
print('current light is: {}').format(currentLight)
currentLight, changeTime = FADE(currentLight, base[getIndex()][0])
print('current light is now: {}, changed at {}').format(currentLight, changeTime)

#PIR triggers
# print('PIR Triggered, current light is: {}').format(currentLight)
# currentLight = FADE(currentLight, base[getIndex()][1])
# print('current light is now: {}').format(currentLight)
try:
    while True:
        pir = pi.read(pirPin)
        if pir == 1:
            currentLight, changeTime = FADE(currentLight, base[getIndex()][pir])


        now = datetime.datetime.now()
        elapsed = now - changeTime
        if elapsed.total_seconds() >= 5:
            currentLight, changeTime = FADE(currentLight, base[getIndex()][pir])

except KeyboardInterrupt:
    print("int")
    pi.set_PWM_dutycycle(lightPin, 0)
    pi.stop()
    sys.exit()
