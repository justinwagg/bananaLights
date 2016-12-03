
import pigpio
import datetime
import time

highTrig = False
lastPress = datetime.datetime.now()

pi = pigpio.pi()
pi.set_mode(12, pigpio.INPUT)

def changeMode(pressTime):
    global highTrig
    if((pressTime - lastPress).total_seconds()*1000 >= 200):
        highTrig = not highTrig
        print("debounced, flipping highTrig to {}").format(highTrig)
        print((pressTime - lastPress).total_seconds()*1000)

    return datetime.datetime.now()

while True:


    if pi.wait_for_edge(12, pigpio.RISING_EDGE, .01):
        pressed = datetime.datetime.now()
        lastPress = changeMode(pressed)
