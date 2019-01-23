from tkinter import *
from math import *
from time import *
from random import *

root = Tk()
root.overrideredirect(True)
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight())) # for fullscreen
ctx = Canvas( root, width=1280, height=1024, background="#6d7d96" )
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
    gravity = 3
    platGen = []#Whether each row is producing platforms
    for i in range(4):
        platGen.append(choice([-2,-5,-13]))
    platCounter = 0
    snowmanChance = 0


    #Background-related stuff
    global background # I didn't use 3 dimensional arrays here for the sake of readability.
    background = [[[0,320],[300,620],[400,520],[650,770],[1250,170], [1450, 370]],
                [[0,640],[200,440],[550,790],[650,690],[850,890],[1100,640], [1250, 790], [1300,740]],
                [[0,960],[150,1110],[350,910],[600,1160],[900,860],[1150,1110],[1350, 910]]]


    #Lists of Object instances:
    global entityList, platformList, projectileList
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
    global pBodyImgs, pArmImgs, snowmanImgs, tutImgs, platImgs, titleImg
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

    titleImg = PhotoImage (file = "assets/title0000.gif")
        
    #Platforms at the Start of the Game:
    for i in range(29):
        platform(550,i*48)
        
def pVector(magnitude, angle): # Converts an angle and a magnitude to x and y values.
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
        if self.isFixed: #if an object is fixed, it scrolls along with scrSpd (i.e. platforms, I had ideas for other stuff to be fixed but didn't get around to it)
            self.pos[0] -= scrSpd
        else:
            self.pos[0] += self.vel[0] #otherwise it falls due to gravity
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
            if self.airborne: # use air sprites if in air
                if self.vel[1] > 0:
                    ctx.create_image(self.pos[0], self.pos[1], image = pBodyImgs[13], anchor = CENTER) 
                    ctx.create_image(self.pos[0], self.pos[1], image = pArmImgs[7], anchor = CENTER)
                else:
                    ctx.create_image(self.pos[0], self.pos[1], image = pBodyImgs[12], anchor = CENTER)
                    ctx.create_image(self.pos[0], self.pos[1], image = pArmImgs[6], anchor = CENTER)
            else: #loop through run animation otherwise
                ctx.create_image(self.pos[0], self.pos[1], image = pBodyImgs[t%12], anchor = CENTER)
                ctx.create_image(self.pos[0], self.pos[1], image = pArmImgs[t%6], anchor = CENTER)

        

    def checkCollisions(self):
        
        for platform in platformList: #check all platforms for collision
            if platform.pos[0] <= self.pos[0] + 24 and platform.pos[0] + platform.length >= self.pos[0] - 24:  #compare x values
                if platform.pos[1] >= self.pos[1] + 24 and platform.pos[1] <= self.pos[1] + 24 + self.vel[1]:  #compare y values
                    self.pos[1] = platform.pos[1] -24
                    self.vel[1] = 0
                    self.vel[0] = 0#Set running speed to 0 when landing.
                    self.airborne = False
                    break #Stop checking for collisions after the first one.
        else: #if the loop is not broken (No platforms were touched):
           self.airborne = True
                
    def onClick(self): #Fire the cannons! (spill the hot drinks!)
        if self.shotCharge >= 100: # if you have enough ammo
            recoil = pVector(45, self.angleMouse + pi)#launch self with 45 force away from your mouse
            self.vel[0] += recoil[0]
            self.vel[1] += recoil[1]
            for i in range(7): # Shoot 7 globs
                projectile()
            self.shotCharge -= 100 #lower ammo so your shots are limited
            
    def update(self):
        if self.shotCharge < 200:
            self.shotCharge += 2
            if not self.airborne: #Charge more while on the ground
                self.shotCharge += 0.5
        
        self.angleMouse = atan2(yMouse - self.pos[1], xMouse - self.pos[0]) # use tan-1 to calculate the angle of the mouse
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
        self.vel = pVector(randint(35,40) + uniform(-5,5), p.angleMouse + uniform(-pi/5,pi/5))
        self.rad = randint(15,30)
        
    def draw(self):
        ctx.create_oval(self.pos[0]-self.rad,self.pos[1]-self.rad,self.pos[0]+self.rad,self.pos[1]+self.rad, fill = "#bf8d5f", outline = "#bf8d5f")
        
    def update(self):
        self.draw()
        entity.update(self)
        if self.pos[1] >= 1100: # Delete self when sufficiently offstage
            self.delete = True


