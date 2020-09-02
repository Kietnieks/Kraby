# XXX Add a simple map design
# XXX introduce jumping,slow falling,side glideing.
# XXX introduce coustum sprites/backgrounds
# XXX
# XXX Internal needs:
# XXX - update rate control:
# XXX   - on fast systems, limit the maximum update tick rate
# XXX   - on slow systems, scale up the move size per tick
# XXX - background
# XXX   - when drawing, a horizontal scroll position selects what portion of
# XXX     the background is blitted onto the screen, and also offsets the
# XXX     sprite position (presumably all positions are tracked in absolute
# XXX     coordinates and adjusted for the scroll only during display)
# XXX   - the background is also responsible for supplying the ground height
# XXX     and horizontal obstacle positions to limit-check moves
# XXX     - the best performance might be if we limit-check horizontal moves
# XXX       at the highest point, so each update might perform up moves, then
# XXX       horizontal moves, then down moves
# XXX   - maybe, the background is text-encoded, and characters reference
# XXX     different image files for tiling
import sys
import os
import pygame
pygame.init()
root = sys.path[0]

class KeyCombo:
    event_types = (pygame.KEYDOWN,pygame.KEYUP)
    def __init__(self,outputs):
        self.my_keys = set()
        self.outputs = []
        for row in outputs:
            s = set(row[1:])
            self.outputs.append((row[0],s))
            self.my_keys |= s
        self.active_keys = set()
    def handle_event(self,event):
        if event.type not in self.event_types:
            return
        if event.key not in self.my_keys:
            return
        if event.type == pygame.KEYDOWN:
            self.active_keys.add(event.key)
        else:
            self.active_keys.remove(event.key)
    def get_value(self):
        for val,s in self.outputs:
            if self.active_keys == s:
                return val
        return self.outputs[-1][0]

class Sprite:
    def __init__(self,image_file,scale=None):
        self.image = pygame.image.load(image_file)
        if scale:
            self.image = pygame.transform.rotozoom(self.image,0,scale)
        self.rect = self.image.get_rect()
        self.event_listeners = dict(
                hmove = KeyCombo([
                        (-1,pygame.K_a),
                        (1,pygame.K_d),
                        (0,),
                        ])
                )
    def draw(self,screen):
        speed = 3
        hdir = self.event_listeners['hmove'].get_value()
        self.rect = self.rect.move([speed*hdir,0])
        screen.blit(self.image, self.rect)
    def handle_event(self,event):
        for el in self.event_listeners.values():
            el.handle_event(event)


size = width, height = 640, 480
black = 0, 0, 0
grey = 50, 50, 50
screen = pygame.display.set_mode(size)

#player = Sprite("intro_ball.gif")
player = Sprite(os.path.join(root,"blue goblin.png"),scale=0.25)

clock = pygame.time.Clock()
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

    ms_elapsed = clock.tick(60)
    screen.fill(grey)
    player.draw(screen)
    pygame.display.flip()
