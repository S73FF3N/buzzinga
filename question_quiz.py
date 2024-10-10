import os, pygame, json, random

from quiz_games import QuizGameBase
from static import Static
from game_utilities import optimize_text_in_container
from animation import BuzzingaAnimation


class QuestionQuiz(QuizGameBase):
    def __init__(self, clock, game_data, players, is_game_sounds, max_score, language):
        super().__init__(clock, game_data, players, is_game_sounds, max_score, language)
        self.player1_answer_keys = [1, 2, 3, 4]
        self.player2_answer_keys = [6, 7, 8, 9]
        self.player3_answer_keys = [11, 12, 13, 14]
        self.player4_answer_keys = [16, 17, 18, 19]

        self.current_question = None
        self.player_answers = {1: False, 2: False, 3: False, 4: False}
        self.player1_locked = False
        self.player2_locked = False
        self.player3_locked = False
        self.player4_locked = False
        self.question_answered = False
        self.answers_shown = False
        self.solution_dict = {}

        self.question_container_width = self.left_container_width
        self.question_container_height = self.SCREEN_HEIGHT * 0.3
        self.option_container_width = (self.left_container_width / 2) - 20
        self.option_container_height = (self.SCREEN_HEIGHT * 0.25) - 20
        self.question_container = pygame.Rect(0, self.top_container_height, self.question_container_width,
                                     self.question_container_height)
        self.option1_container = pygame.Rect(10, self.top_container_height + self.question_container_height, self.option_container_width,
                                    self.option_container_height)
        self.option2_container = pygame.Rect(30 + self.option_container_width,
                                    self.top_container_height + self.question_container_height, self.option_container_width,
                                    self.option_container_height)
        self.option3_container = pygame.Rect(10,
                                    self.top_container_height + self.question_container_height + self.option_container_height + 20,
                                    self.option_container_width,
                                    self.option_container_height)
        self.option4_container = pygame.Rect(30 + self.option_container_width,
                                    self.top_container_height + self.question_container_height + self.option_container_height + 20,
                                    self.option_container_width,
                                    self.option_container_height)

    def load_round_data(self):
        with open(self.game_data, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        for q in data:
            self.round_data.append({'question': q["fields"]["quiz_question"],
                             'solution': q["fields"]["solution"],
                             'option1': q["fields"]["option1"],
                             'option2': q["fields"]["option2"],
                             'option3': q["fields"]["option3"]})
        self.total_rounds = len(data)
        random.shuffle(self.round_data)

    def play_round(self):
        self.player_answers = {1: False, 2: False, 3: False, 4: False}
        self.player1_locked = self.player2_locked = self.player3_locked = self.player4_locked = False
        current_data = self.round_data[self.current_round - 1]
        self.current_question = current_data["question"]
        self.current_solution = current_data["solution"]
        pygame.draw.rect(self.screen, Static.WHITE, self.main_container)
        optimize_text_in_container(self.screen, self.question_container, self.current_question, color=Static.RED)
        options = [current_data["option1"], current_data["option2"], current_data["option3"], current_data["solution"]]
        random.shuffle(options)
        colors = [Static.BLUE, Static.ORANGE, Static.GREEN, Static.YELLOW]
        containers = [self.option1_container, self.option2_container, self.option3_container, self.option4_container]
        for i, (color, container) in enumerate(zip(colors, containers), start=1):
            self.draw_rect(color, Static.RED, 10, container)
            optimize_text_in_container(self.screen, container, options[0])
            self.solution_dict[5-i] = [options[0], color]
            del options[0]

    def show_solution(self):
        if self.solution_dict[4][0] == self.current_solution:
            pygame.draw.rect(self.screen, Static.LIGHT_GREEN, self.option1_container, 50)
            pygame.draw.rect(self.screen, Static.RED, self.option1_container, 10)
            optimize_text_in_container(self.screen, self.option1_container, self.current_solution)
        elif self.solution_dict[3][0] == self.current_solution:
            pygame.draw.rect(self.screen, Static.LIGHT_GREEN, self.option2_container, 50)
            pygame.draw.rect(self.screen, Static.RED, self.option2_container, 10)
            optimize_text_in_container(self.screen, self.option2_container, self.current_solution)
        elif self.solution_dict[2][0] == self.current_solution:
            pygame.draw.rect(self.screen, Static.LIGHT_GREEN, self.option3_container, 50)
            pygame.draw.rect(self.screen, Static.RED, self.option3_container, 10)
            optimize_text_in_container(self.screen, self.option3_container, self.current_solution)
        elif self.solution_dict[1][0] == self.current_solution:
            pygame.draw.rect(self.screen, Static.LIGHT_GREEN, self.option4_container, 50)
            pygame.draw.rect(self.screen, Static.RED, self.option4_container, 10)
            optimize_text_in_container(self.screen, self.option4_container, self.current_solution)

    def run(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        self.screen.fill(Static.WHITE)
        pygame.display.set_caption(self.game_name)
        moving_sprites = pygame.sprite.Group()
        animation = BuzzingaAnimation(self.main_container, self.image_cache)
        moving_sprites.add(animation)

        self.display_game_info()

        while self.running:
            key, button = self.handle_events()
            if self.escape_pressed:
                break

            while self.initializing:
                key, button = self.handle_events()
                if self.escape_pressed:
                    break
                if key == pygame.K_RETURN:
                    try:
                        self.animation_stopped = True
                        self.current_round += 1
                        self.update_progress()
                        self.play_round()
                        pygame.display.flip()
                    except Exception as e:
                        os.chdir(Static.GIT_DIRECTORY)
                        self.running = False
                    self.initializing = False
                if not self.animation_stopped:
                    self.draw_rect(Static.BLUE, Static.WHITE, 8, self.main_container)
                    moving_sprites.draw(self.screen)
                    moving_sprites.update(0.25)
                    animation.animate()
                    pygame.display.flip()
                    self.clock.tick(60)

            while not self.question_answered and not self.winner_found:
                key, button = self.handle_events()
                if self.escape_pressed:
                    break
                if key == pygame.K_RETURN:
                    if not self.player1_locked and not self.player2_locked and not self.player3_locked and not self.player4_locked:
                        self.question_answered = True
                        self.answers_shown = True
                        for n in range(1, self.amount_players + 1):
                            self.display_buzzer(n-1, Static.GREY)
                    else:
                        for n in range(1, self.amount_players + 1):
                            color = Static.RED if self.player_answers[n] else Static.GREY
                            self.display_buzzer(n-1, color)
                        pygame.display.flip()
                        self.question_answered = True

                if button in self.player1_answer_keys and not self.player1_locked:
                    self.player1_locked = True
                    self.player_answers[1] = self.solution_dict[self.player1_answer_keys.index(button)+1]
                    self.display_buzzer(0, Static.RED)
                elif button in self.player2_answer_keys and not self.player2_locked:
                    self.player2_locked = True
                    self.player_answers[2] = self.solution_dict[self.player2_answer_keys.index(button)+1]
                    self.display_buzzer(1, Static.RED)
                elif button in self.player3_answer_keys and not self.player3_locked:
                    self.player3_locked = True
                    self.player_answers[3] = self.solution_dict[self.player3_answer_keys.index(button)+1]
                    self.display_buzzer(2, Static.RED)
                elif button in self.player4_answer_keys and not self.player4_locked:
                    self.player4_locked = True
                    self.player_answers[4] = self.solution_dict[self.player4_answer_keys.index(button)+1]
                    self.display_buzzer(3, Static.RED)
                if self.player1_locked and self.player2_locked and self.player3_locked and self.player4_locked:
                    self.question_answered = True
                pygame.display.flip()

            while self.question_answered and not self.winner_found:
                key, button = self.handle_events()
                if self.escape_pressed:
                    break

                while not self.answers_shown:
                    key, button = self.handle_events()
                    if self.escape_pressed:
                        break

                    if key == pygame.K_RETURN:
                        for n in range(1, self.amount_players + 1):
                            color = self.player_answers[n][1] if self.player_answers[n] else Static.GREY
                            self.display_buzzer(n-1, color)
                        self.answers_shown = True
                        pygame.display.flip()

                while self.answers_shown and not self.solution_shown:
                    key, button = self.handle_events()
                    if self.escape_pressed:
                        break

                    if key == pygame.K_RETURN:
                        # solution is shown
                        self.show_solution()

                        for n in range(1, self.amount_players + 1):
                            color = Static.LIGHT_GREEN if self.player_answers[n] and self.player_answers[n][0] == self.current_solution else Static.RED
                            self.display_buzzer(n-1, color, width=15)
                            if self.player_answers[n] and self.player_answers[n][0] == self.current_solution:
                                self.scores[n-1] += 1
                                self.update_score(n-1)
                        self.solution_shown = True
                        pygame.display.flip()

                while self.answers_shown and self.solution_shown:
                        key, button = self.handle_events()
                        if self.escape_pressed:
                            break
                        if key == pygame.K_RETURN:
                            for n in range(1, self.amount_players + 1):
                                self.display_buzzer(n-1, Static.LIGHT_BLUE)
                            self.check_game_over()
                            self.answers_shown = False
                            self.solution_shown = False
                            self.question_answered = False
                            if not self.winner_found:
                                self.current_round += 1
                                self.display_game_info()
                                self.update_progress()
                                self.play_round()
                            else:
                                self.show_winner()
                            pygame.display.flip()    