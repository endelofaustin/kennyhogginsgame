#!/usr/bin/python3

import sys, pygame
from engineglobals import EngineGlobals
pygame.init()

# must be after the above global variables are defined
import physics

# create a display window with the above width and height
EngineGlobals.screen = pygame.display.set_mode((EngineGlobals.width, EngineGlobals.height))

# load a font to use for displaying text
myfont = pygame.font.SysFont('Comic Sans MS', 20)

# load kenny's face
all_sprites = pygame.sprite.Group()
kenny = physics.PhysicsSprite()
all_sprites.add(kenny)

#load lucinda and set her to a different starting position than the default 0,0
lucinda  = pygame.image.load("./artwork/lucinda.png")
# move the entire rectangle encompassing Lucinda by 201 pixels horizontally and 201 pixels vertically
##lucindarect = lucinda.get_rect()
#lucindarect.left += 201
#lucindarect.right += 201
#lucindarect.top += 201
#lucindarect.bottom += 201


# this is the main game loop!
while 1:
    # if the window gets closed, end the program
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    
    # get a list of all keys that are currently pressed
    pressed_keys = pygame.key.get_pressed()

    # interpret arrow keys into velocity
    kenny.speed[0] = 0
    if pressed_keys[pygame.K_LEFT]:
        kenny.speed[0] -= 2
    if pressed_keys[pygame.K_RIGHT]:
        kenny.speed[0] += 2

    
    all_sprites.update()


    # Creation of a basic platform that Kenny can jump onto 
    # A nested list 

    platform = [ 
         #  0,1,2,3,4,5,6,7,8,0,1,2,3,4,5,6,7,8
           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
           [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
           [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0], ]

    # iterate through the nested list and render a rectangle if a 1 is in that position
    WHITE = (255, 255, 255,)
    GREEN = (0, 255, 0,)
    EngineGlobals.screen.fill(WHITE)

    for row in platform:
        for item in row:
            if item == 0:
                pass
            elif item == 1:
                # arguments for rect placements are (x axis, y axis, height width
                pygame.draw.rect(EngineGlobals.screen, GREEN, (120,500,350,100))

            
    all_sprites.draw(EngineGlobals.screen)

    textsurface = myfont.render("down is %s" % kenny.speed[1], False, (255, 0, 255)).convert_alpha()
    EngineGlobals.screen.blit(textsurface, (0,0))

    pygame.display.flip()
