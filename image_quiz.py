import os, random, pygame, pybuzzers

from quiz_games import QuizGameBase
from static import Static
from game_utilities import convert_image_to, load_image, adjust_image_size
from animation import BuzzingaAnimation


class ImageQuiz(QuizGameBase):
    def __init__(self, clock, game_data, players, is_game_sounds, max_score, buzzer_set):
        super().__init__(clock, game_data, players, is_game_sounds, max_score, buzzer_set)
        self.buzzer_set = buzzer_set
        self.buzzering_player = None
        def handle_buzz(buzzer_set: pybuzzers.BuzzerSet, buzzer: int):
            if not self.buzzer_hit and not self.initializing:
                self.buzzering_player = buzzer
        
        self.buzzer_set.on_buzz(handle_buzz)
        self.buzzer_set.start_listening()

    def clean_game_data(self):
        os.chdir(self.game_data)
        game_data_list = os.listdir(self.game_data)
        for f in game_data_list:
            if os.path.isdir(f) or not f.lower().endswith((".bmp", ".png", ".jpg", ".jpeg")):
                pass
            elif not f.lower().endswith(".bmp"):
                try:
                    f = convert_image_to(f, "bmp")
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

    def play_round(self):
        current_data = self.round_data[self.current_round - 1]
        current_image = current_data["data"]
        self.current_solution = current_data["solution"]
        img = load_image(current_image, os.path.join(Static.ROOT_EXTENDED, Static.GAME_FOLDER_IMAGES, self.game_data))
        image_size = adjust_image_size(img, self.left_container_width, self.main_container_height)
        img = pygame.transform.scale(img, image_size)
        pygame.draw.rect(self.screen, Static.WHITE, self.main_container)
        pygame.display.flip()
        self.screen.blit(img, img.get_rect(center=self.main_container.center))
        pygame.draw.rect(self.screen, Static.WHITE, self.main_container, width=8)

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

            while not self.buzzer_hit and not self.solution_shown:
                key = self.handle_events()

                if self.escape_pressed:
                    break
                # noone buzzers
                if key == pygame.K_RETURN:
                    self.buzzer_hit = True
                    for n in range(0, self.amount_players):
                        self.display_buzzer(n, Static.GREY)
                    pygame.display.flip()

                # player buzzers
                if self.buzzering_player:
                    first_buzz = self.buzzering_player
                    self.display_buzzer(first_buzz, Static.RED)
                    self.buzzering_player = None
                    self.play_buzzer_sound()
                    self.buzzer_hit = True
                    self.countdown(5)

            while self.buzzer_hit:
                key = self.handle_events()
                if self.escape_pressed:
                    break

                if key == pygame.K_RETURN:
                    # solution is shown
                    if not self.solution_shown and not self.winner_found:
                        self.show_solution()
                        pygame.display.flip()
                        self.solution_shown = True
                    # next round is started
                    elif self.solution_shown:
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