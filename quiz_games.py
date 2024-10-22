import pygame, os, sys, pybuzzers

import pygame.locals

from static import Static
from game_utilities import blit_text_objects
from animation import SoundAnimation

class QuizGameBase:
    def __init__(self, clock, game_data, players, is_game_sounds, max_score, buzzer_set):
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN)
        self.clock = clock
        self.sound_channel = pygame.mixer.Channel(0)
        self.game_sound_channel = pygame.mixer.Channel(1)
        self.game_name = os.path.basename(os.path.dirname(game_data)).replace('_', ' ')
        self.players = players  # List of player names
        self.amount_players = len(players)
        self.scores = [0 for player in players]
        self.answer_keys = [pygame.K_r, pygame.K_f]
        self.image_cache = {}
        self.current_round = 0
        self.total_rounds = 0
        self.max_score = max_score
        self.is_game_sounds = is_game_sounds
        self.buzzer_hit = False
        self.game_data = game_data
        self.cleaned_game_data = []
        self.clean_game_data()
        self.round_data = []
        self.load_round_data()
        self.running = True
        self.initializing = True
        self.winner_found = False
        self.animation_stopped = False
        self.solution_shown = False
        self.current_solution = None
        self.escape_pressed = False

        self.left_container_width = self.SCREEN_WIDTH * 8 // 10
        self.right_container_width = self.SCREEN_WIDTH - self.left_container_width
        self.main_container_height = self.SCREEN_HEIGHT * 8 // 10
        self.top_container_height = (self.SCREEN_HEIGHT - self.main_container_height) // 2
        self.bottom_container_height = self.SCREEN_HEIGHT - self.main_container_height - self.top_container_height

        # Adjust the bottom container to fill any remaining gap
        self.bottom_container_height += self.SCREEN_HEIGHT - (self.top_container_height + self.main_container_height + self.bottom_container_height)

        self.top_left_container = pygame.Rect(0, 0, self.left_container_width, self.top_container_height)
        self.main_container = pygame.Rect(0, self.top_container_height, self.left_container_width, self.main_container_height)
        self.bottom_left_container = pygame.Rect(0, (self.top_container_height + self.main_container_height),
                                            self.left_container_width, self.bottom_container_height)
        self.top_right_container = pygame.Rect(self.left_container_width, 0, self.right_container_width,
                                                    self.top_container_height)
        self.bottom_right_container = pygame.Rect(self.left_container_width,
                                            (self.top_container_height + self.main_container_height),
                                            self.right_container_width, self.bottom_container_height)
        
        self.player_container_height = self.SCREEN_HEIGHT * 2 // 10
        self.player_label_container_height = self.player_container_height * 4 // 10
        self.player_buzzer_container_width = self.right_container_width * 5 // 10
        self.player_buzzer_container_height = self.player_container_height * 6 // 10
        self.player_score_container_width = self.right_container_width * 5 // 10
        self.player_score_container_height = self.player_container_height * 6 // 10
        
        self.BUTTON_WIDTH = self.SCREEN_WIDTH * 0.625 // 3
        self.BUTTON_HEIGHT = self.SCREEN_HEIGHT * 5 // 81
        self.BUTTON_SPACING = self.SCREEN_WIDTH / 100 * 4
        self.TOGGLE_ADJ = int(self.BUTTON_WIDTH * 0.075)
        
        self.MENU_TEXT = pygame.font.SysFont("Verdana", self.SCREEN_HEIGHT // 5)
        self.MEDIUM_TEXT = pygame.font.SysFont("Verdana", self.SCREEN_HEIGHT // 9, bold=True)
        self.SMALL_TEXT = pygame.font.SysFont("Verdana", self.SCREEN_HEIGHT // 25, bold=True)
        self.MINI_TEXT = pygame.font.SysFont("Verdana", self.SCREEN_HEIGHT // 40, bold=True)
        
        self.sound_moving_sprites = pygame.sprite.Group()
        self.sound_animation = SoundAnimation(self.main_container, self.image_cache)
        self.sound_animation_running = False
    
    def clean_game_data(self):
        pass

    def load_round_data(self):
        pass

    def draw_rect(self, color, border_color, border_width, rect):
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, border_color, rect, width=border_width)

    def display_buzzer(self, i, buzzer_color, width=0, y_offset=8):
        player_buzzer_container = pygame.Rect(self.left_container_width, (
                                            self.top_container_height + self.player_label_container_height - y_offset + (i * self.player_container_height)),
                                            self.player_buzzer_container_width, self.player_buzzer_container_height)
        pygame.draw.circle(self.screen, buzzer_color, player_buzzer_container.center, self.player_buzzer_container_width / 3.5, width)
        return player_buzzer_container
    
    def update_score(self, n):        
        player_label_container = pygame.Rect(self.left_container_width,
                                                (self.top_container_height + n * self.player_container_height),
                                                self.right_container_width, self.player_label_container_height)
        player_container = pygame.Rect(self.left_container_width, self.top_container_height + n * self.player_container_height,
                                        self.right_container_width, self.player_container_height)
        player_score_container = pygame.Rect((self.left_container_width + self.player_buzzer_container_width), (
                    self.top_container_height + self.player_label_container_height - 8 + n * self.player_container_height),
                                            self.player_score_container_width, self.player_score_container_height)
        pygame.draw.rect(self.screen, Static.WHITE, player_score_container)
        blit_text_objects(self.screen, player_score_container, str(self.scores[n]), self.MEDIUM_TEXT, Static.LIGHT_BLUE)
        self.draw_rect(Static.LIGHT_BLUE, Static.WHITE, 8, player_label_container)
        blit_text_objects(self.screen, player_label_container, self.players[n], self.SMALL_TEXT)
        pygame.draw.rect(self.screen, Static.LIGHT_BLUE, pygame.Rect(player_container.x+8, player_container.y+8, player_container.w-16, player_container.h-16), width=4)

    def update_progress(self):
        self.draw_rect(Static.RED, Static.WHITE, 8, self.top_right_container)
        if self.current_round == 0:
            progress = self.SMALL_TEXT.render(f"{str(self.total_rounds)} Runden", 1, Static.WHITE)
        else:
            progress = self.SMALL_TEXT.render(f"Runde {str(self.current_round)}/{str(self.total_rounds)}", 1, Static.WHITE)
        self.screen.blit(progress, progress.get_rect(center=self.top_right_container.center))
    
    def display_game_info(self):
        self.draw_rect(Static.RED, Static.WHITE, 8, self.top_left_container)
        self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_right_container)
        self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_left_container)
        if not os.path.isdir(self.game_data):
            game_title = os.path.basename(self.game_data)
            game_title = os.path.splitext(game_title)[0].replace('_', ' ')
        else:
            game_title = os.path.basename(os.path.dirname(self.game_data)).replace('_', ' ')
        blit_text_objects(self.screen, self.top_left_container, game_title, self.SMALL_TEXT)
        self.update_progress()

        for n in range(0, self.amount_players):
            self.update_score(n)
            self.display_buzzer(n, Static.LIGHT_BLUE)

        pygame.display.flip()
        pygame.display.update()

    def play_round(self):
        pass
    
    def countdown(self, count_from):
        for i in range(1, count_from):
            time_left = str(count_from - i)
            blit_text_objects(self.screen, self.bottom_right_container, time_left, self.SMALL_TEXT)
            countdown = self.SMALL_TEXT.render(time_left, 1, Static.WHITE)
            self.screen.blit(countdown, countdown.get_rect(center=self.bottom_right_container.center))
            pygame.display.flip()
            pygame.time.wait(1000)
            if time_left != 0:
                self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_right_container)
                pygame.display.flip()
                if self.is_game_sounds:
                    countdown_sound = pygame.mixer.Sound(os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER, 'countdown.wav'))
                    self.game_sound_channel.play(countdown_sound)
        if self.is_game_sounds:
            countdown_end_sound = pygame.mixer.Sound(os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER, 'countdown_end.wav'))
            self.game_sound_channel.play(countdown_end_sound)

    def play_buzzer_sound(self):
        if self.is_game_sounds:
            buzzerHit = pygame.mixer.Sound(os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER, 'buzzer.wav'))
            self.game_sound_channel.play(buzzerHit)

    def award_points(self, first_buzz, key, reset=False):
        if key == self.answer_keys[0]:
            self.scores[first_buzz] += 1
            if reset:
                self.correct_answer = True
        if key == self.answer_keys[1]:
            self.scores[first_buzz] -= 1
            if reset:
                self.buzzer_hit = False
        self.update_score(first_buzz)
        pygame.display.flip()

    def show_solution(self):
        blit_text_objects(self.screen, self.bottom_left_container, self.current_solution, self.SMALL_TEXT)

    def check_game_over(self):
        if max(self.scores) >= self.max_score:
            self.winner_found = True
        elif self.current_round == self.total_rounds and self.solution_shown:
            self.winner_found = True

    def show_winner(self):
        self.buzzer_hit = False
        self.solution_shown = True
        self.draw_rect(Static.BLUE, Static.WHITE, 8, self.main_container)
        self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_left_container)
        winner_ix = [i for i, x in enumerate(self.scores) if x == max(self.scores)]
        title_rect = pygame.Rect(0, self.top_container_height, self.left_container_width, self.main_container_height/2)
        blit_text_objects(self.screen, title_rect, "GEWINNER", self.MEDIUM_TEXT)
        winners = []
        [winners.append(self.players[i]) for i in winner_ix]
        for line in range(len(winners)):
            winner_rect = pygame.Rect(0, self.top_container_height+self.main_container_height/2.8+(80*line), self.left_container_width, self.main_container_height/2/len(winners))
            blit_text_objects(self.screen, winner_rect, winners[line], self.MEDIUM_TEXT, Static.RED)

    def handle_events(self):
        key_status = pygame.key.get_pressed()
        key_pressed = None
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
                if key_pressed == pygame.K_ESCAPE:
                    self.escape_pressed = True
                    self.sound_channel.stop()
                    os.chdir(Static.GIT_DIRECTORY)
        return key_pressed
    
    def run(self):
        pass
