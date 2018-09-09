from tkinter import *
from math import *
import threading

##############################
####   GLOBAL VARIABLES   ####
##############################

scrSpd = 30 #scroll speed
entityList = []

####################
####   ENTITY   ####
####################

class entity():
    def __init__(self):
        entityList.append(self)
        self.pos = [0,0]
        self.vel = [0,0]
        self.imgList = []
        self.touchingGround = False
        self.isFixed = False #determines if it moves relative to everything or not

    def draw(self): #draw this obj
        #draw stuff here
        e = 0 #filler garbo so it doesn't throw an error
    def update(self):
        if self.isFixed:
            self.pos[0] -= scrSpd
        else:
            self.pos[0] += self.vel[0]
            self.pos[1] += self.vel[1]
        self.draw()
        

####################
####   PLAYER   ####
####################
        
class player(entity):
    def __init__(self):
        entity.__init__(self)
        self.shootClip = False
        self.canShoot = True

    def update(self):
        #shooty stuff here
        entity.update(self)

p = player()
##################
####   MAIN   ####
##################

def setInterval(func, sec): #setInterval function; calls func every sec
    def funcWrapper():
        setInterval(func, sec)
        func()
    t = threading.Timer(sec, funcWrapper)
    t.start()
    return t

def mainUpdate(): #updates everything
    for i in range(len(entityList)): #loops through the list of entities and calls update in all of them
        entityList[i].update
        
setInterval(mainUpdate, 1/30) #call mainUpdate 30 times/sec
