import os, random, pygame, pybuzzers, traceback

from quiz_games import QuizGameBase
from static import Static
from game_utilities import convert_image_to, load_image, adjust_image_size, load_video, adjust_video_size
from animation import BuzzingaAnimation


class ImageQuiz(QuizGameBase):
    def __init__(self, clock, game_data, players, is_game_sounds, max_score, buzzer_set, image_reveal_animation):
        self.image_exts = (".bmp", ".png", ".jpg", ".jpeg", ".webp", ".avif")
        self.video_exts = (".mp4", ".mov", ".avi", ".webm", ".mkv")
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
        self.clip = None
        self.video_frame_time = 0.0
        self.video_playing = False
        self.solution_video_playing = False
        self.tiles = None


    def clean_game_data(self):
        game_data_list = os.listdir(self.game_data)
        for f in game_data_list:
            full_path = os.path.join(self.game_data, f)
            if os.path.isdir(full_path):
                continue
            lower_f = f.lower()
            if lower_f.endswith(self.image_exts):
                try:
                    converted = convert_image_to(full_path, "png")
                    if converted:
                        # store filename (existing code expects filenames, joins with self.game_data later)
                        self.cleaned_game_data.append({"filename": os.path.basename(converted), "file_type": "image"})
                except Exception as e:
                    print(f"convert_image_to raised for {full_path}: {e}")
            elif lower_f.endswith(self.video_exts):
                self.cleaned_game_data.append({"filename": os.path.basename(full_path), "file_type": "video"})


    def load_round_data(self):    
        for item in self.cleaned_game_data:
            f = item["filename"]
            file_type = item["file_type"]
            if not os.path.splitext(f)[0].endswith("_solution"):
                file_path = os.path.join(self.game_data,f)
                base = os.path.basename(file_path)
                name_o = os.path.splitext(base)[0]
                name = name_o.replace("_", " ").replace("zzz", "(").replace("uuu", ")")

                # Build the expected solution file name
                name_no_ext, ext = os.path.splitext(f)
                solution_filename = f"{name_no_ext}_solution"
                for ext in self.image_exts + self.video_exts:
                    solution_path = os.path.join(self.game_data, solution_filename + ext)
                    if os.path.exists(solution_path):
                        solution_file = solution_path
                        if ext.lower() in self.image_exts:
                            solution_file_type = "image"
                        else:
                            solution_file_type = "video"
                        break
                    else:
                        solution_file = None
                        solution_file_type = None
                
                self.round_data.append({
                    "solution": name if not name_no_ext.endswith("_example") else name[:-8],
                    "data": file_path,
                    "solution_file": solution_file,
                    "example": False if not name_no_ext.endswith("_example") else True,
                    "file_type": file_type,
                    "solution_file_type": solution_file_type,
                })
        self.total_rounds = len(self.round_data)
        random.shuffle(self.round_data)
        # Ensure the example round is first if present
        for i, rd in enumerate(self.round_data):
            if rd.get("example", False):
                self.round_data.insert(0, self.round_data.pop(i))
                break

    def get_current_file(self):
        current_data = self.round_data[self.current_round - 1]
        current_file = current_data["data"]
        self.current_file_type = current_data["file_type"]
        self.current_solution = current_data["solution"]
        self.current_solution_file = current_data["solution_file"]
        self.current_solution_file_type = current_data["solution_file_type"]

        if self.current_file_type == "image":
            file_to_display = load_image(current_file, os.path.join(
                Static.ROOT_EXTENDED, Static.GAME_FOLDER_IMAGES, self.game_data
            ))

            # Scale image
            image_size = adjust_image_size(
                file_to_display, self.left_container_width - 16, self.main_container_height - 16
            )
            file_to_display = pygame.transform.scale(file_to_display, image_size)
            rect = file_to_display.get_rect(center=self.main_container.center)
        elif self.current_file_type == "video":
            file_to_display = load_video(current_file, os.path.join(
                Static.ROOT_EXTENDED, Static.GAME_FOLDER_IMAGES, self.game_data
            ))

            video_size = adjust_video_size(
                file_to_display.w, file_to_display.h, self.left_container_width - 16, self.main_container_height - 16
            )
            file_to_display = file_to_display.resized(new_size=video_size)

            rect = None

        return file_to_display, rect

    def play_round(self, tile_size=(50, 50), reveal_speed=60):
        file_to_display, rect = self.get_current_file()

        pygame.draw.rect(self.screen, Static.WHITE, self.main_container)

        if self.current_file_type == "image":
            if not self.image_reveal_animation:
                # Draw full image immediately
                self.screen.blit(file_to_display, rect)
                pygame.draw.rect(self.screen, Static.WHITE, self.main_container, width=8)
                pygame.display.flip()
                self.tiles = None
                return

            # Prepare tile reveal state
            tile_w, tile_h = tile_size
            cols = (rect.width + tile_w - 1) // tile_w
            rows = (rect.height + tile_h - 1) // tile_h

            tiles = []
            for r in range(rows):
                for c in range(cols):
                    tile_rect = pygame.Rect(
                        rect.left + c * tile_w,
                        rect.top + r * tile_h,
                        min(tile_w, rect.width - c * tile_w),
                        min(tile_h, rect.height - r * tile_h),
                    )
                    tiles.append(tile_rect)

            random.shuffle(tiles)

            # Store state for update loop
            self.tiles = tiles
            self.revealed_tiles = []
            self.reveal_speed = reveal_speed
            self.next_reveal_time = pygame.time.get_ticks()

        elif self.current_file_type == "video":
            self.tiles = None
            self.clip = file_to_display
            self.video_frame_time = 0.0
            self.solution_video_playing = False
            self.video_playing = True

            # Immediately draw first frame so playback visually starts after initializing
            try:
                self._draw_video_frame()
            except Exception as e:
                print("DEBUG: failed to draw first frame:", e)

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

    def _draw_video_frame(self):
        if not self.clip:
            return
        t = min(self.video_frame_time, getattr(self.clip, "duration", 0))
        try:
            frame = self.clip.get_frame(t)
        except Exception as e:
            print("DEBUG: get_frame error:", e)
            return

        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        self.screen.blit(frame_surface, self.main_container.move(16, 16))
        pygame.display.update(self.main_container)


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
                        traceback.print_exc()
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
                #if self.solution_video_playing:
                #    self.solution_video_playing = False
                #    if self.clip:
                #        self.clip.close()
                #        self.clip = None

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

                dt = self.clock.tick(60) / 1000.0
                if self.video_playing and self.clip:
                    self._draw_video_frame()
                    self.video_frame_time += dt
                    if getattr(self.clip, "duration", None) and self.video_frame_time >= self.clip.duration:
                        self.video_playing = False

                # Update tile reveal each frame
                self.update_tile_reveal()
                pygame.display.flip()

            while self.buzzer_hit:
                if self.video_playing:
                    self.video_playing = False
                    if self.clip:
                        self.clip.close()
                        self.clip = None
                    
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

                dt = self.clock.tick(60) / 1000.0
                if self.solution_video_playing and self.clip:
                    self._draw_video_frame()
                    self.video_frame_time += dt
                    if getattr(self.clip, "duration", None) and self.video_frame_time >= self.clip.duration:
                        self.solution_video_playing = False

                if self.continue_reveal:
                    self.update_tile_reveal()

                self.check_game_over()
                pygame.display.flip()

            # Update and draw particles
            for p in self.particles[:]:
                p.update()
                p.draw(self.screen)
                if p.life <= 0:
                    self.particles.remove(p)
                pygame.display.flip()