#########################
##   SNOWMAN ENEMIES   ##
#########################

class snowman(entity):
    def __init__(self, y, x = 1300):
        entity.__init__(self)
        self.pos = [x,y]
        self.speedMod = 1
        self.baseSpeed = -5
        self.vel = [self.baseSpeed-scrSpd,0]

    def draw(self):
        ctx.create_image(self.pos[0], self.pos[1], image = snowmanImgs[t%8], anchor = CENTER) #loop through the snowman run animation

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
                            self.vel[1] -= 25 # jump
                    break #Stop checking for collisions after the first one.
        else: #if the loop is not broken (No platforms were touched):
           self.airborne = True
        
    def update(self):
        global score
        self.draw()
        entity.update(self)
        self.checkCollisions()
        
        ## Converge to base speed in air. 
        if self.airborne: 
            self.vel[0] += ((self.baseSpeed-scrSpd)*self.speedMod - self.vel[0])/10
        else:
            self.vel[0] *= self.speedMod #Accelerate when on the ground.

        self.speedMod = min(1+sqrt(score)/100,2) # speed multiplier is proportional to sqrt of score.

        for proj in projectileList: #Test for collision with projectiles
            if (hypot(self.pos[0]-proj.pos[0],self.pos[1]-proj.pos[1]) <= proj.rad+24):
                for i in range(10):
                    particle(randint(5,10), uniform(self.pos[0]-24,self.pos[0]+24),uniform(self.pos[1]-24,self.pos[1]+24),*pVector(randint(20,30), uniform(-pi*5/6,-pi*3/4)))
                score += 100 #increase the score as a reward for melting killer snow homunculi
                self.delete = True
                break
        
        if hypot(p.pos[0]-self.pos[0],p.pos[1]-self.pos[1])<= 48: #Test for collisions with player
            if p.invulnerable <= 0:
                p.health-=1 #when colliding damage the player and make them invulnerable temporarily
                p.invulnerable = 60
                for i in range(10):
                    particle(randint(5,10), uniform(self.pos[0]-24,self.pos[0]+24),uniform(self.pos[1]-24,self.pos[1]+24),*pVector(randint(20,30), uniform(-pi*5/6,-pi*3/4))) #Make particles when destroyed
                self.delete = True

        if self.pos[1] >= 1100: # delete self when sufficiently off-stage
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
        self.isFixed = True # scroll along at scroll speed
        self.neighbors = [0,0] #whether the block has adjacent blocks
        
    def crumble(self): #Destroy self
        for i in range(3):
            particle(randint(3,5), randint(self.pos[0],self.pos[0]+self.length),randint(self.pos[1],self.pos[1]+self.length/2),*pVector(randint(20,30), uniform(-pi*5/6,-pi*3/4)))
        self.delete = True

    def draw(self): # Draw self
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
            if (self.pos[0] + self.length - scrSpd < p.pos[0] + p.vel[0]): #if the player is stepping off the platform
                self.crumble()
                
        for proj in projectileList: #Check for projectile collision using simple distance formula from either end
            if (hypot(self.pos[0]-proj.pos[0],self.pos[1]-proj.pos[1]) <= proj.rad or hypot(self.pos[0]+self.length-proj.pos[0],self.pos[1]-proj.pos[1])<= proj.rad):
                self.crumble() # break when hit by projectile
                break
            
        for platform in platformList:#Check for neighbors to the left 
            if platform != self:
                if self.pos[1] == platform.pos[1]:
                    if platform.pos[0] <= self.pos[0] <= platform.pos[0]+platform.length+24: #if there is a platform directly to the left of this platform:
                        self.neighbors[0] = 1
                        break
        else:
            self.neighbors[0] = 0
            
        for platform in platformList: #Check for neighbors to the right
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
    def __init__(self, rad, x, y, xVel, yVel):#takes arguments so you can set how they fly out, etc
        entity.__init__(self)
        self.pos = [x,y]
        self.vel = [xVel,yVel]
        self.rad = rad
    def draw(self): # Draw self
        ctx.create_oval(self.pos[0]-self.rad, self.pos[1]-self.rad,self.pos[0]+self.rad,self.pos[1]+self.rad, fill = "white", outline = "white")
    def update(self):
        self.draw()
        entity.update(self)
        if self.pos[1] >= 1050: # mark self for deletion when sufficiently off-screen
            self.delete = True
        

