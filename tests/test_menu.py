import pygame
import pytest

from buzzinga.buzzinga_class import Buzzinga
from buzzinga.translations import english


@pytest.fixture
def buzzinga():
    return Buzzinga()


def test_entered_player_names_are_kept_and_defaults_follow_the_language(buzzinga):
    buzzinga.player = ["Anna", "", "Spieler 3", "Player 4"]
    buzzinga.current_language = english

    buzzinga.fill_default_player_names()

    assert buzzinga.player == ["Anna", "Player 2", "Player 3", "Player 4"]


def test_start_screen_exits_when_the_window_is_closed(buzzinga, monkeypatch):
    # Keep the session's display alive for the other tests
    monkeypatch.setattr(pygame, "quit", lambda: None)
    pygame.event.clear()
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    # If QUIT were ignored, this key press leaves the start screen, so the
    # test fails instead of looping forever
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, unicode=" "))

    with pytest.raises(SystemExit):
        buzzinga.start_screen()
