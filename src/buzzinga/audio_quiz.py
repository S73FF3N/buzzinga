import os, random, pygame, pybuzzers
from pathlib import Path

from .quiz_games import QuizGameBase
from .static import Static
from .game_utilities import is_hidden_file
from .animation import BuzzingaAnimation


class AudioQuiz(QuizGameBase):
    # Class-level so the category menu counts rounds with the same extensions
    sound_exts = (".wav", ".mp3")
    solution_image_exts = (".jpg", ".png", ".jpeg", ".bmp")

    def __init__(self, clock, game_data, players, is_game_sounds, max_score, buzzer_set, image_reveal_animation, language=None):
        super().__init__(clock, game_data, players, is_game_sounds, max_score, buzzer_set, image_reveal_animation, language)
        self.current_sound = None
        self.current_solution_sound = None

        self.buzzer_set = buzzer_set
        self.buzzering_player = None
        def handle_buzz(buzzer_set: pybuzzers.BuzzerSet, buzzer: int):
            if not self.buzzer_hit and not self.initializing:
                self.buzzering_player = buzzer + 1
        
        self.set_buzzer_handler(on_buzz=handle_buzz)

    def clean_game_data(self):
        game_data_path = Path(self.game_data)
        for f in game_data_path.iterdir():
            # pygame.mixer plays both formats directly
            if f.is_file() and not is_hidden_file(f) and f.suffix.lower() in self.sound_exts:
                self.cleaned_game_data.append(f)

    def load_round_data(self):    
        folder_files = [str(p) for p in Path(self.game_data).iterdir() if p.is_file() and not is_hidden_file(p)]

        def find_solution(solution_filename, extensions):
            # Match the extension case-insensitively (e.g. "_solution.MP3")
            for candidate in folder_files:
                stem, ext = os.path.splitext(candidate)
                if stem == solution_filename and ext.lower() in extensions:
                    return candidate
            return None

        for f in self.cleaned_game_data:
            if not os.path.splitext(f)[0].endswith("_solution"):
                file_path = os.path.join(self.game_data,f)
                base = os.path.basename(file_path)
                name_o = os.path.splitext(base)[0]
                name = name_o.replace("_", " ").replace("zzz", "(").replace("uuu", ")")

                # Build the expected solution file name
                name_no_ext, ext = os.path.splitext(f)
                solution_filename = f"{name_no_ext}_solution"
                solution_sound = find_solution(solution_filename, self.sound_exts)
                solution_image = find_solution(solution_filename, self.solution_image_exts)

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
        # show_solution() in the base class displays current_solution_file
        self.current_solution_file = current_data["solution_img"]
        self.current_solution_file_type = "image" if current_data["solution_img"] else None
        self.current_solution_sound = current_data["solution_sound"]
        if self.current_solution_sound:
            self.current_solution_sound = pygame.mixer.Sound(current_data["solution_sound"])
        self.sound_channel.play(self.current_sound)
        self.sound_animation_running = True

    def round_file_name(self):
        if 0 < self.current_round <= len(self.round_data):
            return os.path.basename(self.round_data[self.current_round - 1]["data"])
        return ""

    def stop_round_media(self):
        self.sound_channel.stop()
        self.sound_animation_running = False
        self.current_solution_sound = None
        self.current_solution_file = None

    def check_sound_animation(self):
        if self.sound_animation_running:
            self.draw_rect(Static.WHITE, Static.WHITE, 8, self.main_container)
            self.sound_moving_sprites.draw(self.screen)
            self.sound_moving_sprites.update(0.15)
            self.sound_animation.animate()
            pygame.display.flip()

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
                    self.animation_stopped = True
                    self.current_round += 1
                    self.update_progress()
                    self.start_round()
                    pygame.display.flip()
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
                    self.first_buzz = None
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
                    self.first_buzz = self.buzzering_player - 1
                    if self.current_solution_sound:
                        self.sound_channel.stop()
                    else:
                        self.sound_channel.pause()
                    self.sound_animation_running = False
                    self.display_buzzer(self.first_buzz, Static.RED)
                    self.buzzering_player = None
                    self.play_buzzer_sound()
                    self.buzzer_hit = True
                    self.countdown(5)

                self.clock.tick(60)

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
                        if self.current_solution_file:
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
                            self.start_round()
                        else:
                            self.show_winner()
                        pygame.display.flip()

                # points are awarded
                if (key in self.answer_keys and self.solution_shown
                        and not self.round_load_failed and self.first_buzz is not None):
                    self.award_points(self.first_buzz, key)

                self.check_game_over()
                self.clock.tick(60)

            # Update and draw particles
            self.update_particles()
            pygame.display.flip()
            self.clock.tick(60)