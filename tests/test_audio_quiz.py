import os

from buzzinga.audio_quiz import AudioQuiz
from buzzinga.game_utilities import count_round_files

from conftest import write_image, write_wav


def test_mp3_and_wav_rounds_with_solution_sound_and_image(tmp_path, make_quiz):
    (tmp_path / "Lied.MP3").write_bytes(b"")
    write_wav(tmp_path / "Song.wav")
    write_wav(tmp_path / "Song_solution.wav")
    write_image(tmp_path / "Song_solution.png")

    quiz = make_quiz(AudioQuiz, tmp_path)

    assert quiz.total_rounds == 2
    assert count_round_files(tmp_path, AudioQuiz.sound_exts) == 2
    quiz.current_round = next(
        i for i, rd in enumerate(quiz.round_data, 1) if os.path.basename(rd["data"]) == "Song.wav"
    )
    quiz.play_round()

    assert quiz.current_solution_sound is not None
    # show_solution() in the base class displays current_solution_file
    assert os.path.basename(quiz.current_solution_file) == "Song_solution.png"
    assert quiz.current_solution_file_type == "image"


def test_solution_files_are_matched_case_insensitively(tmp_path, make_quiz):
    write_wav(tmp_path / "Song.wav")
    write_wav(tmp_path / "Song_solution.WAV")
    write_image(tmp_path / "Song_solution.JPG")

    quiz = make_quiz(AudioQuiz, tmp_path)

    assert quiz.total_rounds == 1
    assert os.path.basename(quiz.round_data[0]["solution_sound"]) == "Song_solution.WAV"
    assert os.path.basename(quiz.round_data[0]["solution_img"]) == "Song_solution.JPG"
