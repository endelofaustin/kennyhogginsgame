#!/usr/bin/python3

import sys, pygame
from engineglobals import EngineGlobals
pygame.init()

# must be after the above global variables are defined
import physics

# create a display window with the above width and height
screen = pygame.display.set_mode((EngineGlobals.width, EngineGlobals.height))

# load a font to use for displaying text
myfont = pygame.font.SysFont('Comic Sans MS', 20)

# load kenny's face
all_sprites = pygame.sprite.Group()
kenny = physics.PhysicsSprite()
all_sprites.add(kenny)

#load lucinda and set her to a different starting position than the default 0,0
lucinda  = pygame.image.load("./artwork/lucinda.png")
# move the entire rectangle encompassing Lucinda by 201 pixels horizontally and 201 pixels vertically
lucindarect = lucinda.get_rect()
lucindarect.left += 201
lucindarect.right += 201
lucindarect.top += 201
lucindarect.bottom += 201


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

    # this is commented out so that we can test only kenny's movement for now
    #lucindarect = lucindarect.move(speed)
    #if lucindarect.left < 0 or lucindarect.right > width:
    #    speed[0] = -speed[0]
    #if lucindarect.top < 0 or lucindarect.bottom > height:
    #    speed[1] = -speed[1]

    screen.fill(EngineGlobals.gray)
    all_sprites.draw(screen)
    screen.blit(lucinda, lucindarect)

    textsurface = myfont.render("down is %s" % kenny.speed[1], False, (255, 255, 255)).convert_alpha()
    screen.blit(textsurface, (0,0))

    pygame.display.flip()
