import datetime
import time
highTrig = False # manual override to flip light to max high

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

def result(index, id):
    q = ('select rest, high from mode{} where rowid = (select max(rowid) from mode{});').format(index, index)
    c.execute(q)
    result = c.fetchall()[0]
    # print("result = {}").format(result[id])
    return result[id]