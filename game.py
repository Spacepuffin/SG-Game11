from tkinter import *
from math import *
from time import *
from random import *

root = Tk()
root.overrideredirect(True)
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
ctx = Canvas( root, width=1280, height=1024, background="dodgerblue" )
ctx.pack()

##############################
####   GLOBAL VARIABLES   ####
##############################
def setInitialValues():
    #General Variables:
    global game, t, score, scrSpd, gravity, platGen, platChoices
    game = True
    t = 0
    score = 0 #score; also counter for time
    scrSpd = 25 #scroll speed
    gravity = 2
    platGen = []#Whether each row is producing platforms
    for i in range(4):
        platGen.append(choice([-2,-5,-13]))
        
    #Lists of Object instances:
    global entityList, platformList, projectileList, particleList
    entityList = []
    platformList = []
    projectileList = []

    #player instance:
    global p
    p = player()
    
    #Input-related Variables:
    global keyA, keyD, xMouse, yMouse
    keyA = False
    keyD = False
    xMouse = 0
    yMouse = 0

    #Buttons:
    global quitButton, pauseButton, resetButton
    quitButton = Button( root, text = "E X I T", command = root.destroy, font = ("Small Fonts", 24), relief = FLAT)
    quitButton.pack
    pauseButton = Button( root, text = "R E S U M E", command = pauseGame, font = ("Small Fonts", 24), relief = FLAT)
    pauseButton.pack
    resetButton = Button( root, text = "R E S E T", command = resetGame, font = ("Small Fonts", 24), relief = FLAT)
    resetButton.pack
    
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

    #Platforms at the Start of the Game:
    for i in range(26):
        platform(550,i*50+5)
        
def pVector(magnitude, angle):
	x = magnitude*cos(angle)
	y = magnitude*sin(angle)
	return [x, y]

####################
####   ENTITY   ####
####################

class entity():
    global entityList
    def __init__(self):
        entityList.append(self)
        self.pos = [0,0]
        self.vel = [0,0]
        self.isFixed = False #determines if it moves relative to everything or not
        self.airborne = True
        self.delete = False #Marks this object for deletion
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
    def __init__(self):
        entity.__init__(self)
        self.pos = [400, 525]
        self.shotCharge = 100
        self.health = 5
        self.invulnerable = 0
        self.moveSpeed = 10
        self.angleMouse = 0
        
    def draw(self):
        if not (self.invulnerable > 0 and t%4 < 2): #blink if invulnerable
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
        else: #if the loop is not broken (No platforms were touched):
           self.airborne = True
                
    def onClick(self): #Fire the cannons! (spill the hot drinks!)
        if self.shotCharge >= 100:
            recoil = pVector(30, self.angleMouse + pi)#launch self with 30 force away from your mouse
            self.vel[0] += recoil[0]
            self.vel[1] += recoil[1]
            for i in range(5):
                projectile()
            self.shotCharge -= 100
            
    def update(self):
        if self.shotCharge < 200:
            self.shotCharge += 2
            if not self.airborne: #Charge more while on the ground
                self.shotCharge += 0.5
        
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
                
        if self.pos[1] >= 1100:  #If you fall off the stage:
            self.pos = [400, -50]
            self.vel = [0,0]
            if not tutorial > 0:
                self.health -= 1
                self.invulnerable = 60 #give 60 ticks of invulnerable after falling off the stage.
            
        if self.invulnerable > 0: 
            self.invulnerable -= 1 # tick down the invuln timer if you're invulnerable


        if self.health <= 0:
            endGame()
        
        entity.update(self)
        self.draw()
        
####################
##   PROJECTILE   ##
####################

