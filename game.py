from tkinter import *
from math import *
from time import *
from random import *

Interface = Tk()
ctx = Canvas( Interface, width=1200, height=800, background="brown" )
ctx.pack()

##############################
####   GLOBAL VARIABLES   ####
##############################
def setInitialValues():
    global t, score, scrSpd, entityList, gravity, p, platformList, pBodyImgs, pArmImgs, tutImgs
    t = 0
    score = 0 #score; also counter for time
    scrSpd = 30 #scroll speed
    entityList = []
    gravity = 2
    p = player(0)
    platformList = []
    
    #images:
    pBodyImgs = []
    pArmImgs = []
    tutImgs = []
    for i in range(14): # load Character body images
        fileName = "assets\character" + format(i, '04d')+ ".gif"
        image = PhotoImage(file = fileName)
        pBodyImgs.append(image)
    for i in range(8): # load Arm images
        fileName = "assets\mugArm" + format(i, '04d')+ ".gif"
        image = PhotoImage(file = fileName)
        pArmImgs.append(image)
    for i in range(4):
        fileName = "assets\Tut" + format(i, '04d')+ ".gif"
        image = PhotoImage(file = fileName)
        tutImgs.append(image)

    

####################
####   ENTITY   ####
####################

class entity():
    global entityList
    def __init__(self, id):
        entityList.append(self)
        self.id = id
        self.pos = [0,0]
        self.vel = [0,0]
        self.isFixed = False #determines if it moves relative to everything or not
        self.airborne = True
    def update(self):
        if self.isFixed:
            self.pos[0] -= scrSpd
        else:
            self.pos[0] += self.vel[0]
            self.pos[1] += self.vel[1]
            if self.airborne:
                self.vel[1] += gravity
        

####################
####   PLAYER   ####
####################
        
class player(entity):
    def __init__(self, id):
        entity.__init__(self, id)
        self.pos = [400, -200]
        self.shotTime = 100
        self.invulnerable = False
    def draw(self):
        if not (self.invulnerable and t%4 < 2): #blink if invulnerable
            if self.airborne:
                if self.vel[1] > 0:
                    ctx.create_image(self.pos[0], self.pos[1], image = pBodyImgs[13], anchor = CENTER)
                    ctx.create_image(self.pos[0], self.pos[1], image = pArmImgs[7], anchor = CENTER)
                else:
                    ctx.create_image(self.pos[0], self.pos[1], image = pBodyImgs[12], anchor = CENTER)
                    ctx.create_image(self.pos[0], self.pos[1], image = pArmImgs[6], anchor = CENTER)
            else:
                ctx.create_image(self.pos[0], self.pos[1], image = pBodyImgs[t%12], anchor = CENTER)
                ctx.create_image(self.pos[0], self.pos[1], image = pArmImgs[t%6], anchor = CENTER)

    def checkCollisions(self):
        for platform in platformList:
            if platform.pos[0] <= self.pos[0] + 24 and platform.pos[0] + platform.length >= self.pos[0] - 24: 
                if platform.pos[1] >= self.pos[1] + 24 and platform.pos[1] <= self.pos[1] + 24 + self.vel[1]:
                    self.pos[1] = platform.pos[1] -24
                    self.vel[1] = 0
                    self.airborne = False
                    break # breaks are so that it only needs to collide with one platform to not be airborne.
                elif self.pos[1] == platform.pos[1] -24:
                    self.vel[1] = 0
                    self.airborne = False
                    break
                else:
                    self.airborne = True
                break
            else:
                self.airborne = True
                
                    
    def update(self):
        #shooty stuff here
        self.checkCollisions()
        entity.update(self)
        self.draw()

            
    
#######################
####   PLATFORMS   ####
#######################
        
class platform(entity):
    def __init__(self, id, length, y):
        platformList.append(self)
        entity.__init__(self, id)
        self.length = length
        self.pos = [1200,y]
        self.isFixed = True

    def draw(self):
        ctx.create_rectangle(self.pos[0], self.pos[1], self.pos[0] + self.length, self.pos[1] + 5, fill = "white", outline = "white")

    def update(self):
        self.draw()
        entity.update(self)

##################
####   MAIN   ####
##################

def mainUpdate(): #updates everything
    global t, entityList
    for i in range(len(entityList)): #loops through the list of entities and calls update in all of them
        entityList[i].update()
    ctx.update()
    ctx.delete(ALL)
    t+=1

    
def runGame():
    setInitialValues()
    p = platform(10000, 500, 500)
    while True:
        mainUpdate()
        sleep(1/30)
        
        if t%30 == 0:
            p = platform(t,500,500)

runGame()
