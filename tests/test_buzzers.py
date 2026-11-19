from buzzinga.image_quiz import ImageQuiz

from conftest import write_image


def test_listener_starts_once_and_only_the_current_game_receives_buzzes(tmp_path, make_quiz, buzzer_set):
    write_image(tmp_path / "A.png")

    first = make_quiz(ImageQuiz, tmp_path)
    second = make_quiz(ImageQuiz, tmp_path)
    for quiz in (first, second):
        quiz.initializing = False
    buzzer_set.press(2)

    assert buzzer_set.listener_threads == 1
    assert len(buzzer_set.buzz_handlers) == 1
    assert first.buzzering_player is None
    assert second.buzzering_player == 3
