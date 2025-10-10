import os, random, pygame, pybuzzers

from quiz_games import QuizGameBase
from static import Static
from game_utilities import convert_image_to, load_image, adjust_image_size
from animation import BuzzingaAnimation


class ImageQuiz(QuizGameBase):
    def __init__(self, clock, game_data, players, is_game_sounds, max_score, buzzer_set, image_reveal_animation):
        super().__init__(clock, game_data, players, is_game_sounds, max_score, buzzer_set, image_reveal_animation)
        self.buzzer_set = buzzer_set
        self.buzzering_player = None
        def handle_buzz(buzzer_set: pybuzzers.BuzzerSet, buzzer: int):
            if not self.buzzer_hit and not self.initializing:
                self.buzzering_player = buzzer + 1
        
        self.buzzer_set.on_buzz(handle_buzz)
        self.buzzer_set.start_listening()
        self.image_reveal_animation = image_reveal_animation
        self.continue_reveal = False


    def clean_game_data(self):
        # avoid changing cwd; use full paths
        game_data_list = os.listdir(self.game_data)
        for f in game_data_list:
            full_path = os.path.join(self.game_data, f)
            if os.path.isdir(full_path) or not f.lower().endswith((".bmp", ".png", ".jpg", ".jpeg", ".webp", ".avif")):
                continue
            try:
                converted = convert_image_to(full_path, "png")
                if converted:
                    # store filename (existing code expects filenames, joins with self.game_data later)
                    self.cleaned_game_data.append(os.path.basename(converted))
            except Exception as e:
                print(f"convert_image_to raised for {full_path}: {e}")


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
                for ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                    solution_path = os.path.join(self.game_data, solution_filename + ext)
                    if os.path.exists(solution_path):
                        solution_image = solution_path
                        break
                    else:
                        solution_image = None
                
                self.round_data.append({"solution": name if not name_no_ext.endswith("_example") else name[:-8], "data": file_path, "solution_image": solution_image, "example": False if not name_no_ext.endswith("_example") else True})
        self.total_rounds = len(self.round_data)
        random.shuffle(self.round_data)
        # Ensure the example round is first if present
        for i, rd in enumerate(self.round_data):
            if rd.get("example", False):
                self.round_data.insert(0, self.round_data.pop(i))
                break

    def get_current_image(self):
        current_data = self.round_data[self.current_round - 1]
        current_image = current_data["data"]
        self.current_solution = current_data["solution"]
        self.current_solution_image = current_data["solution_image"]

        img = load_image(current_image, os.path.join(
            Static.ROOT_EXTENDED, Static.GAME_FOLDER_IMAGES, self.game_data
        ))

        # Scale image
        image_size = adjust_image_size(
            img, self.left_container_width - 16, self.main_container_height - 16
        )
        img = pygame.transform.scale(img, image_size)

        self.round_img = img
        self.round_img_rect = img.get_rect(center=self.main_container.center)

        return img

    def play_round(self, tile_size=(50, 50), reveal_speed=60):
        img = self.get_current_image()

        pygame.draw.rect(self.screen, Static.WHITE, self.main_container)

        if not self.image_reveal_animation:
            # Draw full image immediately
            self.screen.blit(img, self.round_img_rect)
            pygame.draw.rect(self.screen, Static.WHITE, self.main_container, width=8)
            pygame.display.flip()
            self.tiles = None
            return

        # Prepare tile reveal state
        tile_w, tile_h = tile_size
        cols = (self.round_img_rect.width + tile_w - 1) // tile_w
        rows = (self.round_img_rect.height + tile_h - 1) // tile_h

        tiles = []
        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(
                    self.round_img_rect.left + c * tile_w,
                    self.round_img_rect.top + r * tile_h,
                    min(tile_w, self.round_img_rect.width - c * tile_w),
                    min(tile_h, self.round_img_rect.height - r * tile_h),
                )
                tiles.append(rect)

        random.shuffle(tiles)

        # Store state for update loop
        self.tiles = tiles
        self.revealed_tiles = []
        self.reveal_speed = reveal_speed
        self.next_reveal_time = pygame.time.get_ticks()

    def update_tile_reveal(self):
        if not self.tiles:  # no reveal in progress
            return

        now = pygame.time.get_ticks()
        if now >= self.next_reveal_time and self.tiles:
            self.revealed_tiles.append(self.tiles.pop())
            if self.continue_reveal:
                self.next_reveal_time = now + self.reveal_speed // 7
            else:
                self.next_reveal_time = now + self.reveal_speed

        # Draw background
        pygame.draw.rect(self.screen, Static.WHITE, self.main_container)

        # Draw revealed tiles
        for rect in self.revealed_tiles:
            src_rect = pygame.Rect(
                rect.x - self.round_img_rect.x,
                rect.y - self.round_img_rect.y,
                rect.width,
                rect.height
            )
            self.screen.blit(self.round_img, rect, src_rect)

        # Draw border
        pygame.draw.rect(self.screen, Static.WHITE, self.main_container, width=8)
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
                    first_buzz = self.buzzering_player - 1
                    self.display_buzzer(first_buzz, Static.RED)
                    self.buzzering_player = None
                    self.play_buzzer_sound()
                    self.buzzer_hit = True
                    self.countdown(5)

                # Update tile reveal each frame
                self.update_tile_reveal()

            while self.buzzer_hit:
                key = self.handle_events()
                if self.escape_pressed:
                    break
                
                #self.update_tile_reveal()
                if key == pygame.K_s:
                    self.continue_reveal = True

                if key == pygame.K_RETURN:
                    # solution is shown
                    if not self.solution_shown and not self.winner_found:
                        self.continue_reveal = False
                        self.show_solution()
                        pygame.display.flip()
                        self.solution_shown = True
                    # next round is started
                    elif self.solution_shown:
                        self.buzzer_hit = False
                        self.solution_shown = False
                        self.particles = []
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
                
                if self.continue_reveal:
                    self.update_tile_reveal()

                self.check_game_over()

            # Update and draw particles
            for p in self.particles[:]:
                p.update()
                p.draw(self.screen)
                if p.life <= 0:
                    self.particles.remove(p)
                pygame.display.flip()            
            self.clock.tick(60)