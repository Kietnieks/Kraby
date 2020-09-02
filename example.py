# XXX Add a simple map design
# XXX introduce jumping,slow falling,side glideing.
# XXX introduce coustum sprites/backgrounds
# XXX
import sys
import os
import pygame
pygame.init()
root = sys.path[0]

class Sprite:
    def __init__(self,image_file,scale=None):
        self.image = pygame.image.load(image_file)
        if scale:
            self.image = pygame.transform.rotozoom(self.image,0,scale)
        self.rect = self.image.get_rect()
        self.active_keys = set()
    def draw(self,screen):
        speed = 3
        for key,motion in (
                (pygame.K_a,[-speed,0]),
                (pygame.K_d,[speed,0]),
                ):
            if self.active_keys == set([key]):
                self.rect = self.rect.move(motion)
        screen.blit(self.image, self.rect)
    def handle_event(self,event):
        valid_keys = set([pygame.K_a,pygame.K_d])
        if event.type == pygame.KEYDOWN:
            if event.key in valid_keys:
                self.active_keys.add(event.key)
        if event.type == pygame.KEYUP:
            if event.key in valid_keys:
                self.active_keys.remove(event.key)


size = width, height = 640, 480
black = 0, 0, 0
grey = 50, 50, 50
screen = pygame.display.set_mode(size)

#player = Sprite("intro_ball.gif")
player = Sprite(os.path.join(root,"blue goblin.png"),scale=0.25)

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        player.handle_event(event)

    if False:
        if ballrect.left < 0 or ballrect.right > width:
            speed[0] = -speed[0]
        if ballrect.top < 0 or ballrect.bottom > height:
            speed[1] = -speed[1]

    screen.fill(grey)
    player.draw(screen)
    pygame.display.flip()
