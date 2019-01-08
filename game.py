from tkinter import *
from math import *
from time import *
from random import *

root = Tk()
ctx = Canvas( root, width=1200, height=800, background="brown" )
ctx.pack()

##############################
####   GLOBAL VARIABLES   ####
##############################
def setInitialValues():
    #General Variables:
    global t, score, scrSpd, entityList, gravity, p, platformList

    t = 0
    score = 0 #score; also counter for time
    scrSpd = 30 #scroll speed
    entityList = []
    gravity = 2
    p = player(0)
    platformList = []

    #Input-related Variables:
    global keyA, keyD, xMouse, yMouse
    
    keyA = False
    keyD = False
    xMouse = 0
    yMouse = 0
    
    #Images:
    global pBodyImgs, pArmImgs, tutImgs
    
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
        self.shotCharge = 100
        self.invulnerable = False
        self.moveSpeed = 10
        
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
                
    def onClick(self): #Fire the cannons! (spill the hot drinks!)
        print ("FIRE!")
    def update(self):
        self.checkCollisions()
        entity.update(self)
        
        if keyA: self.pos[0] -= self.moveSpeed
        if keyD: self.pos[0] += self.moveSpeed   
        self.draw()

##################
##   PLATFORM   ##
##################

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


##   Pause Function   ##

def pauseGame():
    print("Pause Game")
##   Main Update   ##
def mainUpdate(): #updates everything
    global t, entityList
    for i in range(len(entityList)): #loops through the list of entities and calls update in all of them
        entityList[i].update()
    ctx.update()
    ctx.delete(ALL)
    t+=1


##   Input Handlers   ##

def mouseClickHandler( event ):
    global p
    
    p.onclick() #call the Onclick function in the player class

def mouseMotionHandler( event ):
    global xMouse, yMouse

    xMouse = event.x
    yMouse = event.y

def keyDownHandler( event ):
    global keyA, keyD
    if event.keysym in ["Escape", "p", "P", "q", "Q"]: # Bind Escape Key, P and Q to pause
        pauseGame()
    if event.keysym in ["a", "A"]:
        keyA = True
    if event.keysym in ["d", "D"]:      
        keyD = True
        
def keyUpHandler( event ):
    global keyA, keyD
                        
    if event.keysym in ["a", "A"]:
        keyA = False
    if event.keysym in ["d", "D"]:      
        keyD = False
                        
#####################
####   RUNGAME   ####
#####################
    
def runGame():
    setInitialValues()
    p = platform(10000, 500, 500)
    while True:
        mainUpdate()
        sleep(1/30)
        
        if t%30 == 0:
            p = platform(t,500,500)

root.after( 0, runGame )

ctx.bind( "<Button-1>", mouseClickHandler )
ctx.bind( "<Motion>", mouseMotionHandler )
ctx.bind( "<Key>", keyDownHandler )
ctx.bind( "<KeyRelease>", keyUpHandler )


ctx.pack()
ctx.focus_set()
root.mainloop()