##   Pause   ##

def pauseGame():
    global game, quitButton, pauseButton, resetButton
    if game: #if the game is currently running, pause, and vice-versa
        game = False
        ctx.create_rectangle(0,0,1280,1024,fill="gray10",outline="",stipple="gray50") #dim the background
        ctx.create_text(640,300, text = "- p a u s e -", font = ("Small Fonts", 112, "bold"), fill = "White")
        quitButton.place(x=350, y=600, width=150, height=60) #give the options "exit", "resume", and "reset"
        pauseButton.place(x=540, y=600, width=200, height=60)
        resetButton.place(x=780, y=600, width=150, height=60)
        
    else:
        game = True #unpausing destroys the buttons, so they don't clog up the screen
        quitButton.destroy()
        pauseButton.destroy()
        resetButton.destroy()
        # define the buttons again so we can use them (as well as in other functions)
        quitButton = Button( root, text = "E X I T", command = root.destroy, font = ("Small Fonts", 24), relief = FLAT) 
        quitButton.pack
        pauseButton = Button( root, text = "R E S U M E", command = pauseGame, font = ("Small Fonts", 24), relief = FLAT)
        pauseButton.pack
        resetButton = Button( root, text = "R E S E T", command = resetGame, font = ("Small Fonts", 24), relief = FLAT)
        resetButton.pack

##   End Game   ##
def endGame():
    global game, quitButton, resetButton
    game = False
    ctx.create_rectangle(0,0,1280,1024,fill="black",outline="",stipple="gray50")
    ctx.create_text(640,300, text = "y o u r    s c o r e :   " + str(score), font = ("Small Fonts", 112, "bold"), fill = "White")
    ctx.create_text(640,450, text = "- t r y    a g a i n ? -", font = ("Small Fonts", 112, "bold"), fill = "White")
    quitButton.place(x=350, y=600, width=150, height=60) #give the options to exit or reset the game.
    resetButton.place(x=780, y=600, width=150, height=60)

##   Reset The Game   ##

def resetGame(): #Essentially just setInitialValues but it also moves the buttons back first.
    global quitButton, pauseButton, resetButton
    quitButton.destroy() #hide the buttons
    pauseButton.destroy()
    resetButton.destroy()
    setInitialValues() #reset everything ; start a new game
    
##   Draw HUD   ##

