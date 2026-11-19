import pygame, os, sys, traceback

import pygame.locals

from .static import Static, Confetti
from .translations import german
from .game_utilities import load_static_sound, blit_text_objects, optimize_text_in_container, load_image, adjust_image_size, load_video, adjust_video_size
from .animation import SoundAnimation

# Buzzer sets whose listener thread is running. pybuzzers keeps one BuzzerSet
# per device, and its stop_listening() closes the device underneath a read
# that may still be blocked on it, so each set's thread is started once and
# reused by every following game; only the handlers are swapped.
_listening_buzzer_sets = set()


class QuizGameBase:
    def __init__(self, clock, game_data, players, is_game_sounds, max_score, buzzer_set, image_reveal_animation, language=None):
        # Texts on the game screens follow the language chosen in the menu
        self.language = language or german
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
        self.current_file_type = None
        self.current_solution = None
        self.current_solution_file = None
        self.current_solution_file_type = None
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

        self.particles = []
        # Index of the player whose buzz is being judged in the current round,
        # None if nobody buzzed
        self.first_buzz = None
        # True while the current round could not be loaded; the round is then
        # shown as resolved so Enter moves on to the next one
        self.round_load_failed = False


    @classmethod
    def parse_entry(cls, entry):
        """Turn one entry of a category's JSON file into round data. Raises
        KeyError, TypeError or ValueError if the entry is incomplete. Only
        quiz types whose categories are JSON files implement this."""
        raise NotImplementedError

    @classmethod
    def parse_rounds(cls, data, warn=True):
        """Parse the entries of a category's JSON file. Incomplete entries are
        skipped, so a single bad entry does not stop the whole category. The
        category menu uses this too, so its round count matches the game."""
        rounds = []
        for index, entry in enumerate(data):
            try:
                rounds.append(cls.parse_entry(entry))
            except (KeyError, TypeError, ValueError) as e:
                if warn:
                    print(f"Skipping entry {index + 1}: missing or invalid {e!r}")
        return rounds

    def start_round(self):
        """Show the current round. If it cannot be loaded (corrupt file,
        missing codec or library), show an error in place of the round and
        mark it as resolved, so the next Enter press skips to the next round
        instead of leaving an empty screen or crashing."""
        self.round_load_failed = False
        try:
            self.play_round()
        except Exception:
            traceback.print_exc()
            self.show_round_load_error()

    def round_file_name(self):
        """File shown on the error screen when the round cannot be loaded."""
        return ""

    def stop_round_media(self):
        """Stop whatever the failed round already started playing."""

    def show_round_load_error(self):
        self.round_load_failed = True
        self.stop_round_media()

        self.draw_rect(Static.BLUE, Static.WHITE, 8, self.main_container)
        message_rect = pygame.Rect(self.main_container.x, self.main_container.y,
                                   self.main_container.w, self.main_container.h // 2)
        file_rect = pygame.Rect(self.main_container.x, self.main_container.centery,
                                self.main_container.w, self.main_container.h // 4)
        optimize_text_in_container(self.screen, message_rect,
                                   self.language['round_load_error'])
        optimize_text_in_container(self.screen, file_rect, self.round_file_name(), color=Static.YELLOW)
        for n in range(self.amount_players):
            self.display_buzzer(n, Static.GREY)

        # Resolved state: buzzers are ignored and Enter starts the next round
        self.buzzer_hit = True
        self.solution_shown = True

    def set_buzzer_handler(self, on_buzz=None, on_button_down=None):
        """Make the given handler the only one on the buzzer set, so buzzes
        no longer reach earlier games, and start listening if not yet done."""
        self.buzzer_set.clear_handlers()
        if on_buzz:
            self.buzzer_set.on_buzz(on_buzz)
        if on_button_down:
            self.buzzer_set.on_button_down(on_button_down)
        if self.buzzer_set not in _listening_buzzer_sets:
            self.buzzer_set.start_listening()
            _listening_buzzer_sets.add(self.buzzer_set)

    def update_particles(self):
        """Advance and draw the confetti. The caller flips the display once
        per frame, so the cost does not grow with the number of particles."""
        for p in self.particles[:]:
            p.update()
            p.draw(self.screen)
            if p.life <= 0:
                self.particles.remove(p)

    def wait_responsive(self, ms):
        """Wait for `ms` milliseconds while still pumping the event loop, so the
        window manager does not flag the window as unresponsive. Key presses
        stay queued and are handled once the wait is over."""
        end = pygame.time.get_ticks() + ms
        while pygame.time.get_ticks() < end:
            pygame.event.pump()
            self.clock.tick(60)

    # Trigger confetti
    def celebrate(self, x, y, amount=100):
        for _ in range(amount):
            self.particles.append(Confetti(x, y))
    
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
        #blit_text_objects(self.screen, player_score_container, str(self.scores[n]), self.MEDIUM_TEXT, Static.LIGHT_BLUE)
        optimize_text_in_container(self.screen, player_score_container, str(self.scores[n]), color=Static.LIGHT_BLUE)
        self.draw_rect(Static.LIGHT_BLUE, Static.WHITE, 8, player_label_container)
        # blit_text_objects(self.screen, player_label_container, self.players[n], self.SMALL_TEXT)
        optimize_text_in_container(self.screen, player_label_container, self.players[n])
        pygame.draw.rect(self.screen, Static.LIGHT_BLUE, pygame.Rect(player_container.x+8, player_container.y+8, player_container.w-16, player_container.h-16), width=4)

    def update_progress(self):
        self.draw_rect(Static.RED, Static.WHITE, 8, self.top_right_container)
        if self.current_round == 0:
            progress = f"{self.total_rounds} {self.language['rounds']}"
        else:
            progress = f"{self.language['round']} {self.current_round}/{self.total_rounds}"
        #self.screen.blit(progress, progress.get_rect(center=self.top_right_container.center))
        optimize_text_in_container(self.screen, self.top_right_container, progress)
        
    
    def display_game_info(self):
        self.draw_rect(Static.RED, Static.WHITE, 8, self.top_left_container)
        self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_right_container)
        self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_left_container)
        if not os.path.isdir(self.game_data):
            game_title = os.path.basename(self.game_data)
            game_title = os.path.splitext(game_title)[0].replace('_', ' ')
        else:
            game_title = os.path.basename(self.game_data)
        #blit_text_objects(self.screen, self.top_left_container, game_title, self.SMALL_TEXT)
        optimize_text_in_container(self.screen, self.top_left_container, game_title)
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
            self.wait_responsive(1000)
            if time_left != 0:
                self.draw_rect(Static.RED, Static.WHITE, 8, self.bottom_right_container)
                pygame.display.flip()
                if self.is_game_sounds:
                    self.game_sound_channel.play(load_static_sound('countdown.wav'))
        if self.is_game_sounds:
            self.game_sound_channel.play(load_static_sound('countdown_end.wav'))

    def play_buzzer_sound(self):
        if self.is_game_sounds:
            self.game_sound_channel.play(load_static_sound('buzzer.wav'))

    def award_points(self, first_buzz, key, reset=False):
        if key == self.answer_keys[0]:
            self.scores[first_buzz] += 1
            if reset:
                self.correct_answer = True
                self.points_awarded = True
        if key == self.answer_keys[1]:
            self.scores[first_buzz] -= 1
            if reset:
                #self.points_awarded = False
                self.buzzer_hit = False
        self.update_score(first_buzz)
        pygame.display.flip()

    def show_solution(self):
        optimize_text_in_container(self.screen, self.bottom_left_container, self.current_solution)
        # show solution image
        if self.current_solution_file:
            if self.current_solution_file_type == "image":
                img = load_image(self.current_solution_file, os.path.join(Static.ROOT_EXTENDED, Static.GAME_FOLDER_IMAGES, self.game_data))
                image_size = adjust_image_size(img, self.left_container_width-16, self.main_container_height-16) # subtract 16 for the border
                img = pygame.transform.scale(img, image_size)
                pygame.draw.rect(self.screen, Static.WHITE, self.main_container)
                pygame.display.flip()
                self.screen.blit(img, img.get_rect(center=self.main_container.center))
                pygame.draw.rect(self.screen, Static.WHITE, self.main_container, width=8)
            elif self.current_solution_file_type == "video":
                file_to_display = load_video(self.current_solution_file, os.path.join(
                Static.ROOT_EXTENDED, Static.GAME_FOLDER_IMAGES, self.game_data
                ))

                video_size = adjust_video_size(
                    file_to_display.w, file_to_display.h, self.left_container_width - 16, self.main_container_height - 16
                )
                file_to_display = file_to_display.resized(new_size=video_size)
                self.clip = file_to_display
                self.video_frame_time = 0.0
                self.solution_video_playing = True
                # Start the solution video's audio in sync with its frames.
                # Defined on subclasses that support video playback (e.g. ImageQuiz).
                if hasattr(self, "_start_video_audio"):
                    self._start_video_audio(self.clip)

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
        self.celebrate(self.left_container_width // 4 * 3, self.top_container_height * 2)
        self.celebrate(self.left_container_width // 4, self.top_container_height * 5)
        winner_ix = [i for i, x in enumerate(self.scores) if x == max(self.scores)]
        title_rect = pygame.Rect(0, self.top_container_height, self.left_container_width, self.main_container_height/2)
        blit_text_objects(self.screen, title_rect, self.language['winner'], self.MEDIUM_TEXT)
        winners = []
        [winners.append(self.players[i]) for i in winner_ix]
        for line in range(len(winners)):
            winner_rect = pygame.Rect(0, self.top_container_height+self.main_container_height/2.8+(80*line), self.left_container_width, self.main_container_height/2/len(winners))
            #blit_text_objects(self.screen, winner_rect, winners[line], self.MEDIUM_TEXT, Static.RED)
            optimize_text_in_container(self.screen, winner_rect, winners[line], color=Static.RED)
            

    def handle_events(self):
        key_status = pygame.key.get_pressed()
        key_pressed = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            alt_f4 = (event.type == pygame.KEYDOWN and (event.key == pygame.K_F4 and (key_status[pygame.K_LALT] or key_status[pygame.K_RALT])))
            if alt_f4:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                key_pressed = event.key
                if key_pressed == pygame.K_ESCAPE:
                    self.escape_pressed = True
                    self.sound_channel.stop()
                    self.running = False
        return key_pressed
    
    def run(self):
        pass
