from tkinter import *
from math import *
from time import *
from random import *

root = Tk()
root.overrideredirect(True)
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
ctx = Canvas( root, width=1280, height=1024, background="#bc7ebc" )
ctx.pack()

##############################
####   GLOBAL VARIABLES   ####
##############################
def setInitialValues():
    #General Variables:
    global game, t, score, scrSpd, gravity, platGen, platCounter, snowmanChance
    game = True
    t = 0
    score = 0 #score; also counter for time
    scrSpd = 12 #scroll speed
    gravity = 2
    platGen = []#Whether each row is producing platforms
    for i in range(4):
        platGen.append(choice([-2,-5,-13]))
    platCounter = 0
    snowmanChance = 0


    #Background-related stuff
    global background1, background2, background3, bInc1, bInc2, bInc3 # I didn't use 3 dimensional arrays here for the sake of readability.
    background1 = [[0,320],[300,620],[400,520],[650,770],[1050,370]] #list of points for the first background part.
    background2 = [[0,640],[200,440],[550,790],[650,690],[850,890],[1100,640]]
    background3 = [[0,960],[150,1110],[350,910],[600,1160],[900,860],[1150,1110]]
    bInc1 = 1 #whether to go up or down next
    bInc2 = 1
    bInc3 = 1

    #Lists of Object instances:
    global entityList, platformList, projectileList, snowmanList
    entityList = []
    platformList = []
    projectileList = []
    snowmanList = []

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
    global pBodyImgs, pArmImgs, snowmanImgs, tutImgs, platImgs
    pBodyImgs = []
    pArmImgs = []
    snowmanImgs = []
    tutImgs = []
    platImgs = []
    for i in range(14): # load Character body images
        #the art program I drew the sprites in automatically names them name0000.gif so I can use a for loop to load many at a time.
        fileName = "assets\character" + format(i, '04d')+ ".gif" 
        image = PhotoImage(file = fileName)
        pBodyImgs.append(image)
    for i in range(8): # load Arm images
        fileName = "assets\mugArm" + format(i, '04d')+ ".gif"
        image = PhotoImage(file = fileName)
        pArmImgs.append(image)
    for i in range(8): #load platform images
        fileName = "assets\snowman"+ format(i, '04d')+ ".gif"
        image = PhotoImage(file = fileName)
        snowmanImgs.append(image)
    for i in range(4): #load tutorial images
        fileName = "assets\Tut" + format(i, '04d')+ ".gif"
        image = PhotoImage(file = fileName)
        tutImgs.append(image)
    for i in range(4): #load platform images
        fileName = "assets\platform"+ format(i, '04d')+ ".gif"
        image = PhotoImage(file = fileName)
        platImgs.append(image)
        
    #Platforms at the Start of the Game:
    for i in range(27):
        platform(550,i*48+5)
        
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


#########################
##   SNOWMAN ENEMIES   ##
#########################

class snowman(entity):
    def __init__(self, y, x = 1300):
        snowmanList.append(self)
        entity.__init__(self)
        self.pos = [x,y]
        self.speedMod = 1
        self.baseSpeed = -10
        self.vel = [self.baseSpeed-scrSpd,0]

    def draw(self):
        ctx.create_image(self.pos[0], self.pos[1], image = snowmanImgs[t%8], anchor = CENTER)

    def checkCollisions(self):
        for platform in platformList:
            if platform.pos[0] <= self.pos[0] + 24 and platform.pos[0] + platform.length >= self.pos[0] - 24: 
                if platform.pos[1] >= self.pos[1] + 24 and platform.pos[1] <= self.pos[1] + 24 + self.vel[1]:
                    self.pos[1] = platform.pos[1] -24
                    self.vel[1] = 0
                    self.vel[0] = self.baseSpeed-scrSpd#Set running speed to base speed when landing.
                    self.airborne = False
                    if platform.neighbors in [[0,1],[0,0]]: #if the snowman is at the end of the group of platforms
                        if p.pos[1]<= self.pos[1]:
                            self.vel[1] -= 30 # jump
                    break #Stop checking for collisions after the first one.
        else: #if the loop is not broken (No platforms were touched):
           self.airborne = True
        
    def update(self):
        self.draw()
        entity.update(self)

        self.checkCollisions()
        
        ## Converge to base speed in air. 
        if self.airborne: 
            self.vel[0] += ((self.baseSpeed-scrSpd)*self.speedMod - self.vel[0])/10
        else:
            self.vel[0] *= self.speedMod #Accelerate when on the ground.

        self.speedMod = min(1+sqrt(score)/50,2)

        for proj in projectileList: #Test for collision with projectiles
            if (hypot(self.pos[0]-proj.pos[0],self.pos[1]-proj.pos[1]) <= proj.rad+24):
                for i in range(10):
                    particle(randint(5,10), uniform(self.pos[0]-24,self.pos[0]+24),uniform(self.pos[1]-24,self.pos[1]+24),*pVector(randint(20,30), uniform(-pi*5/6,-pi*3/4)))
                self.delete = True
                p.shotCharge += 100
                break
        
        if hypot(p.pos[0]-self.pos[0],p.pos[1]-self.pos[1])<= 48: #Test for collisions with player
            if p.invulnerable <= 0:
                p.health-=1
                p.invulnerable = 60
                for i in range(10):
                    particle(randint(5,10), uniform(self.pos[0]-24,self.pos[0]+24),uniform(self.pos[1]-24,self.pos[1]+24),*pVector(randint(20,30), uniform(-pi*5/6,-pi*3/4)))
                self.delete = True

        if self.pos[1] >= 1100:
            self.delete = True
        