def drawHUD():
    global score, p
    #Tutorial Images

    if tutorial == 3:
        ctx.create_image(640, 400 + 30*sin(t/30), image = titleImg, anchor = CENTER)
        if t%30 <=20 :
            ctx.create_text(640,800, text = "- Click To Start -",font = ("Small Fonts", 52, "bold"), anchor = CENTER, fill = "White")
        
    else:
        if tutorial == 2: #If it's the Keyboard Tutorial
            ctx.create_text(200,300, text = "Use A and D to move left and right.",font = ("Small Fonts", 30, "bold"), anchor = NW, fill = "White")
            if t%18<=6:
                ctx.create_image(1000, 320, image = tutImgs[2], anchor = CENTER)
            else:
                ctx.create_image(1000, 320, image = tutImgs[3], anchor = CENTER)
                
        if tutorial == 1: #If it's the Mouse Tutorial
            ctx.create_text(300,300, text = "Click to fire your hot cocoa!",font = ("Small Fonts", 30, "bold"), anchor = NW, fill = "White")
            if t%18<=6:
                ctx.create_image(950, 320, image = tutImgs[0], anchor = CENTER)
            else:
                ctx.create_image(950, 320, image = tutImgs[1], anchor = CENTER)

        #Ammo Gauge
        gaugeColour = ""
        if (p.shotCharge >= 100):
            gaugeColour = "#bf8d5f" #Change colour when the shot is ready. Otherwise, it's grey.
        else:
            gaugeColour = "grey60"
        ctx.create_rectangle(30,330, 70, 330-(p.shotCharge * 1.5), fill = gaugeColour, outline = "white", width = 4)
        ctx.create_polygon(67,185,55,190,55,180, fill="white", outline="white")

        #Aim
        reticle = []
        reticle += pVector(40, p.angleMouse)
        reticle += pVector(50, p.angleMouse + 0.15)
        reticle += pVector(50, p.angleMouse - 0.15)
        
        for i in range(len(reticle)): #center the aim indicator on the player
            if i%2 == 0:
                reticle[i] += p.pos[0]
            else:
                reticle[i] += p.pos[1]
    
        ctx.create_polygon(*reticle, fill = "white",outline = "white")

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

    if score >= 500: #At certain score numbers, change the probabilities of the platforms spawning to make it harder!
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
    
    
    if platCounter+scrSpd >= 48: #create platforms at a rate proportional to the scroll speed, as to try to keep them spaced evenly
        #That's not always possible because scrollspeed is not always a divisor of the platform length.
        platCounter=0
        if tutorial>0: #if it's the tutorial, only make platforms on one level with no gaps
            platform(550)
        else:
            for i,row in enumerate(platGen):
                if row > 1: # if "row" is greater than one, it means that it is a platform
                    platform((i+1)*200+150)
                    platGen[i] -=1
                elif row < -1: #if it's negative that means it's a gap.
                    platGen[i] += 1
                elif row == 1: #if row is exactly 1 or -1, that means the platform is done.
                    platform((i+1)*200+150)
                    platGen[i] = choice(gapChoices)*-1 #alternate between platforms and gaps.
                else:
                    platGen[i] = choice(platChoices)
    platCounter += scrSpd


## Generate Snowman Enemies  ##
def snowmanGenerator():
    global snowmanChance
    genPositions = [325,525,725,925] ##All the platforms the snowmen can spawn on
    if tutorial == 0:
        if randint(0,100)<= snowmanChance+1: #start with a 1% chance per frame to spawn a snowman.
            snowman(choice(genPositions))
        snowmanChance = sqrt(score)/10 #Chance per frame to spawn a snowman is proportional to sqrt of score.
        

## Draw Background ##

def drawBackground():
    global background

    ptsLists = [[],[],[]] #later we need to turn the list of tuples into a single list of alternating x's and y's
    
    for i in range(3): #three mountain ranges.
        
        for point in background[i]: #shift x values for the mountains. The closer mountains move faster, simulating parallax.
            point[0]-=3*(i+1)
            
        if background[i][1][0]< 0: #if the next point is off the screen on the left side, delete this point.
            background[i].pop(0)
            
        if background[i][-1][0]<= 1300: # if the x coordinate of the last point is less than 1300
                targetY = randint(i*256,(i+1)*256) #pick a random target Y value
                targetX = background[i][-1][0] + abs(targetY - background[i][-1][1])  #place the target X farther by the difference (so that x and y change at the same rate)
                background[i].append([targetX,targetY])
            
        for point in background[i]: #points are smooshed into single list to feed into create_polygon
            ptsLists[i] += point
    
    ctx.create_polygon(*ptsLists[0],1280,1024,0,1024, fill = "#385177") #use ptsList to draw the mountain ranges
    ctx.create_polygon(*ptsLists[1],1280,1024,0,1024, fill = "#152d51")
    ctx.create_polygon(*ptsLists[2],1280,1024,0,1024, fill = "#041530")
    

