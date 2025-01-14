# -*- coding: utf-8 -*-

import os
from pathlib import Path

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
    GIT_DIRECTORY = os.path.dirname(__file__)
    ROOT = Path(os.path.dirname(GIT_DIRECTORY))
    ROOT_EXTENDED = Path(os.path.join(ROOT, "data/"))
    STATIC_FOLDER = Path(os.path.join(ROOT_EXTENDED, "staticfiles/"))
    GAME_FOLDER_IMAGES="images/"
    GAME_FOLDER_SOUNDS="sounds/"
    GAME_FOLDER_QUESTIONS="questions/"
    GAME_FOLDER_HINTS="hints/"
    GAME_FOLDER_WHO_KNOWS_MORE="who-knows-more/"
    BUTTONS_PER_PAGE = 29