##################
##   PLATFORM   ##
##################

class platform(entity):
    def __init__(self, y, x=1325, length=48): # inputting an x value is optional. It defaults to the right side of the screen.
        platformList.append(self)
        entity.__init__(self)
        self.length = length
        self.pos = [x,y]
        self.isFixed = True
        self.neighbors = [0,0] #whether the block has adjacent blocks
        
    def crumble(self): #destroy self
        for i in range(3):
            particle(randint(3,5), randint(self.pos[0],self.pos[0]+self.length),randint(self.pos[1],self.pos[1]+self.length/2),*pVector(randint(20,30), uniform(-pi*5/6,-pi*3/4)))
        self.delete = True

    def draw(self):
        if self.neighbors == [0,1]:
            ctx.create_image(self.pos[0], self.pos[1], image = platImgs[0], anchor = NW)
        elif self.neighbors == [1,0]:
            ctx.create_image(self.pos[0], self.pos[1], image = platImgs[1], anchor = NW)
        elif self.neighbors == [0,0]:
            ctx.create_image(self.pos[0], self.pos[1], image = platImgs[2], anchor = NW)
        else:
            ctx.create_image(self.pos[0], self.pos[1], image = platImgs[3], anchor = NW)

    def update(self):
        if self.pos[0] + self.length <= -100:# delete self if off screen by enough
            self.delete = True
        if (self.pos[0] + self.length >= p.pos[0]-24 and p.pos[1] + 24 == self.pos[1]): #if the player is touching the platform
            if (self.pos[0] + self.length - scrSpd < p.pos[0]-24 + p.vel[0]): #if the player is stepping off the platform
                self.crumble()
        for proj in projectileList:
            if (hypot(self.pos[0]-proj.pos[0],self.pos[1]-proj.pos[1]) <= proj.rad or hypot(self.pos[0]+self.length-proj.pos[0],self.pos[1]-proj.pos[1])<= proj.rad):
                self.crumble()
                break
            
        for platform in platformList:
            if platform != self:
                if self.pos[1] == platform.pos[1]:
                    if platform.pos[0] <= self.pos[0] <= platform.pos[0]+platform.length+24: #if there is a platform directly to the left of this platform:
                        self.neighbors[0] = 1
                        break
        else:
            self.neighbors[0] = 0
            
        for platform in platformList:
            if self.pos[1] == platform.pos[1]:
                if platform.pos[0] <= self.pos[0]+self.length < platform.pos[0]+platform.length: #if there is a platform directly to the right of this platform:
                    self.neighbors[1] = 1
                    break
        else:
            self.neighbors[1] = 0
            
        self.draw()
        entity.update(self)
        

###################
##   PARTICLES   ##
###################

class particle(entity): #Snow particles when platforms are broken or snowmen die
    def __init__(self, rad, x, y, xVel, yVel):
        entity.__init__(self)
        self.pos = [x,y]
        self.vel = [xVel,yVel]
        self.rad = rad
    def draw(self):
        ctx.create_oval(self.pos[0]-self.rad, self.pos[1]-self.rad,self.pos[0]+self.rad,self.pos[1]+self.rad, fill = "white", outline = "white")
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
        quitButton.destroy()
        pauseButton.destroy()
        resetButton.destroy()
        
        quitButton = Button( root, text = "E X I T", command = root.destroy, font = ("Small Fonts", 24), relief = FLAT) 
        quitButton.pack
        pauseButton = Button( root, text = "R E S U M E", command = pauseGame, font = ("Small Fonts", 24), relief = FLAT)
        pauseButton.pack
        resetButton = Button( root, text = "R E S E T", command = resetGame, font = ("Small Fonts", 24), relief = FLAT)
        resetButton.pack

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
    quitButton.destroy()
    pauseButton.destroy()
    resetButton.destroy()
    setInitialValues()
    
