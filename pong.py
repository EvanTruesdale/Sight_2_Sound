import sys, time
import pygame

from src.SoundConverter import Image2Sound

FPS = 10
size = width, height = 128, 128
power = 6
paddle_dist = 8
ballspeed = [1,1]
up = [0,-2]
down = [0,2]
black = 0,0,0

# PyGame Initialization
pygame.init()
pygame.mixer.init()
fpsclock = pygame.time.Clock()
screen = pygame.display.set_mode(size, 0, 8)
pygame.display.set_caption('Pong')

# Import Assets
ball = pygame.image.load('assets/ball.png')
ball_rect = ball.get_rect()
ball_rect.left = width/2; ball_rect.top = height/2

leftpaddle = pygame.image.load('assets/paddle.png')
leftpaddle_rect = leftpaddle.get_rect()
leftpaddle_rect.left = paddle_dist; leftpaddle_rect.top = height/2

rightpaddle = pygame.image.load('assets/paddle.png')
rightpaddle_rect = rightpaddle.get_rect()
rightpaddle_rect.right = width-paddle_dist; rightpaddle_rect.top = height/2

# Image2Sound stuff
AudioGenerator = Image2Sound(power=power, duration=1)

while 1:

    # Get player inputs
    status = pygame.key.get_pressed()
    if status[pygame.K_w]:
        if leftpaddle_rect.top > 0:
            leftpaddle_rect = leftpaddle_rect.move(up)
    if status[pygame.K_s]:
        if leftpaddle_rect.bottom < height:
            leftpaddle_rect = leftpaddle_rect.move(down)
    if status[pygame.K_UP]:
        if rightpaddle_rect.top > 0:
            rightpaddle_rect = rightpaddle_rect.move(up)
    if status[pygame.K_DOWN]:
        if rightpaddle_rect.bottom < height:
            rightpaddle_rect = rightpaddle_rect.move(down)

    # Update ball movement
    ball_rect = ball_rect.move(ballspeed)
    if ball_rect.top < 0 or ball_rect.bottom > height:
        ballspeed[1] = -ballspeed[1]
    if ball_rect.bottom > leftpaddle_rect.top and ball_rect.top < leftpaddle_rect.bottom:
        if ball_rect.left < leftpaddle_rect.right:
            ballspeed[0] = -ballspeed[0]
    if ball_rect.bottom > rightpaddle_rect.top and ball_rect.top < rightpaddle_rect.bottom:
        if ball_rect.right > rightpaddle_rect.left:
            ballspeed[0] = -ballspeed[0]

    # Game End Logic
    if ball_rect.right < leftpaddle_rect.left:
        print('Right Wins')
        ball_rect.left = width/2
        ball_rect.top = height/2
        screen.fill(black)
        screen.blit(ball, ball_rect)
        screen.blit(leftpaddle, leftpaddle_rect)
        screen.blit(rightpaddle, rightpaddle_rect)
        pygame.display.update()
        time.sleep(3)
    if ball_rect.left > rightpaddle_rect.right:
        print('Left Wins')
        ball_rect.left = width/2
        ball_rect.top = height/2
        screen.fill(black)
        screen.blit(ball, ball_rect)
        screen.blit(leftpaddle, leftpaddle_rect)
        screen.blit(rightpaddle, rightpaddle_rect)
        pygame.display.update()
        time.sleep(3)

    # Draw
    screen.fill(black)
    screen.blit(ball, ball_rect)
    screen.blit(leftpaddle, leftpaddle_rect)
    screen.blit(rightpaddle, rightpaddle_rect)

    # Update
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    pygame.display.update()

    # Get audio
    pxarray = pygame.surfarray.array2d(screen).astype('uint8')
    audio = AudioGenerator.get_audio(pxarray, output_file='audio/last_frame.wav')
    sound = pygame.mixer.Sound('audio/last_frame.wav')
    pygame.mixer.Sound.play(sound)
    fpsclock.tick(FPS)
