# XXX Add a simple map design
# XXX introduce jumping,slow falling,side glideing.
# XXX introduce coustum sprites/backgrounds
# XXX
# XXX Internal needs:
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

class KeyState:
    '''Track the current state of all keys.

    self.active_keys has an entry for each key currently depressed.
    The entry holds the key-down time, so long presses can be
    handled specially.
    '''
    event_types = (pygame.KEYDOWN,pygame.KEYUP)
    def __init__(self):
        self.active_keys = dict()
    def handle_event(self,event,now):
        if event.type not in self.event_types:
            return
        if event.type == pygame.KEYDOWN:
            self.active_keys[event.key] = now
        else:
            del(self.active_keys[event.key])

class Sprite:
    def __init__(self,image_file,scale=None):
        self.image = pygame.image.load(image_file)
        if scale:
            self.image = pygame.transform.rotozoom(self.image,0,scale)
        self.rect = self.image.get_rect()
        hpix_per_sec = 200
        self.hmove = {
                pygame.K_a:-hpix_per_sec,
                pygame.K_d:hpix_per_sec,
                }
    def draw(self,screen):
        screen.blit(self.image, self.rect)
    def update(self,now,ms_elapsed,key_state):
        def scale_speed(speed):
            '''Return the number of pixels to move in this tick.

            Input is the tick length in ms and the desired speed
            in pixels per second.
            '''
            return speed * ms_elapsed / 1000
        bounding_box = pygame.Rect(0,0,640,480) #XXX from background eventually
        long_press_time = 500
        # vertical motion
        v = key_state.active_keys.get(pygame.K_w)
        if v is None:
            vspeed = 600 # normal fall (gravity)
        elif now - v > long_press_time:
            vspeed = 50 # slow fall
        else:
            vspeed = -200 # jump
        new_rect = self.rect.move([0,scale_speed(vspeed)])
        self.rect = new_rect.clamp(bounding_box)
        # horizontal motion
        d = self.hmove
        l = set([d[x] for x in key_state.active_keys if x in d])
        if len(l) == 1:
            hspeed = next(iter(l))
            hpix = hspeed * ms_elapsed / 1000
            new_rect = self.rect.move([hpix,0])
            self.rect = new_rect.clamp(bounding_box)


size = width, height = 640, 480
black = 0, 0, 0
grey = 50, 50, 50
screen = pygame.display.set_mode(size)

player = Sprite(os.path.join(root,"blue goblin.png"),scale=0.25)
key_state = KeyState()
event_handlers=[
        key_state,
        ]

clock = pygame.time.Clock()
while 1:
    ms_elapsed = clock.tick(20)
    now = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        for eh in event_handlers:
            eh.handle_event(event,now)

    player.update(now,ms_elapsed,key_state)
    screen.fill(grey)
    player.draw(screen)
    pygame.display.flip()