##   Main Update   ##
def mainUpdate(): #updates everything
    global score, t, p, entityList, scrSpd
    drawBackground() #draw the backgrounds first, so they are behind everything. Also, draw them even during tutorial 3 (title screen)
    if tutorial <3:
        
        for entity in entityList: #loops through the list of entities and calls update in all of them
            entity.update()
        while True: # Keep looking for items to delete until loop is broken
            for i, entity in enumerate(entityList): #Each loop only removes one item from entitylist at a time, as to not mess up index order.
                if entity.delete: #Remove entities that are marked for deletion.
                    entityList.pop(i)
                    if type(entity) == platform: #if it's a platform or a projectile we also have to remove it from those lists.
                        for r,plat in enumerate(platformList):
                            if plat.delete:
                                platformList.pop(r)
                                break
                    if type(entity) == projectile:
                        for q,proj in enumerate(projectileList):
                            if proj.delete:
                                projectileList.pop(q)
                                break
                    break
            else:
                break #Break from the loop if there are no more objects marked for deletion.

        snowmanGenerator() #autogenerate enemies
        platGenerator() #autogenerate platforms
        scrSpd= int(min(17+sqrt(score)/5,24)) #scroll speed speeds up proportional to sqrt of score
        
        if tutorial == 0 : #Only count score if it's not the tutorial
            score += 1
            
        if p.health <= 0: #Stop the game if the player is out of health.
            endGame()
    drawHUD() #Draw all of the indicators, and buttons and stuff
    t += 1 #keep track of time


##   Input Handlers   ##
def mouseClickHandler( event ):
    global p, tutorial

    if tutorial in [3,1]: #These phases of the tutorial advance if you click.
        tutorial -= 1
    if tutorial <= 1: # Don't unlock shooting until this point in the tutorial
        p.onClick()#call the Onclick function in the player class

def mouseMotionHandler( event ): # simple mouse tracking :PP
    global xMouse, yMouse

    xMouse = event.x
    yMouse = event.y

def keyDownHandler( event ):
    global keyA, keyD, tutorial
    
    if event.keysym in ["Escape", "p", "P", "q", "Q"]: # Bind Escape Key, P and Q to pause (You can exit the game from the pause menu)
        pauseGame()
    if event.keysym in ["a", "A", "Left"]:#Move right or left is bound to a and d, but the player can use arrow keys too if they want.
        keyA = True
        if tutorial == 2:
            tutorial = 1
    if event.keysym in ["d", "D", "Right"]:      
        keyD = True
        if tutorial == 2:
            tutorial = 1
            
def keyUpHandler( event ):
    global keyA, keyD
                        
    if event.keysym in ["a", "A", "Left"]: #I have separate variables for A and D so they can fire simultaneously and don't conflict
        keyA = False
    if event.keysym in ["d", "D", "Right"]:      
        keyD = False
                        
#####################
####   RUNGAME   ####
#####################
    
def runGame():
    setInitialValues() #Set Initial Values
    
    global tutorial #Tutorial is outside setInitialValues because I want it to be called only once ever, when the game is first opened up.
    tutorial = 3 #This number represents what stage the tutorial is on; 0 is the normal game.
    
    while True:
        if game:
            ctx.delete(ALL) #I'm deleting everything because it's easy to forget to add items to this list :/
            mainUpdate() #Main update
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