class projectile(entity):
    def __init__(self):
        projectileList.append(self)
        entity.__init__(self)
        self.pos = [p.pos[0],p.pos[1]]
        self.vel = pVector(30 + uniform(-5,5), p.angleMouse + uniform(-pi/4,pi/4))
        self.rad = randint(13,30)
        
    def draw(self):
        ctx.create_oval(self.pos[0]-self.rad,self.pos[1]-self.rad,self.pos[0]+self.rad,self.pos[1]+self.rad, fill = "#bf8d5f", outline = "#da9d3f")
        
    def update(self):
        self.draw()
        entity.update(self)
        if self.pos[1] >= 1100:
            self.delete = True
        
##################
##   PLATFORM   ##
##################

class platform(entity):
    def __init__(self, y, x=1280, length=50): # inputting an x value is optional. It defaults to the right side of the screen.
        platformList.append(self)
        entity.__init__(self)
        self.length = length
        self.pos = [x,y]
        self.isFixed = True
    def crumble(self): #destroy self
        for i in range(randint(3,5)):
            particle(randint(3,5), randint(self.pos[0],self.pos[0]+self.length),randint(self.pos[1],self.pos[1]+self.length/2),*pVector(randint(20,30), uniform(-pi*5/6,-pi*3/4)))
        self.delete = True

    def draw(self):
        ctx.create_rectangle(self.pos[0], self.pos[1], self.pos[0] + self.length, self.pos[1] + 5, fill = "white", outline = "white")

    def update(self):
        self.draw()
        entity.update(self)
        if self.pos[0] + self.length <= -100:# delete self if off screen by enough
            self.delete = True
        if (self.pos[0] + self.length >= p.pos[0]-24 and p.pos[1] + 24 == self.pos[1]): #if the player is touching the platform
            if (self.pos[0] + self.length - scrSpd < p.pos[0]-24 + p.vel[0]): #if the player is stepping off the platform
                self.crumble()
        for proj in projectileList:
            if (hypot(self.pos[0]-proj.pos[0],self.pos[1]-proj.pos[1]) <= proj.rad or hypot(self.pos[0]+self.length-proj.pos[0],self.pos[1]-proj.pos[1])<= proj.rad):
                self.crumble()
                break
            

###################
##   PARTICLES   ##
###################

class particle(entity):
    def __init__(self, rad, x, y, xVel, yVel):
        entity.__init__(self)
        self.pos = [x,y]
        self.vel = [xVel,yVel]
        self.rad = rad
    def draw(self):
        ctx.create_oval(self.pos[0]-self.rad, self.pos[1]-self.rad,self.pos[0]+self.rad,self.pos[1]+self.rad, fill = "lightblue", outline = "white")
    def update(self):
        self.draw()
        entity.update(self)
        if self.pos[1] >= 1100:
            self.delete = True
        

##   Pause Function   ##

def pauseGame():
    global game, quitButton, pauseButton, resetButton
    if game:
        game = False
        ctx.create_rectangle(0,0,1280,1024,fill="gray10",outline="",stipple="gray50")
        ctx.create_text(640,300, text = "- p a u s e -", font = ("Small Fonts", 112, "bold"), fill = "White")
        quitButton.place(x=350, y=600, width=150, height=60)
        pauseButton.place(x=540, y=600, width=200, height=60)
        resetButton.place(x=780, y=600, width=150, height=60)
    else:
        game = True
        quitButton.place(x=-200, y=-200, width=150, height=60) # Hide the buttons when not paused
        pauseButton.place(x=-200, y=-200, width=150, height=60)
        resetButton.place(x=-200, y=-200, width=150, height=60)

##   End Game Function   ##
def endGame():
    global game, quitButton, resetButton
    game = False
    
    ctx.create_rectangle(0,0,1280,1024,fill="black",outline="",stipple="gray50")
    ctx.create_text(640,400, text = "- t r y    a g a i n ? -", font = ("Small Fonts", 112, "bold"), fill = "White")
    quitButton.place(x=350, y=600, width=150, height=60)
    resetButton.place(x=780, y=600, width=150, height=60)

##   Reset The Game   ##

