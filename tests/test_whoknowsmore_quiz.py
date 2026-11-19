import json
import time

import pygame

from buzzinga.whoknowsmore_quiz import WhoKnowsMoreQuiz

ENTRY = {"solution": "Planets", "answers": [{"count_id": 1, "answer": "Mars"}, {"count_id": 2, "answer": "Venus"}]}


def test_answer_key_ends_the_countdown_without_waiting_for_the_next_second(tmp_path, make_quiz):
    path = tmp_path / "Planeten.json"
    path.write_text(json.dumps([ENTRY]), encoding="utf-8")
    quiz = make_quiz(WhoKnowsMoreQuiz, str(path))

    # Keys returned by successive handle_events() calls in run(): outer loop,
    # start the round, first player's turn (starts the countdown), R during
    # the countdown. The call after R is the first one of the next step.
    script = [None, pygame.K_RETURN, pygame.K_RETURN, pygame.K_r]
    pressed_r_at = []
    next_step_after = []

    def scripted_events():
        if script:
            key = script.pop(0)
            if key == pygame.K_r:
                pressed_r_at.append(time.monotonic())
            return key, ""
        next_step_after.append(time.monotonic() - pressed_r_at[0])
        quiz.escape_pressed = True
        quiz.running = False
        return pygame.K_ESCAPE, ""

    quiz.handle_events = scripted_events
    quiz.run()

    assert quiz.correct_answer
    assert next_step_after[0] < 0.5
