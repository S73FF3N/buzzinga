import pygame, os, sys, shutil, subprocess, shutil, json
from pygame import gfxdraw
from itertools import islice
from pathlib import Path
import stat

from static import Static
from game_utilities import load_and_scale_image, load_image, blit_text_objects, text_objects, count_files_by_extensions
from translations import english, german
from image_quiz import ImageQuiz
from audio_quiz import AudioQuiz
from question_quiz import QuestionQuiz
from hint_quiz import HintQuiz
from whoknowsmore_quiz import WhoKnowsMoreQuiz
from animation import BuzzingaAnimation


class Buzzinga():
    def __init__(self):
        pygame.init()

        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.SCREEN = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN)

        self.BUTTON_WIDTH = self.SCREEN_WIDTH * 0.625 // 3
        self.BUTTON_HEIGHT = self.SCREEN_HEIGHT * 5 // 81
        self.BUTTON_SPACING = self.SCREEN_WIDTH / 100 * 4

        self.button_x_start1 = ((self.SCREEN_WIDTH - 2 * self.BUTTON_WIDTH) // 2) - (self.BUTTON_SPACING // 2)
        self.button_x_start2 = self.button_x_start1 + self.BUTTON_WIDTH + self.BUTTON_SPACING
        self.button_x_start3 = self.button_x_start2 + self.BUTTON_WIDTH + self.BUTTON_SPACING
        self.button_x_start0 = self.button_x_start1 - self.BUTTON_WIDTH - self.BUTTON_SPACING

        self.button_layout_32 = []
        for col, x_start in enumerate([self.button_x_start0, self.button_x_start1, self.button_x_start2, self.button_x_start3]):
            for row in range(5, 13):
                y_position = self.SCREEN_HEIGHT * row // 14
                self.button_layout_32.append((x_start, y_position, self.BUTTON_WIDTH, self.BUTTON_HEIGHT))

        self.TOGGLE_ADJ = int(self.BUTTON_WIDTH * 0.075)
        self.BUTTON_PADDING_X = self.SCREEN_WIDTH / 50
        self.BUTTON_PADDING_Y = self.SCREEN_WIDTH / 25

        self.MENU_TEXT = pygame.font.SysFont("Ariel", self.SCREEN_HEIGHT // 5)
        self.MEDIUM_TEXT = pygame.font.SysFont("Ariel", self.SCREEN_HEIGHT // 9)
        self.SMALL_TEXT = pygame.font.SysFont("Ariel", self.SCREEN_HEIGHT // 25)
        self.MINI_TEXT = pygame.font.SysFont("Ariel", self.SCREEN_HEIGHT // 35)

        self.current_language = german
        self.language_toggle = True
        self.game_type = "images"
        self.player = [self.current_language['player1'], self.current_language['player2'], self.current_language['player3'], self.current_language['player4']]
        self.game_dir = None
        self.is_game_sounds = False
        self.game_modus = True
        self.points_to_win = 10

        self.image_cache = {}
        self.is_game_choosen = False
        self.delete_modus = False
        self.game_folder = ""
        self.pages = 0
        self.buttons = {}

        self.key_instructions = []

        self.running = True
        self.choose_game_menu_running = False
        self.choose_category_menu = False
        self.settings_menu_running = False
        self.start_game = False

        self.FOLDER_MAPPING = {
            "images": Static.GAME_FOLDER_IMAGES,
            "sounds": Static.GAME_FOLDER_SOUNDS,
            "questions": Static.GAME_FOLDER_QUESTIONS,
            "hints": Static.GAME_FOLDER_HINTS,
            "who-knows-more": Static.GAME_FOLDER_WHO_KNOWS_MORE,
        }

        pygame.display.set_caption('BUZZINGA')
        self.clock = pygame.time.Clock()
        self.build_required_folders()

    def game(self):
        common_args = (self.clock, self.game_dir, self.player, self.is_game_sounds, self.points_to_win, self.current_language)
        match self.game_type:
            case "images":
                quiz = ImageQuiz(*common_args)
            case "sounds":
                quiz = AudioQuiz(*common_args)
            case "questions":
                quiz = QuestionQuiz(*common_args)
            case "hints":
                quiz = HintQuiz(*common_args)
            case "who-knows-more":
                quiz = WhoKnowsMoreQuiz(*common_args)
        quiz.run()

    def get_amount_rounds(self, category_folder):
        if self.game_type == "images":
            file_count = count_files_by_extensions(f"{self.game_folder}/{category_folder}/", '.bmp', '.jpg', '.jpeg', '.png')
            return file_count
        elif self.game_type == "sounds":
            file_count = count_files_by_extensions(f"{self.game_folder}/{category_folder}/", '.wav', '.mp3')
            return file_count
        else:
            with open(f"{self.game_folder}/{category_folder}", 'r', encoding='utf-8') as f:
                data = json.load(f)
                return len(data)

    def build_required_folders(self):
        for folder in self.FOLDER_MAPPING.keys():
            dir_name = os.path.join(Static.ROOT_EXTENDED, folder)
            if not os.path.exists(dir_name):
                try:
                    os.mkdir(dir_name)
                except OSError as e:
                    print(f"Error creating directory {dir_name}: {e}")

    def is_hovered(self, rect):
        mouse_pos = pygame.mouse.get_pos()
        return rect.collidepoint(mouse_pos)
    
    def render_button(self, text, rect, click, inactive_color=Static.RED, active_color=Static.YELLOW, text_color=Static.WHITE, image=False):
        hover = self.is_hovered(rect)
        if hover:
            pygame.draw.rect(self.SCREEN, inactive_color, rect)
            pygame.draw.rect(self.SCREEN, active_color, rect, width=4)
        else:
            pygame.draw.rect(self.SCREEN, inactive_color, rect)

        if not image:
            blit_text_objects(self.SCREEN, rect, text, self.SMALL_TEXT, text_color)
        else:
            image_file = load_image(text, os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER))
            scaled_image = pygame.transform.scale(image_file, (int(rect.height / 2), rect.height // 2))
            self.SCREEN.blit(scaled_image, scaled_image.get_rect(center=rect.center))
        return hover and click and pygame.time.get_ticks() > 100

    def toggle_btn(self, text, text2, rect, click, text_color=Static.WHITE, enabled=True, draw_toggle=True, blit_text=True, enabled_color=Static.RED):
        hover = self.is_hovered(rect)
        rect_height = rect.h // 2 + (1 if rect.h % 2 == 0 else 0)
        toggle_x_offset = rect.x + int(self.BUTTON_PADDING_X)
        
        text_surf, text_rect = text_objects(text, self.SMALL_TEXT, color=text_color)
        toggle_start_x = toggle_x_offset + text_rect.width
        toggle_center_y = rect.y + rect.h // 2
        
        if draw_toggle:
            pygame.draw.rect(self.SCREEN, enabled_color, (toggle_start_x, rect.y + rect.h // 4, self.TOGGLE_ADJ, rect_height))

            circle_radius = rect.h // 4
            small_circle_radius = rect.h // 5
            left_circle_x = toggle_start_x
            right_circle_x = toggle_start_x + circle_radius + self.TOGGLE_ADJ // 2

            circles = [
                (left_circle_x, toggle_center_y, circle_radius, enabled_color),
                (right_circle_x, toggle_center_y, circle_radius, enabled_color),
                (right_circle_x if enabled else left_circle_x, toggle_center_y, small_circle_radius, Static.WHITE)
            ]
            for args in circles:
                self.draw_circle(self.SCREEN, *args)

        if blit_text:
            text_rect.topleft = (rect.x, rect.y + rect.h // 4)
            self.SCREEN.blit(text_surf, text_rect)

            text_surf2, text_rect2 = text_objects(text2, self.SMALL_TEXT, color=text_color)
            text_rect2.topleft = (toggle_start_x + circle_radius + self.TOGGLE_ADJ + int(self.BUTTON_PADDING_Y), rect.y + rect.h // 4)
            self.SCREEN.blit(text_surf2, text_rect2)
            
        return hover and click and pygame.time.get_ticks() > 100
    
    def draw_circle(self, surface, x, y, radius, color):
        gfxdraw.aacircle(surface, x, y, radius, color)
        gfxdraw.filled_circle(surface, x, y, radius, color)

    def draw_button(self, text, text2, rect, click, color, is_image=False, enabled=None, toggle=False):
        if toggle:
            return self.toggle_btn(text, text2, rect, click, enabled=enabled)
        else:
            return self.render_button(text, rect, click, inactive_color=color, active_color=color, text_color=Static.WHITE, image=is_image)
        
    def show_mouse(self):
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(True)

    def player_name_input(self, rect, click, inactive_color=Static.RED, active_color=Static.YELLOW):
        color = active_color if self.is_hovered(rect) else inactive_color
        pygame.draw.rect(self.SCREEN, color, rect, 5)
        return self.is_hovered(rect) and click and pygame.time.get_ticks() > 100
    
    def print_player_name(self, x_pos, player_name):
        x, y, w, h = self.button_layout_32[x_pos + 8]

        pygame.draw.rect(self.SCREEN, Static.BLUE, (x, y, w, h))
        pygame.draw.rect(self.SCREEN, Static.RED, (x, y, w, h), 5)
        pygame.draw.rect(self.SCREEN, Static.RED, (x - w // 4, y, w // 4, h))

        image_file = load_and_scale_image('user.bmp', os.path.join(Static.ROOT_EXTENDED, Static.STATIC_FOLDER), h // 2, self.image_cache)
        self.SCREEN.blit(image_file, image_file.get_rect(center=pygame.Rect(x - w // 4, y, w // 4, h).center))

        blit_text_objects(self.SCREEN, pygame.Rect(x, y, w, h), player_name, self.SMALL_TEXT, Static.WHITE)
        pygame.display.update()

    def process_delete(self, categories_to_delete):
        if not categories_to_delete:
            return None
        
        for category in categories_to_delete:
            if self.game_type in ["images", "sounds"]:
                delete_status = self.delete_category(f"{self.game_folder}/{category}", multiple_files=True)
            else:
                delete_status = self.delete_category(f"{self.game_folder}/{category}.json", multiple_files=False)
        
        return delete_status
    
    def setup_selected_category(self, category_folder):
        self.is_game_choosen = True
        category_folder = category_folder.replace(' ', '_')
        if self.game_type in ["images", "sounds"]:
            self.game_dir = f"{self.game_folder}/{category_folder}/"
        else:
            self.game_dir = f"{self.game_folder}/{category_folder}.json"
        self.settings_menu()

    def handle_category_selection(self, click, game_options, categories_to_delete):
        for game_option in game_options:
            game_name, clicked, x, y, w, h, total_rounds = game_option

            if self.delete_modus and game_name in categories_to_delete:
                inactive_color = Static.GREY
            else:
                inactive_color = Static.RED
            self.render_button(game_name, pygame.Rect(x, y, w, h), clicked, inactive_color=inactive_color)
            pygame.draw.circle(self.SCREEN, Static.LIGHT_BLUE, (x+w, y), 24)
            pygame.draw.circle(self.SCREEN, Static.WHITE, (x+w, y), 24, width=2)
            blit_text_objects(self.SCREEN, pygame.Rect(x+w-12,y-12,24,24), str(total_rounds), self.MINI_TEXT)
            
            if clicked:
                if not self.delete_modus:
                    self.setup_selected_category(game_name)
                else:
                    self.toggle_category_for_deletion(game_option, categories_to_delete)

    def delete_category(self, game_dir, multiple_files=True):
        game_path = Path(game_dir)

        def remove_readonly(func, path, _):
            os.chmod(path, stat.S_IWRITE)
            func(path)

        if multiple_files:
            for file_path in game_path.iterdir():
                if file_path.is_file():
                    try:
                        file_path.chmod(0o777)
                    except PermissionError as e:
                        print(e)
                    try:
                        file_path.unlink()
                    except OSError as e:
                        print(e)
            try:
                shutil.rmtree(game_path, onerror=remove_readonly)
                return self.current_language['deletion_successful']
            except OSError:
                return self.current_language['deletion_failed']
        else:
            try:
                game_path.chmod(0o777)
            except PermissionError:
                return "Permission error: "
            try:
                if game_path.is_file():
                    game_path.unlink()
                else:
                    shutil.rmtree(game_path, onerror=remove_readonly)
                return self.current_language['deletion_successful']
            except OSError:
                return self.current_language['deletion_failed']

    def toggle_category_for_deletion(self, game_option, categories_to_delete):
        _, _, x, y, w, h, total_rounds = game_option
        pygame.draw.rect(self.SCREEN, Static.GREY, (x, y, w, h))
        
        category_folder = game_option[0].replace(' ', '_')
        if category_folder not in categories_to_delete:
            categories_to_delete.append(category_folder)

    def get_free_disk_space(self):
        usage = shutil.disk_usage(Static.ROOT)
        total_size = usage.total / (1024.0 ** 3)
        free_size = usage.free / (1024.0 ** 3)
        free_percentage = int(100.0 / total_size * free_size)
        return str(free_percentage)
    
    def build_key_instructions(self):
        self.key_instructions = [
            ('Esc', 'Escape', 3),
            ('Enter', self.current_language['progress'], 4)
        ]
        match self.game_type:
            case 'images':
                self.key_instructions.extend(
                    [('r', self.current_language['correct'], 5),
                    ('f', self.current_language['wrong'], 6)]
                )
            case 'sounds':
                self.key_instructions.extend(
                    [('r', self.current_language['correct'], 5),
                    ('f', self.current_language['wrong'], 6),
                    ('p', 'replay', 7)]
                )
            case 'hints':
                self.key_instructions.extend(
                    [('r', self.current_language['correct'], 5),
                    ('f', self.current_language['wrong'], 6),
                    ('n', 'next hint', 7)]
                )
            case 'questions':
                pass
            case 'who-knows-more':
                self.key_instructions.extend(
                    [('r', self.current_language['correct'], 5),
                    ('f', self.current_language['wrong'], 6),
                    ('1-9', self.current_language['display_answer'], 7)]
                )               

    def build_category_buttons_dict(self):
        self.game_folder = os.path.join(Static.ROOT_EXTENDED, self.FOLDER_MAPPING[self.game_type])
        categories = [item for item in os.listdir(self.game_folder) if not item.startswith('.')]
        
        self.pages = (len(categories) - 1) // Static.BUTTONS_PER_PAGE + 1
        self.buttons = {f'page {page+1}': [] for page in range(self.pages)}

        for page, category_chunk in enumerate(self.chunked(categories, Static.BUTTONS_PER_PAGE), 1):
            for btn_index, item in enumerate(category_chunk):
                x, y, w, h = self.button_layout_32[btn_index]
                total_rounds = self.get_amount_rounds(item)
                category_name = os.path.splitext(item)[0].replace('_', ' ')
                self.buttons[f'page {page}'].append([category_name, x, y, w, h, total_rounds])

    @staticmethod
    def chunked(iterable, n):
        it = iter(iterable)
        while True:
            chunk = list(islice(it, n))
            if not chunk:
                break
            yield chunk

    def handle_events(self):
        key_status = pygame.key.get_pressed()
        key_pressed = None
        letter_pressed = None
        event = None
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            alt_f4 = (event.type == pygame.KEYDOWN and (event.key == pygame.K_F4 and (key_status[pygame.K_LALT] or key_status[pygame.K_RALT])))
            if alt_f4:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                key_pressed = event.key
                letter_pressed = event.unicode
                if key_pressed == pygame.K_ESCAPE:
                    self.escape_pressed = True
                    os.chdir(Static.GIT_DIRECTORY)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click = True
        return key_pressed, letter_pressed, click
    
    def menu_setup(self, rect, title):
        self.show_mouse()
        self.SCREEN.fill(Static.BLUE)
        blit_text_objects(self.SCREEN, rect, title, self.MEDIUM_TEXT)

    def start_screen_setup(self):
        self.SCREEN.fill(Static.BLUE)
        blit_text_objects(self.SCREEN, pygame.Rect(0, self.SCREEN_HEIGHT * 4 / 5, self.SCREEN_WIDTH, self.SCREEN_HEIGHT / 5), 'PRESS ANY KEY', self.SMALL_TEXT)

    def start_screen(self):
        self.start_screen_setup()
        main_container = pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT * 0.8)
        moving_sprites = pygame.sprite.Group()
        animation = BuzzingaAnimation(main_container, self.image_cache)
        moving_sprites.add(animation)

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.players_names_menu()

            pygame.draw.rect(self.SCREEN, Static.BLUE, main_container)
            moving_sprites.draw(self.SCREEN)
            moving_sprites.update(0.25)
            animation.animate()
            pygame.display.flip()
            self.clock.tick(60)
            pygame.display.update()

    def players_names_menu_setup(self):
        self.menu_setup(pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT / 2), self.current_language['who_plays'])

        self.player = [self.current_language['player1'], self.current_language['player2'], self.current_language['player3'], self.current_language['player4']]
        for i, player in enumerate(self.player):
            self.print_player_name(i, player)

    def players_names_menu(self):
        self.players_names_menu_setup()
        player_name_input_active = [False, False, False, False]
        input_mappings = [(8, 0), (9, 1), (10, 2), (11, 3)]

        while self.running:
            click = False
            key, letter, click = self.handle_events()

            if key:
                active = [i for i, x in enumerate(player_name_input_active) if x]
                if active:
                    player_index = active[0]
                    if key == pygame.K_BACKSPACE:
                        self.player[player_index] = self.player[player_index][:-1]
                    else:
                        self.player[player_index] += letter
                    self.print_player_name(player_index, self.player[player_index])

            for layout_idx, player_idx in input_mappings:
                x, y, w, h = self.button_layout_32[layout_idx]
                if self.player_name_input(pygame.Rect(x, y, w, h), click):
                    player_name_input_active = [False] * len(player_name_input_active)
                    player_name_input_active[player_idx] = True
                    self.player[player_idx] = ''
                    self.print_player_name(player_idx, self.player[player_idx])

            self.draw_button(self.current_language['language'], '', pygame.Rect(self.button_layout_32[17]), False, Static.RED)
            if self.draw_button('English', 'Deutsch', pygame.Rect(self.button_layout_32[18]), click, Static.RED, enabled=self.language_toggle, toggle=True):
                self.language_toggle = not self.language_toggle
                self.current_language = german if self.current_language == english else english
                self.players_names_menu()

            x11, y11, w11, h11 = self.button_layout_32[19]
            x12, y12, w12, h12 = self.button_layout_32[16]

            if self.render_button(self.current_language['choose_game'], pygame.Rect(x11, y11, w11, h11), click):
                self.choose_game_menu()

            elif self.render_button('X', pygame.Rect(x12+w12*3/4, y12, w12/4, h12), click):
                # Shutdown the system (works only on Linux with sudo privileges)
                os.popen("sudo poweroff")

            pygame.display.update()
            self.clock.tick(100)
    
    def choose_game_menu(self):
        self.menu_setup(pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT / 2), self.current_language['which_game'])
        self.choose_game_menu_running = True

        button_data = [
            (self.current_language['image_quiz'], 8, "images"),
            ('Audio Quiz', 9, "sounds"),
            ('Multiple Choice Quiz', 10, "questions"),
            (self.current_language['hints'], 11, "hints"),
            (self.current_language['who_knows_more'], 12, "who-knows-more")
        ]

        while self.choose_game_menu_running:
            click = False
            key, letter, click = self.handle_events()

            for button_text, layout_index, game_type in button_data:
                x, y, w, h = self.button_layout_32[layout_index]
                
                if self.render_button(button_text, pygame.Rect(x, y, w, h), click):
                    self.game_type = game_type
                    self.choose_category()
            
            x, y, w, h = self.button_layout_32[20]
            if self.render_button(self.current_language['back'], pygame.Rect(x+w/2, y, w/2, h), click):
                        self.choose_game_menu_running = False
                        self.players_names_menu()

            pygame.display.update()
            self.clock.tick(100)

    def choose_category_setup(self, import_status="", no_categories=False):
        self.menu_setup(pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT / 2), self.current_language['game_category'])
        free_space = self.get_free_disk_space()
        blit_text_objects(self.SCREEN, pygame.Rect(self.SCREEN_WIDTH * 11 / 15, self.SCREEN_HEIGHT * 8 / 9, self.SCREEN_WIDTH * 4 / 15, self.SCREEN_HEIGHT * 1 / 9), f"{free_space} % {self.current_language['free_disk_space']}", self.SMALL_TEXT)
        blit_text_objects(self.SCREEN, pygame.Rect(0, self.SCREEN_HEIGHT * 8 / 9, self.SCREEN_WIDTH * 11 / 15, self.SCREEN_HEIGHT / 9), import_status, self.SMALL_TEXT)
        
        if no_categories:
            blit_text_objects(self.SCREEN, pygame.Rect(0, self.SCREEN_HEIGHT / 2, self.SCREEN_WIDTH, self.SCREEN_HEIGHT / 2), self.current_language['no_categories'], self.SMALL_TEXT)

    def choose_category(self, import_status=""):    
        self.build_category_buttons_dict()
        
        if not self.buttons:
            self.choose_category_setup(import_status=import_status, no_categories=True)
        else:
            self.choose_category_setup(import_status=import_status, no_categories=False)
        
        self.choose_category_menu = True
        game_options = []
        page_counter = 1
        categories_to_delete = []
        
        while self.choose_category_menu:
            key, letter, click = self.handle_events()
            
            if page_counter <= self.pages:
                for game in self.buttons[f'page {page_counter}']:
                    game_options.append([game[0], self.render_button(game[0], pygame.Rect(game[1], game[2], game[3], game[4]), click), *game[1:]])
            
            if page_counter < self.pages and self.render_button('>>', pygame.Rect(*self.button_layout_32[31]), click):
                self.delete_modus = False
                self.choose_category_setup(import_status)
                page_counter += 1
            
            x, y, w, h = self.button_layout_32[29]
            inactive_color = Static.GREY if self.delete_modus else Static.RED
            if self.render_button('delete.bmp', pygame.Rect(x, y, w/3, h), click, inactive_color=inactive_color, image=True):
                self.delete_modus = not self.delete_modus
                self.choose_category()
            
            inactive_color = Static.GREY if not self.delete_modus else Static.RED
            if self.render_button('trash-truck.bmp', pygame.Rect(x+w/3, y, w/3, h), click, inactive_color=inactive_color, image=True):
                self.delete_modus = False
                delete_status = self.process_delete(categories_to_delete)
                categories_to_delete.clear()
                if delete_status:
                    self.choose_category(import_status=delete_status)
            
            inactive_color = Static.GREY if self.delete_modus else Static.RED
            if self.render_button('flash-drive.bmp', pygame.Rect(x+2*w/3, y, w/3, h), click, inactive_color=inactive_color, image=True):
                if not self.delete_modus:
                    pygame.draw.rect(self.SCREEN, Static.BLUE, pygame.Rect(0, self.SCREEN_HEIGHT * 8 / 9, self.SCREEN_WIDTH * 11 / 15, self.SCREEN_HEIGHT / 9))
                    blit_text_objects(self.SCREEN, pygame.Rect(0, self.SCREEN_HEIGHT * 8 / 9, self.SCREEN_WIDTH * 11 / 15, self.SCREEN_HEIGHT / 9), self.current_language['import_files'], self.SMALL_TEXT)
                    pygame.display.flip()
                    language = "german" if self.current_language == german else "english"
                    try:
                        usb_input = subprocess.run([sys.executable, "check_usb_input.py", self.game_type, language], capture_output=True, text=True)
                        self.choose_category_menu = False
                        self.choose_category(import_status=usb_input.stdout.strip())
                    except subprocess.CalledProcessError as e:
                        print(f"An error occurred: {e}")
                        print(f"Error output: {e.stderr}")
            
            if self.render_button(self.current_language['back'], pygame.Rect(*self.button_layout_32[30]), click):
                self.delete_modus = False
                self.choose_category_menu = False
                self.choose_game_menu()

            self.handle_category_selection(click, game_options, categories_to_delete)

            pygame.display.update()
            self.clock.tick(60)

    def settings_menu_setup(self):
        self.menu_setup(pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT / 2), self.current_language['settings'])

        self.draw_button('SOUNDS', '', pygame.Rect(self.button_layout_32[8]), False, Static.RED)
        self.draw_button(self.current_language['mode'], '', pygame.Rect(self.button_layout_32[16]), False, Static.RED)

    def settings_menu(self):
        def no_buzzer_connected():
            blit_text_objects(self.SCREEN, pygame.Rect(0, self.SCREEN_HEIGHT * 8 / 9, self.SCREEN_WIDTH, self.SCREEN_HEIGHT / 9), self.current_language['no_buzzer'], self.SMALL_TEXT)

        self.settings_menu_setup()
        self.settings_menu_running, self.start_game = True, False
        self.build_key_instructions()

        while self.settings_menu_running:
            key_pressed, letter, click = self.handle_events()

            if self.draw_button(self.current_language['on'], self.current_language['off'], pygame.Rect(self.button_layout_32[9]), click, Static.RED, enabled=self.is_game_sounds, toggle=True):
                self.is_game_sounds = not self.is_game_sounds

            if self.draw_button(self.current_language['points'], self.current_language['all_rounds'], pygame.Rect(self.button_layout_32[17]), click, Static.RED, enabled=self.game_modus, toggle=True):
                self.game_modus = not self.game_modus

            if not self.game_modus:
                x9, y9, w9, h9 = self.button_layout_32[18]
                pygame.draw.rect(self.SCREEN, Static.RED, (x9, y9, w9 / 2, h9))
                blit_text_objects(self.SCREEN, pygame.Rect(x9, y9, w9 / 2, h9), str(self.points_to_win), self.SMALL_TEXT)

                if self.render_button('+', pygame.Rect(x9 + w9 / 2, y9, w9 / 2, h9 / 2), click):
                    self.points_to_win += 1

                if self.render_button('-', pygame.Rect(x9 + w9 / 2, y9 + h9 / 2, w9 / 2, h9 / 2), click) and self.points_to_win > 1:
                    self.points_to_win -= 1

            if self.game_modus:
                x9, y9, w9, h9 = self.button_layout_32[18]
                pygame.draw.rect(self.SCREEN, Static.BLUE, (x9, y9, w9, h9))

            if self.render_button(self.current_language['start_game'], pygame.Rect(self.button_layout_32[21]), click, Static.RED):
                if self.game_type == "who-knows-more":
                    self.start_game = True
                else:
                    try:
                        pygame.joystick.quit()
                        pygame.joystick.init()
                        if pygame.joystick.get_count() == 1:
                            pygame.joystick.Joystick(0).init()
                            self.start_game = True
                        else:
                            no_buzzer_connected()
                    except Exception as e:
                        no_buzzer_connected()

            x, y, w, h = self.button_layout_32[20]
            if self.render_button(self.current_language['back'], pygame.Rect(x+w/2, y, w/2, h), click, Static.RED):
                self.settings_menu_running = False
                self.choose_category(import_status="")

            x, y, w, h = self.button_layout_32[2]
            blit_text_objects(self.SCREEN, pygame.Rect(x,y,w,h), self.current_language['keys'], self.SMALL_TEXT, Static.WHITE)
            for key, text, position in self.key_instructions:
                x, y, w, h = self.button_layout_32[position]
                blit_text_objects(self.SCREEN, pygame.Rect(x,y,w/2,h), key, self.SMALL_TEXT, Static.WHITE)
                pygame.draw.rect(self.SCREEN, Static.WHITE, (x,y,w/2,h), width=4)
                blit_text_objects(self.SCREEN, pygame.Rect(x+w/2,y,w/2,h), text, self.SMALL_TEXT, Static.WHITE)

            if self.start_game:
                while self.start_game:
                    self.start_game = self.game()
                    self.settings_menu_running = False
                    self.players_names_menu()

            pygame.display.update()
            self.clock.tick(100)

if __name__ == "__main__":
    buzzinga = Buzzinga()
    buzzinga.start_screen()