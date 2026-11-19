import json

import pytest

from buzzinga.buzzinga_class import Buzzinga
from buzzinga.hint_quiz import HintQuiz
from buzzinga.question_quiz import QuestionQuiz
from buzzinga.sort_quiz import SortQuiz
from buzzinga.whoknowsmore_quiz import WhoKnowsMoreQuiz

HINT = {"fields": {"solution": "Justin Bieber", **{f"hint{n}": f"Hint {n}" for n in range(1, 11)}}}
QUESTION = {"pk": 1, "fields": {"quiz_question": "Q?", "solution": "A", "option1": "B", "option2": "C", "option3": "D"}}
WHO_KNOWS_MORE = {"id": 1, "solution": "Planets", "answers": [{"count_id": 1, "answer": "Mars"}]}
SORT = {"criterion": "Population", "reference": {"name": "CH", "value": 8.9}, "elements": [{"name": "DE", "value": 83}]}


def without(entry, *path):
    """Copy of `entry` with the key at `path` removed."""
    entry = json.loads(json.dumps(entry))
    target = entry
    for key in path[:-1]:
        target = target[key]
    del target[path[-1]]
    return entry


@pytest.mark.parametrize("quiz_class, valid, incomplete", [
    (HintQuiz, HINT, without(HINT, "fields", "hint7")),
    (QuestionQuiz, QUESTION, without(QUESTION, "fields", "option2")),
    (WhoKnowsMoreQuiz, WHO_KNOWS_MORE, without(WHO_KNOWS_MORE, "answers")),
    (SortQuiz, SORT, without(SORT, "reference", "value")),
])
def test_incomplete_entries_are_skipped(quiz_class, valid, incomplete):
    assert len(quiz_class.parse_rounds([valid, incomplete, valid], warn=False)) == 2


def test_optional_ids_may_be_missing():
    # The README's hints example has no "pk"
    assert HintQuiz.parse_rounds([HINT], warn=False)[0]["solution_link"] == ""
    assert len(QuestionQuiz.parse_rounds([without(QUESTION, "pk")], warn=False)) == 1


def test_game_plays_only_the_complete_entries(tmp_path, make_quiz):
    path = tmp_path / "Hinweise.json"
    path.write_text(json.dumps([HINT, without(HINT, "fields", "solution")]), encoding="utf-8")

    assert make_quiz(HintQuiz, str(path)).total_rounds == 1


@pytest.fixture
def hints_menu(tmp_path):
    buzzinga = Buzzinga()
    buzzinga.game_type = "hints"
    buzzinga.game_folder = tmp_path
    return buzzinga


@pytest.mark.parametrize("content", ['[{"fields": {"solution": "X",}]', '{"fields": {}}'])
def test_menu_marks_unreadable_files_instead_of_crashing(hints_menu, tmp_path, content):
    (tmp_path / "Kaputt.json").write_text(content, encoding="utf-8")

    assert hints_menu.get_amount_rounds("Kaputt.json") is None
    # Clicking the category stays on the menu
    assert hints_menu.handle_category_selection(True, [["Kaputt", True, 0, 0, 100, 40, None]]) is None


def test_menu_counts_only_complete_entries(hints_menu, tmp_path):
    (tmp_path / "Hinweise.json").write_text(json.dumps([HINT, without(HINT, "fields", "hint1")]), encoding="utf-8")

    assert hints_menu.get_amount_rounds("Hinweise.json") == 1
