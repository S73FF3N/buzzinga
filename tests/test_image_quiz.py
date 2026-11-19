import os

from buzzinga.game_utilities import count_round_files
from buzzinga.image_quiz import ImageQuiz

from conftest import write_image


def round_by_name(quiz, file_name):
    return next(rd for rd in quiz.round_data if os.path.basename(rd["data"]) == file_name)


def test_solution_files_are_matched_case_insensitively(tmp_path, make_quiz):
    write_image(tmp_path / "Eins.JPG")
    write_image(tmp_path / "Eins_solution.JPG")
    write_image(tmp_path / "Zwei.webp")
    write_image(tmp_path / "Drei.png")
    (tmp_path / "Drei_solution.mp4").write_bytes(b"")

    quiz = make_quiz(ImageQuiz, tmp_path)

    assert quiz.total_rounds == 3
    eins = round_by_name(quiz, "Eins.JPG")
    assert os.path.basename(eins["solution_file"]) == "Eins_solution.JPG"
    assert eins["solution_file_type"] == "image"
    drei = round_by_name(quiz, "Drei.png")
    assert drei["solution_file_type"] == "video"
    assert round_by_name(quiz, "Zwei.webp")["solution_file"] is None


def test_answer_is_derived_from_file_name_and_example_comes_first(tmp_path, make_quiz):
    for name in ["A.png", "B.png", "C.png", "Song_zzzLiveuuu_example.png"]:
        write_image(tmp_path / name)

    quiz = make_quiz(ImageQuiz, tmp_path)

    assert quiz.round_data[0]["example"]
    assert quiz.round_data[0]["solution"] == "Song (Live)"


def test_game_files_are_left_unchanged(tmp_path, make_quiz):
    for name in ["Eins.jpg", "Zwei.jpeg", "Drei.webp", "Drei_solution.bmp"]:
        write_image(tmp_path / name)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}

    quiz = make_quiz(ImageQuiz, tmp_path)
    for i in range(1, quiz.total_rounds + 1):
        quiz.current_round = i
        quiz.start_round()

    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before


def test_unloadable_round_is_shown_as_resolved(tmp_path, make_quiz):
    (tmp_path / "Kaputt.png").write_bytes(b"not an image")

    quiz = make_quiz(ImageQuiz, tmp_path)
    quiz.current_round = 1
    quiz.start_round()

    # Resolved state: buzzers are ignored and Enter moves on to the next round
    assert quiz.round_load_failed
    assert quiz.buzzer_hit and quiz.solution_shown


def test_category_menu_counts_the_rounds_the_quiz_plays(tmp_path, make_quiz):
    for name in ["A.JPG", "B.png", "B_solution.png", "F.jpeg", "G.Png"]:
        write_image(tmp_path / name)
    for name in ["C.gif", "D.tiff", "E.webm"]:
        (tmp_path / name).write_bytes(b"")

    quiz = make_quiz(ImageQuiz, tmp_path)

    assert count_round_files(tmp_path, ImageQuiz.image_exts + ImageQuiz.video_exts) == quiz.total_rounds == 5


def test_hidden_files_are_not_rounds(tmp_path, make_quiz):
    write_image(tmp_path / "A.png")
    # macOS writes these next to copied files on USB sticks
    (tmp_path / "._A.png").write_bytes(b"\x00\x05\x16\x07")
    (tmp_path / ".DS_Store").write_bytes(b"")

    quiz = make_quiz(ImageQuiz, tmp_path)

    assert quiz.total_rounds == 1
    assert count_round_files(tmp_path, ImageQuiz.image_exts) == 1
