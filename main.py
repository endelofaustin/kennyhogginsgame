#!/usr/bin/python3
import sys, pygame
pygame.init()

width, height = 800, 600
speed = [0, 0]
gray = 40, 40, 40
scale_factor = 4

# create a display window with the above width and height
screen = pygame.display.set_mode((width, height))

# load a font to use for displaying text
myfont = pygame.font.SysFont('Comic Sans MS', 20)
textsurface = myfont.render('Use the arrow keys to move the pigster', False, (255, 255, 255)).convert_alpha()

ball = pygame.image.load("./artwork/kennyface1.png").convert_alpha()
ballrect = ball.get_rect()
# scale the image by multiplying its width (right - left) by scale_factor and heigh (bottom - top) by scale_factor
ball = pygame.transform.scale(ball, ((ballrect.right - ballrect.left) * scale_factor, (ballrect.bottom - ballrect.top) * scale_factor))
lucinda  = pygame.image.load("./artwork/lucinda.png")
ballrect = ball.get_rect()

# This is setting the lucinda object in a different starting position than kenny

lucindarect = lucinda.get_rect()
lucindarect.left += 201
lucindarect.right += 201
lucindarect.top += 201
lucindarect.bottom += 201

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    
    pressed_keys = pygame.key.get_pressed()
    speed = [0, 0]
    if pressed_keys[pygame.K_LEFT]:
        speed[0] -= 2
    if pressed_keys[pygame.K_RIGHT]:
        speed[0] += 2
    if pressed_keys[pygame.K_UP]:
        speed[1] -= 2
    if pressed_keys[pygame.K_DOWN]:
        speed[1] += 2

    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        ballrect = ballrect.move([-speed[0], 0])
    if ballrect.top < 0 or ballrect.bottom > height:
        ballrect = ballrect.move([0, -speed[1]])
    
    #lucindarect = lucindarect.move(speed)
    #if lucindarect.left < 0 or lucindarect.right > width:
    #    speed[0] = -speed[0]
    #if lucindarect.top < 0 or lucindarect.bottom > height:
    #    speed[1] = -speed[1]

    screen.fill(gray)
    screen.blit(ball, ballrect)
    #screen.blit(lucinda, lucindarect)
    screen.blit(textsurface, (0,0))
    pygame.display.flip()
