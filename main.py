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

# load kenny's face
ball = pygame.image.load("./artwork/kennyface1.png").convert_alpha()
ballrect = ball.get_rect()
# scale the image by multiplying its width (right - left) by scale_factor and heigh (bottom - top) by scale_factor
ball = pygame.transform.scale(ball, ((ballrect.right - ballrect.left) * scale_factor, (ballrect.bottom - ballrect.top) * scale_factor))

#load lucinda and set her to a different starting position than the default 0,0
lucinda  = pygame.image.load("./artwork/lucinda.png")
ballrect = ball.get_rect()
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
    speed = [0, 0]
    if pressed_keys[pygame.K_LEFT]:
        speed[0] -= 2
    if pressed_keys[pygame.K_RIGHT]:
        speed[0] += 2
    if pressed_keys[pygame.K_UP]:
        speed[1] -= 2
    if pressed_keys[pygame.K_DOWN]:
        speed[1] += 2

    # move the rectangle by whatever velocity was determined;
    # but if it moves outside the window, move it back to where it was
    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        ballrect = ballrect.move([-speed[0], 0])
    if ballrect.top < 0 or ballrect.bottom > height:
        ballrect = ballrect.move([0, -speed[1]])
    
    # this is commented out so that we can test only kenny's movement for now
    #lucindarect = lucindarect.move(speed)
    #if lucindarect.left < 0 or lucindarect.right > width:
    #    speed[0] = -speed[0]
    #if lucindarect.top < 0 or lucindarect.bottom > height:
    #    speed[1] = -speed[1]

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
    
    DISPLAY = pygame.display.set_mode((800,600), 0,32)
    WHITE = (255, 255, 255,)
    GREEN = (0, 255, 0,)
    DISPLAY.fill(WHITE)

    for row in platform:
        for item in row:
            if item == 0:
                pass
            elif item == 1:
                # arguments for rect placements are (x axis, y axis, height width
                pygame.draw.rect(DISPLAY, GREEN, (120,500,350,100))

            
#   screen.fill(gray)
    screen.blit(ball, ballrect)
#    screen.blit(lucinda, lucindarect)
    screen.blit(textsurface, (0,0))
    pygame.display.flip()
