# Importing modules
import pygame as pg
from pygame.sprite import Sprite
from settings import *
from utils import *
from os import path
from math import *
from random import randint

vec = pg.math.Vector2



# Creates Rules For Collisions
def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

# Sets position off of collision
def collide_with_walls(sprite, group, dir):
    hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
    # Horizontal Collisions
    if dir == "x":
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    
    # Vertical Collisions
    if dir == "y":
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.width / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.width / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

# Creates Player Class with Sprite as Super Class
class Player(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        # This provides us with raster images for use in animation or otherwise
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.spritesheet.get_image(0,0,TILESIZE,TILESIZE)
        #self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()   
        # Player Motion
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.pos = vec(x,y) * TILESIZE
        self.cofric = PLAYER_FRIC
        self.hit_rect = PLAYER_HIT_RECT
        # Start with current frames and last update at zero so we can cycle through animations
        self.current_frame = 0
        self.last_update = 0
        # Accounting for the states of the player.
        self.jumping = False
        self.moving = False
        self.coins = 0
        print("player instance created")
        self.load_images()

    # Gets player input
    def get_keys(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_d]:
            self.acc.x = PLAYER_ACC
        if keys[pg.K_w]:
            self.acc.y = -PLAYER_ACC
        if keys[pg.K_s]:
            self.acc.y = PLAYER_ACC
        if keys[pg.K_f]:
            self.pew()
        # Unsure if required
        # if self.vel.x != 0 and self.vel.y != 0:
        #     self.vel *= 0.707106
    def pew(self):
        PewPew(self.game, self.hit_rect.centerx, self.rect.centery, TILESIZE/8, TILESIZE/8, 0, -10)

    def jump(self):
        pass
    # Picks Up Player Skins
    def load_images(self):
        self.idle_frames = [self.spritesheet.get_image(0,0, TILESIZE, TILESIZE), 
                            self.spritesheet.get_image(32,0, TILESIZE, TILESIZE), 
                            self.spritesheet.get_image(0,32, TILESIZE, TILESIZE), 
                            self.spritesheet.get_image(32,32, TILESIZE, TILESIZE)]
    # Cycles through Character Animations
    def animate(self):
        now = pg.time.get_ticks()
        if not self.jumping and not self.moving:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
                bottom = self.rect.bottom
                self.image = self.idle_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        elif self.moving:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
                bottom = self.rect.bottom
                self.image = self.moving_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

    #Checks for coin collection
    # def check_coins(self):
    #     hits = pg.sprite.spritecollide(self, self.coins, True)
    #     self.game.score += len(hits)

    #Rules for Character Movement
    def update(self):
        self.animate()
        self.acc = vec(0,0)
        self.get_keys()
        # self.acc += self.vel * self.cofric
        self.acc.x += self.vel.x * self.cofric
        self.acc.y += self.vel.y * self.cofric
        self.vel += self.acc
        # Limits Max Fall Speed
        # Prompted AI to prevent funneling through tiles
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        if abs(self.vel.y) < 0.1:
            self.vel.y = 0
        # Updates position off of Vel and Acc
        # Used exponential calculation with game.dt to update position
        # Movement in Ice
        # self.pos += self.vel * self.game.dt + 0.5 * self.acc * (self.game.dt ** 2)
        # self.pos += self.vel * self.game.dt + 0.5 * self.acc
        self.pos += self.vel + 0.5 * self.acc
        tile_hits = pg.sprite.spritecollide(self, self.game.all_tiles, False)
        if tile_hits:
            if tile_hits[0].variant == "ice":
                self.cofric = 0
        else:
                self.cofric = -.1
        # Coin Collection
        hits = pg.sprite.spritecollide(self, self.game.all_coins, True)
        for h in hits:
            self.coins += 1
            self.game.score += 1
            self.game.pickup_snd.play()
            for i in range(20):
                Particle(self.game, hits[0].rect.x, hits[0].rect.y)
                hits[0].kill()
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.all_walls, 'y')
        self.rect.center = self.hit_rect.center

