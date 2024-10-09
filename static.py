# -*- coding: utf-8 -*-

import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

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
    ROOT_EXTENDED = Path(os.getenv('ROOT_EXTENDED'))
    STATIC_FOLDER = Path(os.getenv('STATIC_FOLDER'))
    ROOT = Path(os.getenv('ROOT'))
    GAME_FOLDER_IMAGES = Path(os.getenv('GAME_FOLDER_IMAGES'))
    GAME_FOLDER_SOUNDS = Path(os.getenv('GAME_FOLDER_SOUNDS'))
    GAME_FOLDER_QUESTIONS = Path(os.getenv('GAME_FOLDER_QUESTIONS'))
    GAME_FOLDER_HINTS = Path(os.getenv('GAME_FOLDER_HINTS'))
    GAME_FOLDER_WHO_KNOWS_MORE = Path(os.getenv('GAME_FOLDER_WHO_KNOWS_MORE'))
    GIT_DIRECTORY = Path(os.getenv('GIT_DIRECTORY'))
    BUTTONS_PER_PAGE = 29