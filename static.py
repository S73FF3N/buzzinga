# -*- coding: utf-8 -*-

import sys
import os
import random
import pygame
from pathlib import Path

# Always use the directory where the .exe or .py is located
if getattr(sys, 'frozen', False):
    # PyInstaller: use directory of the executable in dist for ROOT_EXTENDED
    BASE_PATH = Path(os.path.dirname(sys.executable))
    ROOT_EXTENDED = BASE_PATH / "data"
    STATIC_FOLDER = Path(sys._MEIPASS) / "staticfiles"
else:
    BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))
    ROOT_EXTENDED = BASE_PATH / "data"
    STATIC_FOLDER = BASE_PATH / "staticfiles"

class Static:
    BLACK = 0, 0, 0
    WHITE = 255, 255, 255
    ORANGE = 201, 87, 16
    RED = 235, 26, 26
    LIGHT_RED = 220, 32, 25
    GREEN = 51, 102, 0
    LIGHT_GREEN = 0, 255, 0
    YELLOW = 255, 255, 0
    BLUE = 12, 27, 69
    LIGHT_BLUE = 0, 102, 204
    YELLOW = 235, 217, 26
    GREY = 125, 119, 119
    BASE_PATH = BASE_PATH
    ROOT_EXTENDED = ROOT_EXTENDED
    STATIC_FOLDER = STATIC_FOLDER
    GAME_FOLDER_IMAGES = "images/"
    GAME_FOLDER_SOUNDS = "sounds/"
    GAME_FOLDER_QUESTIONS = "questions/"
    GAME_FOLDER_HINTS = "hints/"
    GAME_FOLDER_WHO_KNOWS_MORE = "who-knows-more/"
    BUTTONS_PER_PAGE = 29


class Confetti:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-8, -4)
        self.size = random.randint(4, 8)
        self.color = random.choice([(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255)])
        self.life = 60  # frames

    def update(self):
        self.vy += 0.3  # gravity
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.rect(surface, self.color, (int(self.x), int(self.y), self.size, self.size))
