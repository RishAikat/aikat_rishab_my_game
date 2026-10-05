# This file was created by: Rish Aikat
# Content inspired by: Chris Cozort
# I do solemnly swear to create concise and informative comments

'''
The game engine consists of three (four) basic components:
Input - keys, buttons, voice, mouse, touch, breath, movement, control stick
Process - input processed (direction of control, magnitude)
Output - Draw new frames pixels, sound, haptic (senses)
(Store)
'''

#Importing required modules

import pygame as pg
from os import path
from settings import *
from sprites import *
from utils import *


# Class Blueprint for Entire Game
class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        print('game class initialized')
        self.clock = pg.time.Clock()
        self.running = True
        self.playing = True

    #Loading files
    def load_data(self, map):
        self.game_dir = path.dirname(__file__)
        self.img_dir = path.join(self.game_dir, 'images')
        self.snd_dir = path.join(self.game_dir, 'sound')
        self.map = Map(path.join(self.game_dir, map))


    def new(self):
        self.load_data('level1.txt')
        self.all_sprites = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()
        # Instantiate Player Here  
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                if tile == 'P':
                    self.player = Player(self, col, row)

    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS)/1000
            self.events() # Gets Player Input
            self.update() # Updates Game
            self.draw() # Draws Sprites

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    # This block of code handles processing of changes based on input
    def update(self):
        self.all_sprites.update()

    #Draws game components
    def draw(self):
        self.screen.fill(BLUE)
        self.all_sprites.draw(self.screen)
        pg.display.flip()

#Starts Game
if __name__ == "__main__":
    g = Game()


while g.running:
    g.new()
    g.run()

pg.quit()
