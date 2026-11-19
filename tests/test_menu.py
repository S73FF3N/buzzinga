import pygame
import pytest

from buzzinga import buzzinga_class
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


@pytest.mark.parametrize("all_rounds_mode, expected_max_score", [(True, 100), (False, 10)])
def test_points_setting_survives_an_all_rounds_game(buzzinga, monkeypatch, all_rounds_mode, expected_max_score):
    started = []

    class FakeQuiz:
        def __init__(self, clock, game_dir, players, is_game_sounds, max_score, *rest):
            started.append(max_score)

        def run(self):
            pass

    monkeypatch.setattr(buzzinga_class, "ImageQuiz", FakeQuiz)
    buzzinga.game_type = "images"
    buzzinga.points_to_win = 10
    buzzinga.game_modus = all_rounds_mode

    buzzinga.game()

    assert started == [expected_max_score]
    assert buzzinga.points_to_win == 10
