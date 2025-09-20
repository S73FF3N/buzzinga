import os, random, pygame, pybuzzers
from pathlib import Path

from quiz_games import QuizGameBase
from static import Static
from game_utilities import mp3_to_wav
from animation import BuzzingaAnimation


class AudioQuiz(QuizGameBase):
    def __init__(self, clock, game_data, players, is_game_sounds, max_score, buzzer_set):
        super().__init__(clock, game_data, players, is_game_sounds, max_score, buzzer_set)
        self.current_sound = None
        self.current_solution_sound = None
        self.current_solution_image = None

        self.buzzer_set = buzzer_set
        self.buzzering_player = None
        def handle_buzz(buzzer_set: pybuzzers.BuzzerSet, buzzer: int):
            if not self.buzzer_hit and not self.initializing:
                self.buzzering_player = buzzer + 1
        
        self.buzzer_set.on_buzz(handle_buzz)
        self.buzzer_set.start_listening()

    def clean_game_data(self):
        game_data_path = Path(self.game_data)
        for f in game_data_path.iterdir():
            if f.is_dir() or f.suffix.lower() not in (".wav", ".mp3"):
                continue
            elif f.suffix.lower() == ".mp3":
                try:
                    converted = mp3_to_wav(f)
                    self.cleaned_game_data.append(converted)
                except Exception:
                    pass
            else:
                self.cleaned_game_data.append(f)

    def load_round_data(self):    
        for f in self.cleaned_game_data:
            if not os.path.splitext(f)[0].endswith("_solution"):
                file_path = os.path.join(self.game_data,f)
                base = os.path.basename(file_path)
                name_o = os.path.splitext(base)[0]
                name = name_o.replace("_", " ").replace("zzz", "(").replace("uuu", ")")

                # Build the expected solution file name
                name_no_ext, ext = os.path.splitext(f)
                solution_filename = f"{name_no_ext}_solution"
                for ext in [".wav", ".mp3"]:
                    solution_path = os.path.join(self.game_data, solution_filename + ext)
                    if os.path.exists(solution_path):
                        solution_sound = solution_path
                    else:
                        solution_sound = None
                
                solution_img_path_list = [os.path.join(self.game_data, f"{name_no_ext}_solution{img_ext}") for img_ext in [".jpg", ".png", ".jpeg", ".bmp"]]
                solution_image = None
                for img_path in solution_img_path_list:
                    if os.path.exists(img_path):
                        solution_image = img_path
                        break

                self.round_data.append({"solution": name if not name_no_ext.endswith("_example") else name[:-8], "data": file_path, "solution_sound": solution_sound, "solution_img": solution_image, "example": False if not name_no_ext.endswith("_example") else True})
        self.total_rounds = len(self.round_data)
        random.shuffle(self.round_data)
        # Ensure the example round is first if present
        for i, rd in enumerate(self.round_data):
            if rd.get("example", False):
                self.round_data.insert(0, self.round_data.pop(i))
                break

    def play_round(self):
        """Display the image and handle buzzer logic for the image quiz."""
        current_data = self.round_data[self.current_round - 1]
        self.current_sound = pygame.mixer.Sound(current_data["data"])
        self.current_solution = current_data["solution"]
        self.current_solution_image = current_data["solution_img"]
        self.current_solution_sound = current_data["solution_sound"]
        if self.current_solution_sound:
            self.current_solution_sound = pygame.mixer.Sound(current_data["solution_sound"])
        self.sound_channel.play(self.current_sound)
        self.sound_animation_running = True

    def check_sound_animation(self):
        if self.sound_animation_running:
            self.draw_rect(Static.WHITE, Static.WHITE, 8, self.main_container)
            self.sound_moving_sprites.draw(self.screen)
            self.sound_moving_sprites.update(0.15)
            self.sound_animation.animate()
            pygame.display.flip()
            self.clock.tick(60)

    def run(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        self.screen.fill(Static.WHITE)
        pygame.display.set_caption(self.game_name)
        moving_sprites = pygame.sprite.Group()
        animation = BuzzingaAnimation(self.main_container, self.image_cache)
        moving_sprites.add(animation)
        self.sound_moving_sprites.add(self.sound_animation)

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

            while not self.buzzer_hit and not self.solution_shown:
                self.check_sound_animation()

                key = self.handle_events()
                if self.escape_pressed:
                    self.sound_channel.pause()
                    self.sound_animation_running = False
                    break
                # noone buzzers
                if key == pygame.K_RETURN:
                    self.buzzer_hit = True
                    for n in range(0, self.amount_players):
                        self.display_buzzer(n, Static.GREY)
                    pygame.display.flip()

                # replay sound
                if key == pygame.K_p:
                    self.sound_channel.stop()
                    self.sound_animation_running = True
                    self.sound_channel.play(self.current_sound)

                # player buzzers
                if self.buzzering_player:
                    first_buzz = self.buzzering_player - 1
                    if self.current_solution_sound:
                        self.sound_channel.stop()
                    else:
                        self.sound_channel.pause()
                    self.sound_animation_running = False
                    self.display_buzzer(first_buzz, Static.RED)
                    self.buzzering_player = None
                    self.play_buzzer_sound()
                    self.buzzer_hit = True
                    self.countdown(5)

            while self.buzzer_hit:
                self.check_sound_animation()

                key = self.handle_events()
                if self.escape_pressed:
                    break

                if key == pygame.K_RETURN:
                    # solution is shown
                    if not self.solution_shown and not self.winner_found:
                        if self.current_solution_sound:
                            self.sound_channel.play(self.current_solution_sound)
                        else:
                            self.sound_channel.unpause()
                        if self.current_solution_image:
                            self.sound_animation_running = False
                        else:
                            self.sound_animation_running = True
                        self.show_solution()
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
                            self.display_game_info()
                            self.update_progress()
                            self.play_round()
                        else:
                            self.show_winner()
                        pygame.display.flip()

                # points are awarded
                if key in self.answer_keys and self.solution_shown:
                    self.award_points(first_buzz, key)

                self.check_game_over()

            # Update and draw particles
            for p in self.particles[:]:
                p.update()
                p.draw(self.screen)
                if p.life <= 0:
                    self.particles.remove(p)
                pygame.display.flip()            
            self.clock.tick(60)