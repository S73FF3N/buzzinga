import os, random, pygame, json

from quiz_games import QuizGameBase
from static import Static
from game_utilities import blit_text_objects
from animation import BuzzingaAnimation


class HintQuiz(QuizGameBase):
    def __init__(self, SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT, clock, game_data, players, is_game_sounds, max_score):
        super().__init__(SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT, clock, game_data, players, is_game_sounds, max_score)
        self.hint_container_width = (self.main_container_width / 2) - 10
        self.hint_container_height = (self.main_container_height / 5) - 5
        self.hint1_container = pygame.Rect(5, self.top_left_container_height, self.hint_container_width, self.hint_container_height)
        self.hint2_container = pygame.Rect(self.hint_container_width + 10, self.top_left_container_height, self.hint_container_width, self.hint_container_height)
        self.hint3_container = pygame.Rect(5, self.top_left_container_height + self.hint_container_height + 5, self.hint_container_width, self.hint_container_height)
        self.hint4_container = pygame.Rect(self.hint_container_width + 10, self.top_left_container_height + self.hint_container_height + 5, self.hint_container_width,
                                    self.hint_container_height)
        self.hint5_container = pygame.Rect(5, self.top_left_container_height + 2*self.hint_container_height + 10, self.hint_container_width,
                                    self.hint_container_height)
        self.hint6_container = pygame.Rect(self.hint_container_width + 10, self.top_left_container_height + 2*self.hint_container_height + 10,
                                    self.hint_container_width,
                                    self.hint_container_height)
        self.hint7_container = pygame.Rect(5, self.top_left_container_height + 3*self.hint_container_height + 15, self.hint_container_width,
                                    self.hint_container_height)
        self.hint8_container = pygame.Rect(self.hint_container_width + 10, self.top_left_container_height + 3*self.hint_container_height + 15,
                                    self.hint_container_width,
                                    self.hint_container_height)
        self.hint9_container = pygame.Rect(5, self.top_left_container_height + 4*self.hint_container_height + 20, self.hint_container_width,
                                    self.hint_container_height)
        self.hint10_container = pygame.Rect(self.hint_container_width + 10, self.top_left_container_height + 4*self.hint_container_height + 20,
                                    self.hint_container_width,
                                    self.hint_container_height)
        
        self.hint_nr = 1
        self.hint_match_dict = {
            1: [self.hint1_container, "hint1"],
            2: [self.hint2_container, "hint2"],
            3: [self.hint3_container, "hint3"],
            4: [self.hint4_container, "hint4"],
            5: [self.hint5_container, "hint5"],
            6: [self.hint6_container, "hint6"],
            7: [self.hint7_container, "hint7"],
            8: [self.hint8_container, "hint8"],
            9: [self.hint9_container, "hint9"],
            10: [self.hint10_container, "hint10"],
        }
        self.no_points_awarded = False
        self.correct_answer = False

    def print_hint(self, screen, n):
        pygame.draw.rect(screen, Static.BLUE, self.hint_match_dict[n][0])
        pygame.draw.rect(screen, Static.LIGHT_BLUE, self.hint_match_dict[n][0], width=8)
        if len(self.round_data[self.current_round-1][self.hint_match_dict[n][1]]) < 22:
            hint1 = self.SMALL_TEXT.render(self.round_data[self.current_round-1][self.hint_match_dict[n][1]], 1, Static.WHITE)
        else:
            hint1 = self.MINI_TEXT.render(self.round_data[self.current_round-1][self.hint_match_dict[n][1]], 1, Static.WHITE)
        screen.blit(hint1, hint1.get_rect(center=self.hint_match_dict[n][0].center))
        pygame.display.flip()

    def load_round_data(self):
        with open(self.game_data, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        for q in data:
            solution_link = "4/" + str(q["pk"])
            self.round_data.append({
                'solution': q["fields"]["solution"],
                'hint1': q["fields"]["hint1"],
                'hint2': q["fields"]["hint2"],
                'hint3': q["fields"]["hint3"],
                'hint4': q["fields"]["hint4"],
                'hint5': q["fields"]["hint5"],
                'hint6': q["fields"]["hint6"],
                'hint7': q["fields"]["hint7"],
                'hint8': q["fields"]["hint8"],
                'hint9': q["fields"]["hint9"],
                'hint10': q["fields"]["hint10"],
                'solution_link': solution_link,
                })
        self.total_rounds = len(data)
        random.shuffle(self.round_data)

    def play_round(self, screen):
        self.hint_nr = 1
        self.correct_answer = False
        current_data = self.round_data[self.current_round - 1]
        self.current_solution = current_data["solution"]
        pygame.draw.rect(screen, Static.WHITE, self.main_container)

    def run(self, screen):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        screen.fill(Static.WHITE)
        pygame.display.set_caption(self.game_name)
        moving_sprites = pygame.sprite.Group()
        animation = BuzzingaAnimation(self.main_container, self.image_cache)
        moving_sprites.add(animation)

        self.display_game_info(screen)

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
                        self.update_progress(screen)
                        self.play_round(screen)
                        pygame.display.flip()
                    except Exception as e:
                        os.chdir(Static.GIT_DIRECTORY)
                        self.running = False
                    self.initializing = False
                if not self.animation_stopped:
                    self.draw_rect(screen, Static.BLUE, Static.WHITE, 8, self.main_container)
                    moving_sprites.draw(self.screen)
                    moving_sprites.update(0.25)
                    animation.animate()
                    pygame.display.flip()
                    self.clock.tick(60)

            while not self.buzzer_hit and not self.solution_shown:
                key, button = self.handle_events()
                if self.escape_pressed:
                    break
                # noone buzzers
                if key == pygame.K_RETURN and self.hint_nr == 10:
                    self.buzzer_hit = True
                    for n in range(0, self.amount_players):
                        self.display_buzzer(screen, n, Static.GREY)
                    pygame.display.flip()
                    self.no_points_awarded = True
                    self.correct_answer = True

                if key == pygame.K_n:
                    self.print_hint(screen, self.hint_nr)
                    if self.hint_nr != 10:
                        self.hint_nr += 1

                # player buzzers
                if key in self.player_buzzer_keys:
                #if button in self.player_buzzer_keys:
                    #first_buzz = self.player_buzzer_keys.index(button)
                    first_buzz = self.player_buzzer_keys.index(key)
                    self.sound_channel.pause()
                    self.sound_animation_running = False
                    buzzer_container = self.display_buzzer(screen, first_buzz, Static.RED)
                    blit_text_objects(screen, buzzer_container, self.round_data[self.current_round]['solution_link'], self.MINI_TEXT)
                    if self.is_game_sounds:
                        buzzerHit = pygame.mixer.Sound(os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER, 'buzzer.wav'))
                        self.game_sound_channel.play(buzzerHit)
                    self.buzzer_hit = True
                    self.countdown(screen, 5)

            while self.buzzer_hit:
                key, button = self.handle_events()
                if self.escape_pressed:
                    break

                if key == pygame.K_n and self.correct_answer:
                    self.print_hint(screen, self.hint_nr)
                    if self.hint_nr != 10:
                        self.hint_nr += 1

                if key == pygame.K_RETURN:
                    # solution is shown
                    if not self.solution_shown and self.correct_answer:
                        self.show_solution(screen)
                        pygame.display.flip()
                        self.solution_shown = True
                    # next round is started
                    elif self.solution_shown:
                        self.buzzer_hit = False
                        self.solution_shown = False
                        if not self.winner_found:
                            self.current_round += 1
                            self.display_game_info(screen)
                            self.update_progress(screen)
                            self.play_round(screen)
                        else:
                            self.show_winner(screen)
                        pygame.display.flip()

                if not self.no_points_awarded and key in self.answer_keys:
                    self.award_points(screen, first_buzz, key, reset=True)
                    if not self.buzzer_hit:
                        for n in range(0, self.amount_players):
                            self.display_buzzer(screen, n, Static.LIGHT_BLUE)
                        pygame.display.flip()

                self.check_game_over()