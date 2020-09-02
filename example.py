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

class Background:
    class Strip:
        def __init__(self,height,width):
            self.height = height
            self.width = width
        def __repr__(self):
            return "Strip(%d,%d)" %(self.height,self.width)
    def __init__(self,width,height):
        self.width = width
        self.height = height
        self.strip_list = [
                self.Strip(50,200),
                self.Strip(100,200),
                self.Strip(150,200),
                self.Strip(100,200),
                self.Strip(200,200),
                self.Strip(100,500),
                ]
        self.strip_total = sum(x.width for x in self.strip_list)
        self.screen = pygame.display.set_mode((width,height))
        self.set_scroll(0)
    def get_strips(self,start,end):
        '''Returns strips overlapping the range (start,end).

        Return value is (starting_offset,strips), where starting_offset
        is the absolute x coordinate of the start of the leftmost strip.
        '''
        offset = 0
        strips = []
        for strip in self.strip_list:
            if offset >= end:
                break # we've passed the right edge
            offset += strip.width
            if offset <= start:
                continue # we're before the left edge
            strips.append(strip)
        starting_offset = offset - sum(x.width for x in strips)
        return (starting_offset,strips)
    def set_scroll(self,pos):
        self.scroll = pos
        # Now construct an image of the visible part of the background.
        # - first, build an appropriate sized surface, filled with a color
        self.image = pygame.Surface((self.width,self.height))
        grey = 50, 50, 50
        self.image.fill(grey)
        # - now, extract the visible portion of the background configuration
        offset,strips = self.get_strips(self.scroll,self.scroll+self.width)
        # - convert the returned offset based on the current scroll position;
        #   this should be 0, or negative if the first strip overhangs the
        #   left edge of the screen
        offset -= self.scroll
        # - now go through all the strips, using each as a guide for painting
        #   in an area in the image being created
        green = 0, 100, 0
        for strip in strips:
            r = pygame.Rect(
                    offset,
                    self.height-strip.height,
                    strip.width,
                    strip.height,
                    )
            self.image.set_clip(r)
            self.image.fill(green)
            offset += strip.width
        self.image.set_clip(None)
    def get_vert_bb(self,rect):
        # Return a rectangle ranging from the top of the highest strip under
        # the input rectangle to the top of the screen. The width is arbitrarily
        # set to the full screen width.
        offset,strips = self.get_strips(rect.left,rect.right)
        floor = max(x.height for x in strips)
        return pygame.Rect(self.scroll,0,self.width,self.height-floor)
    def get_horiz_bb(self,rect):
        # Return a rectangle ranging from the bottom of the input rectangle to
        # the top of the screen, and as wide as it can be without overlapping
        # the terrain.
        floor = rect.bottom
        right,strips = self.get_strips(rect.left,self.scroll+self.width)
        for strip in strips:
            if strip.height > self.height - floor:
                break
            right += strip.width
        offset,strips = self.get_strips(self.scroll,rect.right)
        left_width = sum(x.width for x in strips)
        left = offset + left_width
        for strip in reversed(strips):
            if strip.height > self.height - floor:
                break
            left -= strip.width
        return pygame.Rect(left,0,right-left,floor)
    def draw(self,player):
        margin = 150
        # scroll + margin < cx
        #   scroll < cx - margin
        # scroll + width - margin > cx
        #   scroll > cx - width + margin
        min_scroll = player.rect.centerx + margin - self.width
        max_scroll = player.rect.centerx - margin
        min_scroll = min(self.strip_total - self.width,min_scroll)
        max_scroll = max(0,max_scroll)
        if self.scroll < min_scroll:
            self.set_scroll(min_scroll)
        if self.scroll > max_scroll:
            self.set_scroll(max_scroll)
        self.screen.blit(self.image,self.image.get_rect())
        player_rect = player.rect.move([-self.scroll,0])
        self.screen.blit(player.image, player_rect)

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
    def update(self,now,ms_elapsed,key_state,background):
        def scale_speed(speed):
            '''Return the number of pixels to move in this tick.

            Input is the tick length in ms and the desired speed
            in pixels per second.
            '''
            return speed * ms_elapsed / 1000
        long_press_time = 500
        # vertical motion
        v = key_state.active_keys.get(pygame.K_w)
        if v is None:
            vspeed = 600 # normal fall (gravity)
        elif now - v > long_press_time:
            vspeed = 100 # slow fall
        else:
            vspeed = -200 # jump
        bounding_box = background.get_vert_bb(self.rect)
        new_rect = self.rect.move([0,scale_speed(vspeed)])
        self.rect = new_rect.clamp(bounding_box)
        # horizontal motion
        d = self.hmove
        l = set([d[x] for x in key_state.active_keys if x in d])
        if len(l) == 1:
            bounding_box = background.get_horiz_bb(self.rect)
            hspeed = next(iter(l))
            new_rect = self.rect.move([scale_speed(hspeed),0])
            self.rect = new_rect.clamp(bounding_box)

background = Background(640,480)
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

    player.update(now,ms_elapsed,key_state,background)
    background.draw(player)
    pygame.display.flip()
