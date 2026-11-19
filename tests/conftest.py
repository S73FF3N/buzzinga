import os

# Run pygame without a window or sound device (CI, headless machines)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import wave

import pygame
import pytest
from PIL import Image


@pytest.fixture(scope="session", autouse=True)
def pygame_display():
    pygame.init()
    pygame.display.set_mode((1280, 720))
    yield
    pygame.quit()


class FakeBuzzerSet:
    """Stands in for pybuzzers.BuzzerSet, which needs real Buzz! hardware."""

    def __init__(self):
        self.listener_threads = 0
        self.buzz_handlers = {}
        self.button_down_handlers = {}

    def on_buzz(self, handler, label=None):
        self.buzz_handlers[label or str(handler)] = handler

    def on_button_down(self, handler, label=None):
        self.button_down_handlers[label or str(handler)] = handler

    def clear_handlers(self):
        self.buzz_handlers = {}
        self.button_down_handlers = {}

    def start_listening(self):
        self.listener_threads += 1

    def press(self, buzzer):
        for handler in list(self.buzz_handlers.values()):
            handler(self, buzzer)


@pytest.fixture
def buzzer_set():
    return FakeBuzzerSet()


@pytest.fixture
def make_quiz(buzzer_set):
    def make(quiz_class, game_data):
        return quiz_class(pygame.time.Clock(), game_data, ["A", "B"], False, 100, buzzer_set, False)
    return make


def write_image(path, color=(0, 200, 0)):
    Image.new("RGB", (40, 30), color).save(path)


def write_wav(path, seconds=0.1):
    with wave.open(str(path), "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(44100)
        f.writeframes(b"\x00" * int(44100 * seconds) * 4)
