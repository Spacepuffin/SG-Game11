from tkinter import *
from math import *
from time import *

root = Tk()
ctx = Canvas(root, width=1000, height=600, background="black")


##############################
####   GLOBAL VARIABLES   ####
##############################
def setInitialValues():
    global score, scrSpd, entityList, p
    score = 0 #score; also counter for time
    scrSpd = 30 #scroll speed
    entityList = []
    p = player(0)

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
        self.imgList = []
        self.touchingGround = False
        self.isFixed = False #determines if it moves relative to everything or not

    def draw(self): #draw this obj
        ctx.create_oval(self.pos[0]-20,self.pos[1]-20,self.pos[0]+20,self.pos[1]+20, fill="blue")
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
    def __init__(self, id):
        entity.__init__(self, id)
        self.shootClip = False
        self.canShoot = True

    def update(self):
        #shooty stuff here
        entity.update(self)

##################
####   MAIN   ####
##################

def mainUpdate(): #updates everything
    global entityList
    for i in range(len(entityList)): #loops through the list of entities and calls update in all of them
        entityList[i].update()
        
def runGame():
    setInitialValues()
    while True:
        mainUpdate()
        

runGame()
screen.pack()
screen.focus_set()
root.mainloop()