def resetGame(): #Essentially just setInitialValues but it also moves the buttons back first.
    global quitButton, pauseButton, resetButton
    quitButton.place(x=-200, y=400, width=150, height=60) # Hide the buttons when not paused
    pauseButton.place(x=-200, y=400, width=150, height=60)
    resetButton.place(x=-200, y=400, width=150, height=60)
    setInitialValues()
    
##   Draw HUD   ##

def drawHUD():
    global score, p
    #Tutorial Images
    ctx.create_image(self.pos[0], self.pos[1], image = pBodyImgs[13], anchor = CENTER) AAAAAAaa

    #Ammo Gauge
    gaugeColour = ""
    if (p.shotCharge >= 100):
        gaugeColour = "#bf8d5f"
    else:
        gaugeColour = "grey60"
    ctx.create_rectangle(30,330, 70, 330-(p.shotCharge * 1.5), fill = gaugeColour, outline = "white", width = 4)
    ctx.create_polygon(67,185,55,190,55,180, fill="white", outline="white")

    #Health Indicator
    ctx.create_text(100,30, text = "Health:",font = ("Small Fonts", 36, "bold"), anchor = NW, fill = "White")
    for i in range(p.health):
        ctx.create_rectangle(260+50*i, 45, 300+50*i, 75, fill = "white", outline  = "white")

    #Score Value
    ctx.create_text(1250 - (160 + len(str(score))*20), 30, text = "Score: " + str(score),font = ("Small Fonts", 36, "bold"), anchor = NW, fill = "White")

##   Platform Layout Generator   ##
def platGenerator():
    global platGen
    platChoices = [5] + [8]*2 + [13]*4 + [21]*2 + [26] #At the start, there is a higher chance for longer platforms
    gapChoices = [3] + [5]*2 + [8] 

    if score >= 500:
        platChoices += [5]
        platChoices.remove(26)
        gapChoices += [8]
        gapChoices.remove(3)
    if score >= 1500:
        platChoices += [3]
        platChoices.remove(21)
        platChoices.remove(13)
        gapChoices += [13]
        gapChoices.remove(5)
    if score >= 3000:
        platChoices += [3]
        platChoices.remove(13)
        platChoices.remove(13)
        gapChoices += [13] + [21]*2
        gapChoices.remove(5)
    
    if (t%2==0):# Every other frame:
        if tutorial>0: #if it's the tutorial, only make platforms on one level with no gaps
            platform(550)
        else:
            for i,row in enumerate(platGen):
                if row > 1:
                    platform((i+1)*200+150)
                    platGen[i] -=1
                elif row < -1:
                    platGen[i] += 1
                elif row == 1:
                    platform((i+1)*200+150)
                    platGen[i] = choice(gapChoices)*-1 #alternate between platforms and gaps.
                else:
                    platGen[i] = choice(platChoices)

##   Main Update   ##
def mainUpdate(): #updates everything
    global score, t, entityList

    for entity in entityList: #loops through the list of entities and calls update in all of them
        entity.update()
    while True:
        for i, entity in enumerate(entityList): #Remove one item from entitylist at once.
            if entity.delete: #Remove entities that are marked for deletion.
                entityList.pop(i)
                if type(entity) == platform:
                    for p,plat in enumerate(platformList):
                        if plat.delete:
                            platformList.pop(p)
                            break
                if type(entity) == projectile:
                    for q,proj in enumerate(projectileList):
                        if proj.delete:
                            projectileList.pop(q)
                            break
                break
        else:
            break #Break from the loop if there are no more objects marked for deletion.
    platGenerator()
    t += 1
    score += 1

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
    global tutorial = 2
    while True:
        if game:
            ctx.delete(ALL)
            mainUpdate()
            drawHUD()
        ctx.update()
        sleep(1/30)
    

root.after( 0, runGame )

ctx.bind( "<Button-1>", mouseClickHandler )
ctx.bind( "<Motion>", mouseMotionHandler )
ctx.bind( "<Key>", keyDownHandler )
ctx.bind( "<KeyRelease>", keyUpHandler )


ctx.pack()
ctx.focus_set()
root.mainloop()