##   Draw HUD   ##

def drawHUD():
    global score, p
    #Tutorial Images
    
    if tutorial == 2: #If it's the Keyboard Tutorial
        ctx.create_text(200,300, text = "Use A and D to move horizontally.",font = ("Small Fonts", 30, "bold"), anchor = NW, fill = "White")
        if t%6<=2:
            ctx.create_image(950, 320, image = tutImgs[2], anchor = CENTER)
        else:
            ctx.create_image(950, 320, image = tutImgs[3], anchor = CENTER)
            
    if tutorial == 1: #If it's the Mouse Tutorial
        ctx.create_text(300,300, text = "Click to spill your Hot Cocoa!",font = ("Small Fonts", 30, "bold"), anchor = NW, fill = "White")
        if t%6<=2:
            ctx.create_image(950, 320, image = tutImgs[0], anchor = CENTER)
        else:
            ctx.create_image(950, 320, image = tutImgs[1], anchor = CENTER)

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
    global platGen, platCounter
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
    
    
    if platCounter+scrSpd >= 48:
        platCounter=0
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
    platCounter += scrSpd
    
def snowmanGenerator():
    global snowmanChance
    genPositions = [325,525,725,925]
    if tutorial == 0:
        if randint(0,100)<= snowmanChance+2:
            snowman(choice(genPositions))
        snowmanChance = sqrt(score)/10

## Draw Background ##

def drawBackground():
    global background1, background2, background3, bInc1, bInc2, bInc3
    if background1[-1][0]<= 1100:
        while True:
            increment = randint(50,300)
            if 0 < background1[-1][1] + increment <= 426: #if the resulting point lands within the acceptable range:
                background1.append([background1[-1][0]+increment, background1[-1][1]+increment *bInc1])
                break
            bInc1 *= -1
    if background2[-1][0]<= 1100:
        while True:
            increment = randint(50,300)
            if 426 < background2[-1][1] + increment <= 853: #if the resulting point lands within the acceptable range:
                background2.append([background2[-1][0]+increment, background2[-1][1]+increment *bInc2])
                break
            bInc2 *= -1
    if background3[-1][0]<= 1100:
        while True:
            increment = randint(50,300)
            if 853 < background3[-1][1] + increment <= 1280: #if the resulting point lands within the acceptable range:
                background3.append([background3[-1][0]+increment, background3[-1][1]+increment * bInc3])
                break
            bInc3 *= -1
            
    ptsList1 = [] # Convert to one dimensional array to feed into tkinter polygon
    ptsList2 = []
    ptsList3 = []
    for i in range(len(background1)):
        ptsList1 += background1[i]
    for i in range(len(background2)):
        ptsList2 += background2[i]
    for i in range(len(background3)):
        ptsList3 += background3[i]
        
    ctx.create_polygon(*ptsList1,1280,1024,0,1024, fill = "purple")
    ctx.create_polygon(*ptsList2,1280,1024,0,1024, fill = "magenta")
    ctx.create_polygon(*ptsList3,1280,1024,0,1024, fill = "pink")

    for point in background1:
        point[0]-=3
    for point in background2:
        point[0]-=5
    for point in background3:
        point[0]-=7
        
    if background1[1][0]<0: #if the next point is off the screen on the left side, delete this point.
        background1.pop(0)
    if background2[1][0]<0:
        background2.pop(0)
    if background3[1][0]<0: 
        background3.pop(0)
        

##   Main Update   ##
def mainUpdate(): #updates everything
    global score, t, entityList, scrSpd
    drawBackground()
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
    snowmanGenerator()
    platGenerator()
    scrSpd= int(min(17+sqrt(score)/5,24))
    t += 1
    if not (tutorial > 0): #Don't count score during tutorial
        score += 1

##   Input Handlers   ##

def mouseClickHandler( event ):
    global p, tutorial

    p.onClick() #call the Onclick function in the player class

    if tutorial == 1:
        tutorial = 0

def mouseMotionHandler( event ):
    global xMouse, yMouse

    xMouse = event.x
    yMouse = event.y

def keyDownHandler( event ):
    global keyA, keyD, tutorial
    
    if event.keysym in ["Escape", "p", "P", "q", "Q"]: # Bind Escape Key, P and Q to pause
        pauseGame()
    if event.keysym in ["a", "A"]:
        keyA = True
        if tutorial == 2:
            tutorial = 1
    if event.keysym in ["d", "D"]:      
        keyD = True
        if tutorial == 2:
            tutorial = 1
            
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
    global tutorial
    tutorial = 2
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
