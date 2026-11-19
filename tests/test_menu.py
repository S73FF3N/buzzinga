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
