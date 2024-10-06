import os, random, pygame, time

from quiz_games import QuizGameBase
from static import Static
from game_utilities import mp3_to_wav, blit_text_objects
from animation import BuzzingaAnimation


class AudioQuiz(QuizGameBase):
    def __init__(self, SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT, clock, game_data, players, is_game_sounds, max_score):
        super().__init__(SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT, clock, game_data, players, is_game_sounds, max_score)
        self.current_sound = None

    def clean_game_data(self):
        os.chdir(self.game_data)
        game_data_list = os.listdir(self.game_data)
        for f in game_data_list:
            if os.path.isdir(f) or not f.lower().endswith((".wav", ".mp3")):
                pass
            elif not f.lower().endswith(".wav"):
                try:
                    f = mp3_to_wav(f)
                    self.cleaned_game_data.append(f)
                except:
                    pass
            else:
                self.cleaned_game_data.append(f)

    def load_round_data(self):    
        for f in self.cleaned_game_data:
            file_path = os.path.join(self.game_data,f)
            base = os.path.basename(file_path)
            name_o = os.path.splitext(base)[0]
            name = name_o.replace("_", " ")
            name = name.replace("zzz", "(")
            name = name.replace("uuu", ")")
            self.round_data.append({"solution": name, "data": file_path})
        self.total_rounds = len(self.round_data)
        random.shuffle(self.round_data)

    def play_round(self, screen):
        """Display the image and handle buzzer logic for the image quiz."""
        current_data = self.round_data[self.current_round - 1]
        self.current_sound = pygame.mixer.Sound(current_data["data"])
        self.current_solution = current_data["solution"]
        self.sound_channel.play(self.current_sound)
        self.sound_animation_running = True

    def check_sound_animation(self, screen):
        if self.sound_animation_running:
            self.draw_rect(screen, Static.WHITE, Static.WHITE, 8, self.main_container)
            self.sound_moving_sprites.draw(self.screen)
            self.sound_moving_sprites.update(0.15)
            self.sound_animation.animate()
            pygame.display.flip()
            self.clock.tick(60)

    def run(self, screen):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        screen.fill(Static.WHITE)
        pygame.display.set_caption(self.game_name)
        moving_sprites = pygame.sprite.Group()
        animation = BuzzingaAnimation(self.main_container, self.image_cache)
        moving_sprites.add(animation)
        self.sound_moving_sprites.add(self.sound_animation)

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
                self.check_sound_animation(screen)

                key, button = self.handle_events()
                if self.escape_pressed:
                    break
                # noone buzzers
                if key == pygame.K_RETURN:
                    self.buzzer_hit = True
                    for n in range(0, self.amount_players):
                        self.display_buzzer(screen, n, Static.GREY)
                    pygame.display.flip()

                if key == pygame.K_p:
                    self.sound_channel.stop()
                    self.sound_animation_running = True
                    self.sound_channel.play(self.current_sound)

                # player buzzers
                if key in self.player_buzzer_keys:
                #if button in self.player_buzzer_keys:
                    #first_buzz = self.player_buzzer_keys.index(button)
                    first_buzz = self.player_buzzer_keys.index(key)
                    self.sound_channel.pause()
                    self.sound_animation_running = False
                    self.display_buzzer(screen, first_buzz, Static.RED)
                    if self.is_game_sounds:
                        buzzerHit = pygame.mixer.Sound(os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER, 'buzzer.wav'))
                        self.game_sound_channel.play(buzzerHit)
                    self.buzzer_hit = True
                    self.countdown(screen, 5)

            while self.buzzer_hit:
                self.check_sound_animation(screen)

                key, button = self.handle_events()
                if self.escape_pressed:
                    break

                if key == pygame.K_RETURN:
                    # solution is shown
                    if not self.solution_shown and not self.winner_found:
                        self.sound_channel.unpause()
                        self.sound_animation_running = True
                        self.show_solution(screen)
                        pygame.display.flip()
                        self.solution_shown = True
                    # next round is started
                    elif self.solution_shown:
                        self.sound_channel.stop()
                        self.sound_animation_running = False
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

                # points are awarded
                if key in self.answer_keys and self.solution_shown:
                    self.award_points(screen, first_buzz, key)

                self.check_game_over()