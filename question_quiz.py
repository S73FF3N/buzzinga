import os, pygame, json, random, pybuzzers

from quiz_games import QuizGameBase
from static import Static
from game_utilities import optimize_text_in_container
from animation import BuzzingaAnimation


class QuestionQuiz(QuizGameBase):
    def __init__(self, clock, game_data, players, is_game_sounds, max_score, buzzer_set, image_reveal_animation):
        super().__init__(clock, game_data, players, is_game_sounds, max_score, buzzer_set, image_reveal_animation)

        self.current_question = None
        self.player_answers = {1: False, 2: False, 3: False, 4: False}
        self.player1_locked = False
        self.player2_locked = False
        self.player3_locked = False
        self.player4_locked = False
        self.question_answered = False
        self.answers_shown = False
        self.solution_dict = {}
        self.num_options = 4
        self.option_containers = []

        self.question_container_width = self.left_container_width
        self.question_container_height = self.SCREEN_HEIGHT * 0.3
        self.option_container_width = (self.left_container_width / 2) - 20
        self.option_container_height = (self.SCREEN_HEIGHT * 0.25) - 20
        self.question_container = pygame.Rect(0, self.top_container_height, self.question_container_width,
                                     self.question_container_height)
        
        self.buzzer_set = buzzer_set
        self.buzzering_player = None
        self.answer = None
        def handle_answer(buzzer_set: pybuzzers.BuzzerSet, buzzer: int, button: int):
            if not self.question_answered and not self.initializing and button != 0 and button <= self.num_options:
                self.buzzering_player = buzzer + 1
                self.answer = button
        
        self.buzzer_set.on_button_down(handle_answer)
        self.buzzer_set.start_listening()

    def load_round_data(self):
        with open(self.game_data, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        for q in data:
            fields = q["fields"]
            num_options = fields.get("num_options", 4)
            options = [fields["solution"]]
            for i in range(1, num_options):
                options.append(fields[f"option{i}"])
            self.round_data.append({'question': fields["quiz_question"],
                             'solution': fields["solution"],
                             'options': options,
                             'num_options': num_options})
        self.total_rounds = len(data)
        random.shuffle(self.round_data)

    def _build_option_containers(self, num_options):
        top = self.top_container_height + self.question_container_height
        if num_options == 4:
            w = self.option_container_width
            h = self.option_container_height
            return [
                pygame.Rect(10, top, w, h),
                pygame.Rect(30 + w, top, w, h),
                pygame.Rect(10, top + h + 20, w, h),
                pygame.Rect(30 + w, top + h + 20, w, h),
            ]
        elif num_options == 3:
            w = (self.left_container_width - 40) / 3
            h = self.option_container_height
            return [
                pygame.Rect(10, top, w, h),
                pygame.Rect(20 + w, top, w, h),
                pygame.Rect(30 + 2 * w, top, w, h),
            ]
        else:  # 2 options
            w = self.option_container_width
            h = self.option_container_height
            return [
                pygame.Rect(10, top, w, h),
                pygame.Rect(30 + w, top, w, h),
            ]

    def play_round(self):
        self.player_answers = {1: False, 2: False, 3: False, 4: False}
        self.player1_locked = self.player2_locked = self.player3_locked = self.player4_locked = False
        current_data = self.round_data[self.current_round - 1]
        self.current_question = current_data["question"]
        self.current_solution = current_data["solution"]
        self.num_options = current_data["num_options"]
        self.option_containers = self._build_option_containers(self.num_options)
        self.solution_dict = {}
        pygame.draw.rect(self.screen, Static.WHITE, self.main_container)
        optimize_text_in_container(self.screen, self.question_container, self.current_question, color=Static.RED)
        options = list(current_data["options"])
        random.shuffle(options)
        colors = [Static.BLUE, Static.ORANGE, Static.GREEN, Static.YELLOW]
        for i, container in enumerate(self.option_containers):
            color = colors[i]
            self.draw_rect(color, Static.RED, 10, container)
            optimize_text_in_container(self.screen, container, options[i])
            self.solution_dict[i + 1] = [options[i], color]

    def show_solution(self):
        for button_num, (option_text, color) in self.solution_dict.items():
            if option_text == self.current_solution:
                container = self.option_containers[button_num - 1]
                pygame.draw.rect(self.screen, Static.LIGHT_GREEN, container, 50)
                pygame.draw.rect(self.screen, Static.RED, container, 10)
                optimize_text_in_container(self.screen, container, self.current_solution)
                break

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
            key = self.handle_events()
            if self.escape_pressed:
                break

            while self.initializing:
                key = self.handle_events()
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
                        os.chdir(Static.BASE_PATH)
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
                key = self.handle_events()
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

                if self.buzzering_player == 1 and not self.player1_locked:
                    self.player1_locked = True
                    self.player_answers[1] = self.solution_dict[self.answer]
                    self.buzzering_player = None
                    self.answer = None
                    self.display_buzzer(0, Static.RED)
                elif self.buzzering_player == 2 and not self.player2_locked:
                    self.player2_locked = True
                    self.player_answers[2] = self.solution_dict[self.answer]
                    self.buzzering_player = None
                    self.answer = None
                    self.display_buzzer(1, Static.RED)
                elif self.buzzering_player == 3 and not self.player3_locked:
                    self.player3_locked = True
                    self.player_answers[3] = self.solution_dict[self.answer]
                    self.buzzering_player = None
                    self.answer = None
                    self.display_buzzer(2, Static.RED)
                elif self.buzzering_player == 4 and not self.player4_locked:
                    self.player4_locked = True
                    self.player_answers[4] = self.solution_dict[self.answer]
                    self.buzzering_player = None
                    self.answer = None
                    self.display_buzzer(3, Static.RED)
                if self.player1_locked and self.player2_locked and self.player3_locked and self.player4_locked:
                    self.question_answered = True
                pygame.display.flip()

            while self.question_answered and not self.winner_found:
                key = self.handle_events()
                if self.escape_pressed:
                    break

                while not self.answers_shown:
                    key = self.handle_events()
                    if self.escape_pressed:
                        break

                    if key == pygame.K_RETURN:
                        for n in range(1, self.amount_players + 1):
                            color = self.player_answers[n][1] if self.player_answers[n] else Static.GREY
                            self.display_buzzer(n-1, color)
                        self.answers_shown = True
                        pygame.display.flip()

                while self.answers_shown and not self.solution_shown:
                    key = self.handle_events()
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
                    key = self.handle_events()
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

            # Update and draw particles
            for p in self.particles[:]:
                p.update()
                p.draw(self.screen)
                if p.life <= 0:
                    self.particles.remove(p)
                pygame.display.flip()            
            self.clock.tick(60) 