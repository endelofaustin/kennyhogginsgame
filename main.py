#!/usr/bin/python3

import sys, pygame, physics
from engineglobals import EngineGlobals
from decimal import Decimal

pygame.init()
# create a display window
EngineGlobals.screen = pygame.display.set_mode((EngineGlobals.width, EngineGlobals.height))

# load a font to use for displaying text
myfont = pygame.font.SysFont('Comic Sans MS', 20)
textsurface = myfont.render("Arrow keys move and Ctrl or Up to jump", False, (255, 0, 255)).convert_alpha()

# for now we will simply create a sprite group called all_sprites for the convenience of
# using it to update and draw any sprites we add to this global group
all_sprites = pygame.sprite.Group()
# load kenny's face
kenny = physics.PhysicsSprite()
all_sprites.add(kenny)

#load lucinda and set her to a different starting position than the default 0,0
#lucinda  = pygame.image.load("./artwork/lucinda.png")
# move the entire rectangle encompassing Lucinda by 201 pixels horizontally and 201 pixels vertically
##lucindarect = lucinda.get_rect()
#lucindarect.left += 201
#lucindarect.right += 201
#lucindarect.top += 201
#lucindarect.bottom += 201


# A nested list 

platform = [ 
          #  0,1,2,3,4,5,6,7,8,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
            [0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] ]

EngineGlobals.platform = platform

# this is the main game loop!
while 1:
    # if the window gets closed, end the program
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL or event.key == pygame.K_UP:
                if kenny.speed[1] >= 0:
                    kenny.speed[1] = -3

    # get a list of all keys that are currently pressed
    pressed_keys = pygame.key.get_pressed()

    # interpret arrow keys into velocity
    kenny.speed[0] = 0
    if pressed_keys[pygame.K_LEFT]:
        kenny.speed[0] -= Decimal('1.5')
    if pressed_keys[pygame.K_RIGHT]:
        kenny.speed[0] += Decimal('1.5')

    all_sprites.update()

    # Creation of a basic platform that Kenny can jump onto 
    # A nested list 


    # iterate through the nested list and render a rectangle if a 1 is in that position
    WHITE = (255, 255, 255,)
    GREEN = (0, 255, 0,)
    EngineGlobals.screen.fill(WHITE)

# in order to draw rectangles in the platform object we need to iterate through the matrix and increment counters by a count of 16 for the purpose 
# of keeping track of the drawings location and then 
    xcounter = 0
    ycounter = 0 

    for row in platform:
        textsurface = myfont.render(f'{xcounter}', False, (255, 0, 255)).convert_alpha()
        xcounter = 0
        ycounter += 32
        
        for item in row:
            xcounter += 32
            if item == 0:
                pass
            elif item == 1:
                # arguments for rect placements are (x axis, y axis, height width)
                pygame.draw.rect(EngineGlobals.screen, GREEN, (xcounter,ycounter,32, 32))

    all_sprites.draw(EngineGlobals.screen)

    # debug text
    EngineGlobals.screen.blit(textsurface, (0,0))

    pygame.display.flip()
