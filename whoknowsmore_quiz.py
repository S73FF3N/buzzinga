import os, random, pygame, json, sys, traceback

from quiz_games import QuizGameBase
from static import Static
from game_utilities import blit_text_objects, optimize_text_in_container
from animation import BuzzingaAnimation


class WhoKnowsMoreQuiz(QuizGameBase):
    def __init__(self, clock, game_data, players, is_game_sounds, max_score, language, buzzer_set):
        super().__init__(clock, game_data, players, is_game_sounds, max_score, language, buzzer_set)
        self.answer_category = 1
        self.first_element_of_question = True
        self.active_player = 0
        self.countdown = False
        self.countdown_seconds_left = 30
        self.countdown_ended = False
        self.correct_answer = False
        self.incorrect_answer = False
        self.answer_id = ""
        self.answers_solved = []
        self.skip_print_answer = False
        self.number_keys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]
        self.active_players = [True] * self.amount_players
        self.solution_shown = True

    def load_round_data(self):
        with open(self.game_data, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        data_counter = 0
        for q in data:
            solution_link = "5/" + str(q["id"])
            self.round_data.append({
                'answer_category': q["solution"],
                'solution_link': solution_link,
                'answers': {}
                })
            for a in q["answers"]:
                self.round_data[data_counter]["answers"][a["count_id"]] = a["answer"]
            data_counter += 1
        self.total_rounds = len(data)
        random.shuffle(self.round_data)

    def play_round(self):
        self.active_players = [True] * self.amount_players
        self.first_element_of_question = True
        self.countdown_ended = False
        self.countdown_seconds_left = 30
        self.answers_solved = []
        current_data = self.round_data[self.current_round - 1]
        pygame.draw.rect(self.screen, Static.WHITE, self.main_container)
        self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_left_container)

        answer_font = self.get_answer_text(current_data['answer_category'], False, self.bottom_left_container)
        blit_text_objects(self.screen, self.bottom_left_container, current_data['answer_category'], answer_font)
        blit_text_objects(self.screen, self.bottom_right_container, current_data['solution_link'], self.SMALL_TEXT)

    def handle_events(self):
        key_status = pygame.key.get_pressed()
        key_pressed = None
        letter_pressed = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            alt_f4 = (event.type == pygame.KEYDOWN and (event.key == pygame.K_F4 and (key_status[pygame.K_LALT] or key_status[pygame.K_RALT])))
            if alt_f4:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                key_pressed = event.key
                letter_pressed = event.unicode
                if key_pressed == pygame.K_ESCAPE:
                    self.escape_pressed = True
                    os.chdir(Static.GIT_DIRECTORY)
        return key_pressed, letter_pressed
            
    def get_answer_text(self, answer_text, is_large_grid, container=None):
        if container:
            x, y, container_width, container_height = container.x, container.y, container.w, container.h
        else:
            x, y, container_width, container_height = self.get_answer_position(1, is_large_grid)
        
        min_font_size = 10
        max_font_size = 70
        optimal_font_size = min_font_size
        
        while min_font_size <= max_font_size:
            current_font_size = (min_font_size + max_font_size) // 2
            font = pygame.font.Font(None, current_font_size)
            text_surface = font.render(answer_text, True, Static.WHITE)
            
            if text_surface.get_width() <= (container_width-16) and text_surface.get_height() <= (container_height-6):
                optimal_font_size = current_font_size
                min_font_size = current_font_size + 1
            else:
                max_font_size = current_font_size - 1
        
        optimal_font = pygame.font.Font(None, optimal_font_size)
        return optimal_font

    def get_answer_position(self, answer_id, is_large_grid):
        if is_large_grid:
            container_width = ((self.left_container_width-16) / 6) - 5
            container_height = ((self.main_container_height-16) / 10) - 2
            x = ((answer_id - 1) % 6) * (container_width + 5) + 8
            y = ((answer_id - 1) // 6) * (container_height + 2) + self.top_container_height
        else:
            container_width = ((self.left_container_width-16) / 4) - 5
            container_height = ((self.main_container_height-16) / 7) - 2
            x = ((answer_id - 1) % 4) * (container_width + 5) + 8
            y = ((answer_id - 1) // 4) * (container_height + 2) + self.top_container_height
        return x, y, container_width, container_height
    
    def find_active_player(self):
        while True:
            self.active_player = (self.active_player + 1) % self.amount_players
            if self.active_players[self.active_player]:
                break

    def blit_answer(self, answers, answer_id_int):
        answer_text = answers[answer_id_int]
        self.answers_solved.append(answer_text)
        is_large_grid = len(answers) > 28
        x, y, width, height = self.get_answer_position(answer_id_int, is_large_grid)
        answer_container = pygame.Rect(x, y, width, height)
        self.draw_rect(Static.BLUE, Static.LIGHT_BLUE, 8, answer_container)
        optimize_text_in_container(self.screen, answer_container, answer_text)
        pygame.display.flip()

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
            key, letter = self.handle_events()
            if self.escape_pressed:
                break

            while self.initializing:
                key, letter = self.handle_events()
                if self.escape_pressed:
                    break

                if self.winner_found:
                    if key == pygame.K_RETURN:
                        self.show_winner()
                        pygame.display.flip()

                else:
                    for n in range(0, self.amount_players):
                        self.display_buzzer(n, Static.LIGHT_BLUE)

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

            while self.first_element_of_question and not self.winner_found:
                key, letter = self.handle_events()
                if self.escape_pressed:
                    break
                # noone buzzers
                if key == pygame.K_RETURN:
                    self.first_element_of_question = False
                    self.display_buzzer(self.active_player, Static.RED)
                    pygame.display.flip()
                    self.countdown = True

            while self.countdown and not self.winner_found:
                key, letter = self.handle_events()
                if self.escape_pressed:
                    break
                
                # answer is correct:
                if key == pygame.K_r:
                    self.countdown = False
                    self.correct_answer = True
                # answer is incorrect:
                if key == pygame.K_f:
                    self.countdown = False
                    self.incorrect_answer = True

                if not self.countdown_ended:
                    self.countdown_seconds_left -= 1
                time_left = str(self.countdown_seconds_left)
                self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_right_container)
                blit_text_objects(self.screen, self.bottom_right_container, time_left, self.SMALL_TEXT)
                pygame.display.flip()
                pygame.time.wait(1000)
                self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_right_container)
                pygame.display.flip()
                if self.countdown_seconds_left == 0:
                    if self.is_game_sounds and not self.countdown_ended:
                        countdown_sound = pygame.mixer.Sound(os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER, 'countdown_end.wav'))
                        self.game_sound_channel.play(countdown_sound)
                    self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_right_container)
                    pygame.display.flip()
                    self.countdown_ended = True
                

            while self.correct_answer and not self.winner_found:
                key, letter = self.handle_events()
                if self.escape_pressed:
                    break
                
                current_round_data = self.round_data[self.current_round - 1]

                if key == pygame.K_BACKSPACE and self.answer_id:
                    self.answer_id = self.answer_id[:-1]
                    self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_right_container)
                    blit_text_objects(self.screen, self.bottom_right_container, self.answer_id, self.SMALL_TEXT)
                    pygame.display.flip()
                
                if key in self.number_keys:
                    # let game master provide id of given answer from pool of answers
                    self.answer_id += letter
                    self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_right_container)
                    blit_text_objects(self.screen, self.bottom_right_container, self.answer_id, self.SMALL_TEXT)
                    pygame.display.flip()

                if key == pygame.K_RETURN and self.answer_id:
                    try:
                        # print answer on screen
                        answer_id_int = int(self.answer_id)
                        if current_round_data["answers"][answer_id_int] in self.answers_solved:
                            self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_right_container)
                            blit_text_objects(self.screen, self.bottom_right_container, self.language['already_solved'], self.MINI_TEXT)
                            pygame.display.flip()
                            self.skip_print_answer = True
                        if not self.skip_print_answer:
                            self.blit_answer(current_round_data["answers"], answer_id_int)
                            # if answers left:
                            if len(current_round_data["answers"]) != len(self.answers_solved):
                                #   mark player to give next answer
                                self.find_active_player()
                                for n in range(0, self.amount_players):
                                    self.display_buzzer(n, Static.LIGHT_BLUE)
                                    if not self.active_players[n]:
                                        self.display_buzzer(n, Static.GREY)
                                self.display_buzzer(self.active_player, Static.RED)
                                pygame.display.flip()
                                self.correct_answer = False
                                self.countdown = True
                            # no answers left
                            else:
                                self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_right_container)
                                blit_text_objects(self.screen, self.bottom_right_container, self.language['all_solved'], self.MINI_TEXT)
                                pygame.display.flip()
                                self.correct_answer = False
                                self.initializing = True
                                self.first_element_of_question = True
                                self.answers_solved = []
                        self.countdown_seconds_left = 30   
                        self.answer_id = ""
                        self.skip_print_answer = False
                    except Exception as e:
                        print(e, traceback.print_exc())
                        self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_right_container)
                        blit_text_objects(self.screen, self.bottom_right_container, self.language['wrong_id'], self.SMALL_TEXT)
                        pygame.display.flip()
                        self.answer_id = ""

                self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_right_container)

            while self.incorrect_answer and not self.winner_found:
                key, letter = self.handle_events()
                if self.escape_pressed:
                    break

                self.incorrect_answer = False
                self.active_players[self.active_player] = False
                current_round_data = self.round_data[self.current_round - 1]
                self.find_active_player()

                for n in range(0, self.amount_players):
                    self.display_buzzer(n, Static.LIGHT_BLUE)
                    if not self.active_players[n]:
                        self.display_buzzer(n, Static.GREY)
                self.display_buzzer(self.active_player, Static.RED)
                pygame.display.flip()

                if sum(self.active_players) == 1:
                    #   set variable to start next round
                    self.initializing = True
                    #   print all answers left
                    for a in current_round_data["answers"].keys():
                        self.blit_answer(current_round_data["answers"], a)

                    #   assign point to winning player
                    self.scores[self.active_player] += 1
                    self.update_score(self.active_player)
                    self.check_game_over()
                    if not self.winner_found:
                        self.answer_category += 1
                else:
                    # start countdown
                    self.countdown_seconds_left = 30
                    self.countdown = True