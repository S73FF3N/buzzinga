import pygame, os
from static import Static
from game_utilities import load_and_scale_image


class Animation(pygame.sprite.Sprite):

    def animate(self):
        self.is_animating = True

    def stop_animation(self):
        self.is_animating = False

    def update(self, speed):
        if self.is_animating == True:
            self.current_sprite += speed

            if self.current_sprite >= len(self.sprites):
                self.current_sprite = 0

            self.image = self.sprites[int(self.current_sprite)]
        else:
            self.image = self.sprites[0]


class BuzzingaAnimation(Animation):
    def __init__(self, rect, image_cache):
        super().__init__()
        self.is_animating = False
        self.sprites = []
        self.sprites.append(load_and_scale_image('Buzzinga-1.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.w / 2, image_cache))
        self.sprites.append(load_and_scale_image('Buzzinga-2.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.w / 2, image_cache))
        self.sprites.append(load_and_scale_image('Buzzinga-3.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.w / 2, image_cache))
        self.sprites.append(load_and_scale_image('Buzzinga-4.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.w / 2, image_cache))
        self.sprites.append(load_and_scale_image('Buzzinga-5.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.w / 2, image_cache))
        self.sprites.append(load_and_scale_image('Buzzinga-6.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.w / 2, image_cache))
        self.sprites.append(load_and_scale_image('Buzzinga-7.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.w / 2, image_cache))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.center = rect.center


class SoundAnimation(Animation):
    def __init__(self, rect, image_cache):
        super().__init__()
        self.is_animating = False
        self.sprites = []
        self.sprites.append(load_and_scale_image('sound_animation-1.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.h*0.7, image_cache))
        self.sprites.append(load_and_scale_image('sound_animation-2.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.h*0.7, image_cache))
        self.sprites.append(load_and_scale_image('sound_animation-3.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.h*0.7, image_cache))
        self.sprites.append(load_and_scale_image('sound_animation-4.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.h*0.7, image_cache))
        self.sprites.append(load_and_scale_image('sound_animation-5.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.h*0.7, image_cache))
        self.sprites.append(load_and_scale_image('sound_animation-6.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.h*0.7, image_cache))
        self.sprites.append(load_and_scale_image('sound_animation-7.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.h*0.7, image_cache))
        self.sprites.append(load_and_scale_image('sound_animation-8.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.h*0.7, image_cache))
        self.sprites.append(load_and_scale_image('sound_animation-9.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.h*0.7, image_cache))
        self.sprites.append(load_and_scale_image('sound_animation-10.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), rect.h*0.7, image_cache))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.center = rect.center
