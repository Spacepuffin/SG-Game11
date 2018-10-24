from tkinter import *
from math import *
from time import *

##############################
####   GLOBAL VARIABLES   ####
##############################
score = 0 #score; also counter for time
scrSpd = 30 #scroll speed
entityList = []

####################
####   ENTITY   ####
####################

class entity():
    def __init__(self, id):
        entityList.append(self)
        self.id = id
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
        print(self.id, "updated")
        

####################
####   PLAYER   ####
####################
        
class player(entity):
    def __init__(self, id):
        entity.__init__(self, id)
        self.shootClip = False
        self.canShoot = True

    def update(self):
        #shooty stuff here
        entity.update(self)

p = player(0)
##################
####   MAIN   ####
##################

def mainUpdate(): #updates everything
    for i in range(len(entityList)): #loops through the list of entities and calls update in all of them
        entityList[i].update
        
def runGame():
    while True:
        mainUpdate()

runGame()