class PewPew(Sprite):
    def __init__(self, game, x, y, w, h, sx, sy):
        self.groups = game.all_sprites, game.all_pews
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((w,h))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = TILESIZE / 8
        pg.draw.circle(self.image, YELLOW, self.rect.center, self.radius)
        self.rect.x = x
        self.rect.y = y
        self.speed_x = sx
        self.speed_y = sy
        self.fired = False

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.y < 0 or self.rect.y > HEIGHT:
            self.kill

# Copied over and modifed code for class Player
class Mob(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        # This provides us with raster images for use in animation or otherwise
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.spritesheet.get_image(0,0,TILESIZE,TILESIZE)
        self.image.set_colorkey(RED)
        #self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y 
        self.speed = 275
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE
        self.hit_rect = MOB_HIT_RECT
        # Start with current frames and last update at zero so we can cycle through animations
        self.current_frame = 0
        self.last_update = 0
        # Accounting for the states of the mob.
        self.jumping = False
        self.moving = False
        print("mob instance created")
        self.load_images()

    # Picks Up Mob Skins
    def load_images(self):
            self.idle_frames = [self.spritesheet.get_image(64,32, TILESIZE, TILESIZE), 
                                self.spritesheet.get_image(96,0, TILESIZE, TILESIZE), 
                                self.spritesheet.get_image(64,32, TILESIZE, TILESIZE), 
                                self.spritesheet.get_image(96,32, TILESIZE, TILESIZE)]
    # Cycles through Mob Animations
    def animate(self):
        now = pg.time.get_ticks()
        if not self.jumping and not self.moving:
            # Decides when to switch to next frame
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
                bottom = self.rect.bottom
                self.image = self.idle_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        elif self.moving:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
                bottom = self.rect.bottom
                self.image = self.moving_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

    #Rules for Mob Movement
    def follow(self,obj):
        # Make the mob follow the player, which is the objective
        direction = vec(obj.rect.centerx - self.rect.centerx, obj.rect.centery - self.rect.centery)
        if direction.length() > 0:
            direction = direction.normalize()
        self.vel = direction
    
    def update(self):   
        self.animate()
        self.follow(self.game.player)
        self.pos += self.vel * self.speed * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.all_walls, 'y')
        self.rect.center = self.hit_rect.center

# Creates Wall Class with Sprite as Super Class
class Wall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE
        self.rect.center = self.pos
        print("Wall Instance Created")

# Copied Wall Class to Make FloorTile Class with Sprite as Super Class
class FloorTile(Sprite):
    def __init__(self, game, x, y, color):
        self.groups = game.all_sprites, game.all_tiles
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE
        self.rect.center = self.pos
        print("Tile Instance Created")
        self.variant = ""

# Copied Wall Class to Make Particle Class with Sprite as Super Class
class Particle(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_particles
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE/4, TILESIZE/4))
        self.image.fill(GOLD)
        self.rect = self.image.get_rect()
        self.vel = vec(randint(-180,180),randint(-180,180))
        self.pos = vec(x,y)
        self.speed = 0.25
        self.rect.center = self.pos
        self.countdown = Cooldown()
        self.countdown.event_time = floor(pg.time.get_ticks()/1000)
        print("Particle Instance Created")
        print(self.rect.x)
        print(self.rect.y)

    # Randomizes Directions and Removes after Duration
    def update(self):
        self.countdown.ticking()
        self.pos += self.vel * self.speed * self.game.dt
        if self.countdown.delta > 1:
            self.kill()
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

# Copied Wall Class to Make Coin Class with Sprite as Super Class
class Coin(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_coins
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        pg.draw.circle(self.image, GOLD, (TILESIZE/2,TILESIZE/2), TILESIZE/2)
        self.image.set_colorkey(BLACK)
        #self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE
        self.rect.center = self.pos
        print("Coin Instance Created")