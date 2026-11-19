import json

import pygame
import pytest

from buzzinga.buzzinga_class import Buzzinga
from buzzinga.image_quiz import ImageQuiz
from buzzinga.sort_quiz import SortQuiz
from buzzinga.translations import english, german

from conftest import write_image


def test_both_languages_define_the_same_texts():
    assert english.keys() == german.keys()


def test_game_screens_use_the_language_chosen_in_the_menu(tmp_path, buzzer_set):
    write_image(tmp_path / "A.png")

    quiz = ImageQuiz(pygame.time.Clock(), tmp_path, ["A"], False, 100, buzzer_set, False, english)

    assert quiz.language is english


def test_sort_banners_default_to_the_game_language(tmp_path, buzzer_set):
    entry = {"criterion": "Population", "reference": {"name": "CH", "value": 8.9},
             "elements": [{"name": "DE", "value": 83}]}
    path = tmp_path / "Sort.json"
    path.write_text(json.dumps([entry, dict(entry, descending=False, top_label="older")]), encoding="utf-8")

    quiz = SortQuiz(pygame.time.Clock(), str(path), ["A"], False, 100, buzzer_set, False, english)
    rounds = sorted(quiz.round_data, key=lambda r: r['descending'])

    assert quiz.direction_labels(rounds[1]) == ("more", "fewer")
    # Labels from the file win; the missing one gets the default
    assert quiz.direction_labels(rounds[0]) == ("older", "more")


@pytest.mark.parametrize("language", [english, german])
@pytest.mark.parametrize("game_type", ["images", "sounds", "questions", "hints", "who-knows-more", "sort"])
def test_settings_menu_has_all_texts(language, game_type):
    buzzinga = Buzzinga()
    buzzinga.current_language = language
    buzzinga.game_type = game_type

    buzzinga.settings_menu_setup()
    buzzinga.build_key_instructions()
