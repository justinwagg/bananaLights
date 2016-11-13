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
    [0, 50],
    [100,100]
]
hours = [6, 17, 24]

highTrig = False # manual override to flip light to max high
lastPress = datetime.datetime.now()


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

try:
    while True:
        pir = pi.read(pirPin)
        if pir == 1:
            currentLight, changeTime = FADE(currentLight, base[getIndex()][pir])


        now = datetime.datetime.now()
        elapsed = now - changeTime
        if elapsed.total_seconds() >= 5:
            currentLight, changeTime = FADE(currentLight, base[getIndex()][pir])

        if pi.wait_for_edge(switch, pigpio.RISING_EDGE, .01):
            pressed = datetime.datetime.now()
            lastPress = changeMode(pressed)
            currentLight, changeTime = FADE(currentLight, base[getIndex()][highTrig])

except KeyboardInterrupt:
    print("Keyboard Interrupt, stopping PWM, exiting")
    pi.set_PWM_dutycycle(lightPin, 0)
    pi.stop()
    sys.exit()
