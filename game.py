from tkinter import *
from math import *
from time import *
from random import *

root = Tk()
ctx = Canvas( root, width=1200, height=800, background="dodgerblue" )
ctx.pack()

##############################
####   GLOBAL VARIABLES   ####
##############################
def setInitialValues():
    #General Variables:
    global game, t, score, scrSpd, gravity
    game = True
    t = 0
    score = 0 #score; also counter for time
    scrSpd = 30 #scroll speed
    gravity = 2
    
    

    #Lists of Object instances:
    global entityList, platformList, projectileList, particleList
    entityList = []
    platformList = []
    projectileList = []
    particleList = []

    #player instance:
    global p
    p = player(0)
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

def pVector(magnitude, angle):
	x = magnitude*cos(angle)
	y = magnitude*sin(angle)
	return [x, y]

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
        self.pos = [400, -50]
        self.shotCharge = 0
        self.invulnerable = False
        self.moveSpeed = 10
        self.angleMouse = 0
        
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

        reticle = []
        reticle += pVector(40, self.angleMouse)
        reticle += pVector(50, self.angleMouse + 0.15)
        reticle += pVector(50, self.angleMouse - 0.15)
        
        for i in range(len(reticle)): #center the aim indicator on the player
            if i%2 == 0:
                reticle[i] += self.pos[0]
            else:
                reticle[i] += self.pos[1]
    
        ctx.create_polygon(*reticle, fill = "white",outline = "white")

    def checkCollisions(self):
        
        for platform in platformList:
            if platform.pos[0] <= self.pos[0] + 24 and platform.pos[0] + platform.length >= self.pos[0] - 24: 
                if platform.pos[1] >= self.pos[1] + 24 and platform.pos[1] <= self.pos[1] + 24 + self.vel[1]:
                    self.pos[1] = platform.pos[1] -24
                    self.vel[1] = 0
                    self.vel[0] = 0#Set running speed to 0 when landing.
                    self.airborne = False
                    break #Stop checking for collisions after the first one.
                elif self.pos[1] == platform.pos[1] -24:
                    self.airborne = False
                    break
                else:
                    self.airborne = True
                break
            else:
                self.airborne = True
                
    def onClick(self): #Fire the cannons! (spill the hot drinks!)
        if self.shotCharge >= 100:
            recoil = pVector(30, self.angleMouse + pi)#launch self with 30 force away from your mouse
            self.vel[0] += recoil[0]
            self.vel[1] += recoil[1]
            self.shotCharge -= 100
            
    def update(self):
        if self.shotCharge <= 200:
            self.shotCharge += 2
        
        self.angleMouse = atan2(yMouse - self.pos[1], xMouse - self.pos[0])
        self.checkCollisions()
        
        if keyA:
            self.pos[0] -= self.moveSpeed
        if keyD:
            self.pos[0] += self.moveSpeed
            
        if not self.airborne: #Automatically center the player on x = 400 gradually, but not enough to stop motion.
            if self.pos[0] >= 400:
                self.pos[0] += max(-1.5,(400-self.pos[0])/10)
            else:
                self.pos[0] += min(1.5,(400-self.pos[0])/10)
                
        if self.pos[1] >= 850:  #If you fall off the stage:
            self.pos = [400, -50]
        
        entity.update(self)
        self.draw()
        
####################
##   PROJECTILE   ##
####################

class projectile(entity):
    def __init__(self, id):
        projectileList.append(self)
        self.pos = [p.pos[0],p.pos[1]]
        self.vel = pVector(30 + uniform(-5,5), p.angleMouse + uniform(-0.5,0.5))
        self.rad = randInt(10,30)
        entity.__init__(self, id)
        
    def draw(self):
        ctx.create_oval(self.pos[0]-self.rad,self.pos[1]-self.rad,self.pos[0]+self.rad,self.pos[1]+self.rad, fill = "#da9d3f", outline = "#da9d3f")
        
    def update(self):
        self.draw()
        entity.update(self)
        
##################
##   PLATFORM   ##
##################

class platform(entity):
    def __init__(self, id, y, x=1200): # inputting an x value is optional. It defaults to the right side of the screen.
        platformList.append(self)
        entity.__init__(self, id)
        self.length = 50
        self.pos = [x,y]
        self.isFixed = True
    def crumble(self): #destroy self
        if (self.pos[0] + self.length >= -10):
            for i in range(randint(3,5)):
                particle(uniform(0,1),randint(3,5), randint(self.pos[0],self.pos[0]+self.length),randint(self.pos[1],self.pos[1]+self.length),*pVector(randint(0,10), uniform(0,2*pi)))
    def draw(self):
        ctx.create_rectangle(self.pos[0], self.pos[1], self.pos[0] + self.length, self.pos[1] + 5, fill = "white", outline = "white")

    def update(self):
        self.draw()
        entity.update(self)
        if (self.pos[0] + self.length <= -10): # delete self if off-screen
            self.crumble()

###################
##   PARTICLES   ##
###################

class particle(entity):
    def __init__(self, id, rad, x, y, xVel, yVel):
        self.pos = [x,y]
        self.vel = [xVel,yVel]
        self.rad = rad
        particleList.append(self)
        entity.__init__(self, id)
    def draw(self):
        ctx.create_oval(self.pos[0]-self.rad,self.pos[1]-self.rad,self.pos[0]+self.rad,self.pos[1]+self.rad, fill = "lightblue", outline = "white")
    def update(self):
        self.draw()
        entity.update(self)
        

##   Pause Function   ##

def pauseGame():
    global game
    print("Pause Game")
    if game:
        game = False
    else:
        game = True

##   Draw HUD   ##

def drawHUD():
    global score, p
    gaugeColour = ""
    if (p.shotCharge >= 100):
        gaugeColour = "#da9d3f"
    else:
        gaugeColour = "grey60"
        
        
    ctx.create_rectangle(30,230, 60, 230-(p.shotCharge), fill = gaugeColour, outline = "white", width = 3)
    ctx.create_polygon(63,130,70,135,70,125, fill="white", outline="white")

##   Main Update   ##
def mainUpdate(): #updates everything
    global t, entityList
    for i in range(len(entityList)): #loops through the list of entities and calls update in all of them
        entityList[i].update()
    ctx.update()
    ctx.delete(ALL)
    t += 1

##   Input Handlers   ##

def mouseClickHandler( event ):
    global p

    p.onClick() #call the Onclick function in the player class

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
    while True:
        sleep(1/30)
        if game:
            mainUpdate()
            drawHUD()
            if t%2 == 0:
                p = platform(t,500)

root.after( 0, runGame )

ctx.bind( "<Button-1>", mouseClickHandler )
ctx.bind( "<Motion>", mouseMotionHandler )
ctx.bind( "<Key>", keyDownHandler )
ctx.bind( "<KeyRelease>", keyUpHandler )


ctx.pack()
ctx.focus_set()
root.mainloop()
