# -*- coding: utf-8 -*-

import os, pygame, sys
import subprocess
from game_utilities import load_image
from pygame.locals import *
from pygame import gfxdraw, KEYDOWN, MOUSEBUTTONDOWN, K_ESCAPE, K_RETURN, K_BACKSPACE
from BuzzerGame import buzzer_game
from MultipleChoiceGame import multiple_choice_game
from static import Static

config = {'game_type': "images",
          'playerNames': ['Spieler 1', 'Spieler 2', 'Spieler 3', 'Spieler 4'],
          'game dir': '/home/pi/Desktop/SdR/Bilder/Tiere/',
          'game choosen': False,
          'game sounds': True,
          'game modus': True,
          'points_to_win': 10}

def game(screen, screenx, screeny):
        if config['game_type'] in ["images", "sounds"]:
                buzzer_game(4, config['playerNames'], config['game dir'], screen, screenx, screeny, config['game_type'], config['game sounds'], config['game modus'], config['points_to_win'])
        elif config['game_type'] == "questions":
                multiple_choice_game(4, config['playerNames'], config['game dir'], screen, screenx, screeny, config['game_type'],
                            config['game sounds'], config['game modus'], config['points_to_win'])
	
def text_objects(text, font, color=Static.BLACK):
        text_surface = font.render(text, 1, color)
        return text_surface, text_surface.get_rect()

def button(text, x, y, w, h, click, inactive_color=Static.RED, active_color=Static.LIGHT_RED, text_color=Static.WHITE, image=False):
        mouse = pygame.mouse.get_pos()
        return_value = False
        if x < mouse[0] < x + w and y < mouse[1] < y + h:
                pygame.draw.rect(SCREEN, active_color, (x,y,w,h))
                if click and pygame.time.get_ticks() > 100:
                        return_value = True
        else:
                pygame.draw.rect(SCREEN, inactive_color, (x,y,w,h))
        if image == False:
                text_surf, text_rect = text_objects(text, SMALL_TEXT, color=text_color)
                text_rect.center = (int(x +w/2), int(y + h/2))
                SCREEN.blit(text_surf, text_rect)
        else:
                image_file = load_image(text, '/home/pi/Desktop/venv/mycode/images')
                image_size = image_file.get_rect().size
                rela = image_size[0]/float(image_size[1])
                image_file = pygame.transform.scale(image_file, (int(h/2*rela), int(h/2)))
                SCREEN.blit(image_file, image_file.get_rect(center=pygame.Rect(x,y,w,h).center))
        return return_value

def player_name_input(x, y, w, h, click, inactive_color=Static.RED, active_color=Static.LIGHT_RED, text_color=Static.RED):
        mouse = pygame.mouse.get_pos()
        return_value = False
        if x < mouse[0] < x + w and y < mouse[1] < y + h:
                pygame.draw.rect(SCREEN, active_color, (x,y,w,h), 5)
                if click and pygame.time.get_ticks() > 100:
                        return_value = True
        else:
                pygame.draw.rect(SCREEN, inactive_color, (x,y,w,h), 5)
        return return_value

def draw_circle(surface, x, y, radius, color):
        gfxdraw.aacircle(surface, x, y, radius, color)
        gfxdraw.filled_circle(surface, x, y, radius, color)

def toggle_btn(text, text2, x, y, w, h, click, text_color=Static.RED, enabled=True, draw_toggle=True, blit_text=True, enabled_color=Static.LIGHT_RED):
        mouse = pygame.mouse.get_pos()
        rect_height = h // 2
        text_surf, text_rect = text_objects(text, SMALL_TEXT, color=text_color)
        if rect_height % 2 == 0:
                rect_height += 1
        if enabled and draw_toggle:
                pygame.draw.rect(SCREEN, enabled_color, (x + text_rect.width + int(SCREEN_WIDTH/50), y + int(h/4), TOGGLE_ADJ, rect_height))
                draw_circle(SCREEN, int(x + text_rect.width + SCREEN_WIDTH/50), y + int(h/2), int(h // 4), enabled_color)
                draw_circle(SCREEN, int(x + text_rect.width + SCREEN_WIDTH/50 + h/4 + TOGGLE_ADJ/2), y + int(h/2), int(h // 4), enabled_color)
                draw_circle(SCREEN, int(x + text_rect.width + SCREEN_WIDTH/50 + h/4 + TOGGLE_ADJ/2), y + int(h/2), int(h // 5), Static.WHITE)
        elif draw_toggle:
                pygame.draw.rect(SCREEN, enabled_color, (x + text_rect.width + int(SCREEN_WIDTH/50), y + int(h/4), TOGGLE_ADJ, rect_height))
                draw_circle(SCREEN, int(x + text_rect.width + SCREEN_WIDTH/50), y + int(h/2), int(h // 4), enabled_color)
                draw_circle(SCREEN, int(x + text_rect.width + SCREEN_WIDTH/50 + int(h/4) + TOGGLE_ADJ/2), y + int(h/2), int(h // 4), enabled_color)
                draw_circle(SCREEN, int(x + text_rect.width + SCREEN_WIDTH/50), y + int(h/2), int(h // 5), Static.WHITE)
        if blit_text:
                text_rect.topleft = (x, int(y + h/4))
                SCREEN.blit(text_surf, text_rect)
                text_surf2, text_rect2 = text_objects(text2, SMALL_TEXT, color=text_color)
                text_rect2.topleft = (x + text_rect.width + int(SCREEN_WIDTH/25) + int(h/4) + TOGGLE_ADJ, int(y + h/4))
                SCREEN.blit(text_surf2, text_rect2)
        return x < mouse[0] < x + w and y < mouse[1] < y + h and click and pygame.time.get_ticks() > 100

def show_mouse():
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(True)

def get_free_disk_space():
        statvfs = os.statvfs('/home/')
        total_size = statvfs.f_frsize*statvfs.f_blocks/(1024.0**3)
        free_size = statvfs.f_frsize*statvfs.f_bavail/(1024.0**3)
        free_percentage = int(100.0/total_size*free_size)
        return str(free_percentage)

def delete_category(game_dir, multiple_files=True):
        current_dir = os.getcwd()
        # differentiate between images & Sounds and json; done
        if multiple_files:
                os.chdir(game_dir)
                for f in os.listdir(game_dir):
                        if not os.path.isdir(game_dir+"/"+f):
                                os.chmod(game_dir + "/" + f, 0o777)
                                os.remove(game_dir+"/"+f)
                        else:
                                pass
                try:
                        os.rmdir(game_dir)
                except:
                        pass
        else:
                os.chdir(game_dir[:game_dir.rfind("/")])
                try:
                        os.remove(game_dir)
                except:
                        pass
        os.chdir(current_dir)

def print_player_name(x, playerName):
        x, y, w, h = button_layout_28[x+7]
        pygame.draw.rect(SCREEN, Static.WHITE, (x,y,w,h))
        pygame.draw.rect(SCREEN, Static.LIGHT_RED, (x,y,w,h), 5)
        pygame.draw.rect(SCREEN, Static.LIGHT_RED, (x-w/4,y-2,w/4,h+3))
        image_file = load_image('user.bmp', '/home/pi/Desktop/venv/mycode/images')
        image_size = image_file.get_rect().size
        rela = image_size[0]/float(image_size[1])
        image_file = pygame.transform.scale(image_file, (int(h/2*rela), int(h/2)))
        SCREEN.blit(image_file, image_file.get_rect(center=pygame.Rect(x-w/4,y,w/4,h).center))
        text_surf, text_rect = text_objects(playerName, SMALL_TEXT, Static.RED)
        text_rect.center = (int(x +w/2), int(y + h/2))
        SCREEN.blit(text_surf, text_rect)
        pygame.display.update()

def players_names_menu_setup():
        show_mouse()
        SCREEN.fill(Static.WHITE)
        """logo = "BuzzingaLogo.bmp"
        picture = load_image(logo, 'images')
        picture_size = picture.get_rect().size
        rela = picture_size[0] / picture_size[0]
        picture = pygame.transform.scale(picture, (int(SCREEN_WIDTH / 5.5), int((SCREEN_WIDTH / 5.5) * rela)))
        SCREEN.blit(picture, picture.get_rect(center=(int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 5))))"""
        text_surf, text_rect = text_objects('W E R  S P I E L T  M I T ?', MEDIUM_TEXT)
        text_rect.center = (int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 4))
        SCREEN.blit(text_surf, text_rect)
        for i, player in enumerate(config['playerNames']):
                print_player_name(i, player)
        pygame.display.update()

def players_names_menu():
        players_names_menu_setup()
        playerNameInputsActive = [False, False, False, False]
        running = True
        while running:
                click = False
                pressed_keys = pygame.key.get_pressed()
                for event in pygame.event.get():
                        alt_f4 = (event.type == KEYDOWN and (
                                        event.key == K_F4 and (pressed_keys[K_LALT] or pressed_keys[K_RALT])))
                        if alt_f4:
                                sys.exit()
                        if event.type == KEYDOWN:
                                if event.key == K_BACKSPACE:
                                        try:
                                                active = [i for i, x in enumerate(playerNameInputsActive) if x == True]
                                                config['playerNames'][active[0]] = config['playerNames'][active[0]][:-1]
                                                print_player_name(active[0], config['playerNames'][active[0]])
                                        except:
                                                pass
                                else:
                                        try:
                                                active = [i for i, x in enumerate(playerNameInputsActive) if x == True]
                                                config['playerNames'][active[0]] += event.unicode
                                                print_player_name(active[0], config['playerNames'][active[0]])
                                        except:
                                                pass
                        elif event.type == MOUSEBUTTONDOWN:
                                click = True
                x1, y1, w1, h1 = button_layout_28[7]
                x2, y2, w2, h2 = button_layout_28[8]
                x3, y3, w3, h3 = button_layout_28[9]
                x4, y4, w4, h4 = button_layout_28[10]
                x11, y11, w11, h11 = button_layout_28[17]

                if player_name_input(x1, y1, w1, h1, click):
                        playerNameInputsActive = [True, False, False, False]
                        active = [i for i, x in enumerate(playerNameInputsActive) if x == True]
                        config['playerNames'][active[0]] = ''
                        print_player_name(active[0], config['playerNames'][active[0]])
                elif player_name_input(x2, y2, w2, h2, click):
                        playerNameInputsActive = [False, True, False, False]
                        active = [i for i, x in enumerate(playerNameInputsActive) if x == True]
                        config['playerNames'][active[0]] = ''
                        print_player_name(active[0], config['playerNames'][active[0]])
                elif player_name_input(x3, y3, w3, h3, click):
                        playerNameInputsActive = [False, False, True, False]
                        active = [i for i, x in enumerate(playerNameInputsActive) if x == True]
                        config['playerNames'][active[0]] = ''
                        print_player_name(active[0], config['playerNames'][active[0]])
                elif player_name_input(x4, y4, w4, h4, click):
                        playerNameInputsActive = [False, False, False, True]
                        active = [i for i, x in enumerate(playerNameInputsActive) if x == True]
                        config['playerNames'][active[0]] = ''
                        print_player_name(active[0], config['playerNames'][active[0]])
                elif button(u'Spiel wählen', x11, y11, w11, h11, click):
                        choose_game_menu()
                pygame.display.update(button_layout_28)
                clock.tick(100)

def choose_game_menu_setup():
        show_mouse()
        SCREEN.fill(Static.WHITE)
        text_surf, text_rect = text_objects('W E L C H E  S P I E L A R T ?', MEDIUM_TEXT)
        text_rect.center = (int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 4))
        SCREEN.blit(text_surf, text_rect)
        pygame.display.update()

def choose_game_menu():
        choose_game_menu_setup()
        choose_game_menu_running = True
        while choose_game_menu_running:
                click = False
                for event in pygame.event.get():
                        alt_f4 = (event.type == KEYDOWN and (
                                        event.key == K_F4 and (pressed_keys[K_LALT] or pressed_keys[K_RALT])))
                        if alt_f4:
                                sys.exit()
                        if event.type == MOUSEBUTTONDOWN:
                                click = True

                x2, y2, w2, h2 = button_layout_28[7]
                x8, y8, w8, h8 = button_layout_28[8]
                x9, y9, w9, h9 = button_layout_28[9]
                x7, y7, w7, h7 = button_layout_28[17]

                if button(u'Bilder', x2, y2, w2, h2, click):
                        config['game_type'] = "images"
                        choose_category()
                elif button(u'Sounds', x8, y8, w8, h8, click):
                        config['game_type'] = "sounds"
                        choose_category()
                elif button(u'Multiple Choice Quiz', x9, y9, w9, h9, click):
                        config['game_type'] = "questions"
                        choose_category()
                elif button(u'Zurück', x7, y7, w7, h7, click):
                        choose_game_menu_running = False
                        players_names_menu()
                pygame.display.update()
                clock.tick(100)


def choose_category_setup(import_status="", no_categories=False):
        SCREEN.fill(Static.WHITE)
        text_surf, text_rect = text_objects('S P I E L K A T E G O R I E', MEDIUM_TEXT)
        text_rect.center = (int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 4))
        SCREEN.blit(text_surf, text_rect)
        free_space = get_free_disk_space()
        text_surf, text_rect = text_objects(free_space + ' % freier Speicherplatz', SMALL_TEXT)
        text_rect.center = (int(SCREEN_WIDTH / 15 * 13), int(SCREEN_HEIGHT / 18 * 17))
        SCREEN.blit(text_surf, text_rect)
        text_surf, text_rect = text_objects(import_status[:-1], SMALL_TEXT)
        text_rect.center = (int(SCREEN_WIDTH / 8), int(SCREEN_HEIGHT / 18 * 17))
        SCREEN.blit(text_surf, text_rect)
        if no_categories == True:
                text_surf, text_rect = text_objects('Keine Kategorien vorhanden!', SMALL_TEXT)
                x, y, w, h = button_layout_28[7]
                text_rect.center = (int(x + w / 2), int(y + h / 2))
                SCREEN.blit(text_surf, text_rect)
        pygame.display.update()

global delete_modus
delete_modus = False

def choose_category(import_status=""):
        def build_category_buttons_dict():
                global game_folder
                if config['game_type'] == "images":
                        game_folder = "/home/pi/Desktop/SdR/Bilder/"
                elif config['game_type'] == "sounds":
                        game_folder = "/home/pi/Desktop/SdR/Audio/"
                else:
                        game_folder = "/home/pi/Desktop/SdR/Questions/"
                global pages
                pages = (len(os.listdir(game_folder)) // 26) + 1
                global buttons
                buttons = {}
                for page in range(pages):
                        buttons['page ' + str(page + 1)] = []
                game_nr = 1
                page_nr = 1
                for item in os.listdir(game_folder):
                        x, y, w, h = button_layout_28[int(game_nr - 1)]
                        if item.lower().endswith('.json'):
                                if item.lower().startswith('.'):
                                        continue
                                else:
                                        buttons['page ' + str(page_nr)].append([os.path.splitext(item)[0], x, y, w, h])
                        else:
                                buttons['page ' + str(page_nr)].append([item, x, y, w, h])
                        game_nr += 1
                        if game_nr == 26:
                                game_nr = 1
                                page_nr += 1
                return pages, buttons, game_folder

        global delete_modus
        build_category_buttons_dict()
        if len(buttons['page 1']) == 0:
                choose_category_setup(import_status=import_status, no_categories=True)
        else:
                choose_category_setup(import_status=import_status, no_categories=False)
        choose_category_menu = True
        game_options = []
        page_counter = 1
        while choose_category_menu:
                click = False
                for event in pygame.event.get():
                        alt_f4 = (event.type == KEYDOWN and (
                                event.key == K_F4 and (pressed_keys[K_LALT] or pressed_keys[K_RALT])))
                        if alt_f4:
                                sys.exit()
                        if event.type == KEYDOWN:
                                if event.key == K_ESCAPE:
                                        delete_modus = False
                                        choose_game_menu_running = False
                        elif event.type == MOUSEBUTTONDOWN:
                                click = True
                if page_counter <= pages:
                        for game in buttons['page ' + str(page_counter)]:
                                game_options.append(
                                        [game[0], button(game[0], game[1], game[2], game[3], game[4], click), game[1],
                                         game[2], game[3], game[4]])
                if page_counter < pages:
                        x, y, w, h = button_layout_28[27]
                        if button('>>', x, y, w, h, click, inactive_color=Static.ORANGE):
                                delete_modus = False
                                choose_category_setup()
                                game_options = []
                                page_counter += 1
                                for game in buttons['page ' + str(page_counter)]:
                                        game_options.append(
                                                [game[0], button(game[0], game[1], game[2], game[3], game[4], click),
                                                 game[1], game[2], game[3], game[4]])
                x, y, w, h = button_layout_28[25]
                if delete_modus == False:
                        if button('delete.bmp', x, y, w / 3, h, click, inactive_color=Static.ORANGE, image=True):
                                categories_to_delete = []
                                delete_modus = True
                else:
                        if button('delete.bmp', x, y, w / 3, h, click, inactive_color=Static.LIGHT_RED, image=True):
                                for game_option in game_options:
                                        game_option[1] = False
                                delete_modus = False
                if button('trash-truck.bmp', x + w / 3, y, w / 3, h, click, inactive_color=Static.ORANGE, image=True):
                        if 'categories_to_delete' in locals():
                                # differentiate between images & Sounds and json; done
                                for category in categories_to_delete:
                                        if config['game_type'] in ["images", "sounds"]:
                                                delete_category(game_folder + category, multiple_files=True)
                                        else:
                                                delete_category(game_folder + category, multiple_files=False)
                        categories_to_delete = []
                        delete_modus = False
                        choose_category_menu = False #test
                        choose_category()
                if button('flash-drive.bmp', x + (w / 3) * 2, y, w / 3, h, click, inactive_color=Static.ORANGE,
                          image=True):
                        text_surf, text_rect = text_objects('Importiere Dateien', SMALL_TEXT)
                        text_rect.center = (int(SCREEN_WIDTH / 11), int(SCREEN_HEIGHT / 18 * 17))
                        pygame.draw.rect(SCREEN, Static.WHITE,
                                         (text_rect[0], text_rect[1], text_rect[2] + SCREEN_WIDTH / 3, text_rect[3]), 0)
                        SCREEN.blit(text_surf, text_rect)
                        pygame.display.update()
                        usb_input = subprocess.check_output("python3 check_usb_input.py".split())
                        choose_category_menu = False
                        choose_category(import_status=usb_input)
                        click = False
                x, y, w, h = button_layout_28[26]
                if button(u'Zurück', x, y, w, h, click, inactive_color=Static.ORANGE):
                        delete_modus = False
                        choose_category_menu = False
                        choose_game_menu()
                for game_option in game_options:
                        if game_option[1] == True:
                                if delete_modus == False:
                                        # category has been chosen and settings menu opens
                                        config['game choosen'] = True
                                        # differentiate between images & Sounds and json; done
                                        if config['game_type'] in ["images", "sounds"]:
                                                config['game dir'] = game_folder + game_option[0] + "/"
                                        else:
                                                config['game dir'] = game_folder + game_option[0] + ".json"
                                        settings_menu()
                                else:
                                        # categories to selected are deleted
                                        pygame.draw.rect(SCREEN, Static.ORANGE, (
                                        game_option[2], game_option[3], game_option[4], game_option[5]))
                                        text_surf, text_rect = text_objects(game_option[0], SMALL_TEXT,
                                                                            color=Static.WHITE)
                                        text_rect.center = (int(game_option[2] + game_option[4] / 2),
                                                            int(game_option[3] + game_option[5] / 2))
                                        SCREEN.blit(text_surf, text_rect)
                                        if game_option[0] not in categories_to_delete:
                                                # differentiate between images & Sounds and json
                                                if config['game_type'] in ["images", "sounds"]:
                                                        categories_to_delete.append(game_option[0])
                                                else:
                                                        categories_to_delete.append(game_option[0]+".json")
                pygame.display.update()
                clock.tick(100)

def settings_menu_setup():
        SCREEN.fill(Static.WHITE)
        text_surf, text_rect = text_objects('E I N S T E L L U N G E N', MEDIUM_TEXT)
        text_rect.center = (int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 4))
        SCREEN.blit(text_surf, text_rect)
        x, y, w, h = button_layout_28[7]
        pygame.draw.rect(SCREEN, Static.LIGHT_RED, (x,y,w,h))
        text_surf, text_rect = text_objects('S O U N D S', SMALL_TEXT, Static.WHITE)
        text_rect.center = (int(x +w/2), int(y + h/2))
        SCREEN.blit(text_surf, text_rect)
        x7, y7, w7, h7 = button_layout_28[14]
        pygame.draw.rect(SCREEN, Static.LIGHT_RED, (x7,y7,w7,h7))
        text_surf, text_rect = text_objects('M O D U S', SMALL_TEXT, Static.WHITE)
        text_rect.center = (int(x7 +w7/2), int(y7 + h7/2))
        SCREEN.blit(text_surf, text_rect)
        pygame.display.update()

def settings_menu():
        def no_buzzer_connected():
                text_surf, text_rect = text_objects('Kein Buzzer verbunden!', SMALL_TEXT)
                text_rect.center = (int(SCREEN_WIDTH / 11), int(SCREEN_HEIGHT / 18*17))
                pygame.draw.rect(SCREEN, Static.WHITE, (text_rect[0], text_rect[1], text_rect[2]+SCREEN_WIDTH/3, text_rect[3]), 0)
                SCREEN.blit(text_surf, text_rect)
                pygame.display.update()

        settings_menu_setup()
        settings_menu_running = True
        start_game = False#view_choose_game =
        while settings_menu_running:
                click = False
                for event in pygame.event.get():
                        alt_f4 = (event.type == KEYDOWN and (
                                event.key == K_F4 and (pressed_keys[K_LALT] or pressed_keys[K_RALT])))
                        if alt_f4:
                                sys.exit()
                        if event.type == KEYDOWN:
                                if event.key == K_ESCAPE:
                                        settings_menu_running = False
                        if event.type == MOUSEBUTTONDOWN:
                                click = True

                x2, y2, w2, h2 = button_layout_28[8]
                x8, y8, w8, h8 = button_layout_28[15]
                x9, y9, w9, h9 = button_layout_28[16]
                x10, y10, w10, h10 = button_layout_28[17]
                x7, y7, w7, h7 = button_layout_28[18]
                
                if toggle_btn('Aus', 'Ein', x2, y2, w2, h2, click, enabled=config['game sounds']):
                        config['game sounds'] = not config['game sounds']
                        draw_bg_toggle = True
                if toggle_btn('Punkte', 'Alle Dateien', x8, y8, w8, h8, click, enabled=config['game modus']):
                        config['game modus'] = not config['game modus']
                        draw_bg_toggle = True
                if config['game modus'] == False:
                        pygame.draw.rect(SCREEN, Static.LIGHT_RED, (x9,y9,w9/2,h9))
                        text_surf, text_rect = text_objects(str(config['points_to_win']), SMALL_TEXT, Static.WHITE)
                        text_rect.center = (int(x9 +w9/4), int(y9 + h9/2))
                        SCREEN.blit(text_surf, text_rect)
                        if button('+', x9+w9/2, y9, w9/2, h9/2, click):
                                config['points_to_win'] += 1
                                pygame.draw.rect(SCREEN, Static.LIGHT_RED, (x9,y9,w9/2,h9))
                                text_surf, text_rect = text_objects(str(config['points_to_win']), SMALL_TEXT, Static.WHITE)
                                text_rect.center = (int(x9 +w9/4), int(y9 + h9/2))
                                SCREEN.blit(text_surf, text_rect)
                        if button('-', x9+w9/2, y9+h9/2, w9/2, h9/2, click):
                                if config['points_to_win'] != 1:
                                        config['points_to_win'] -= 1
                                        pygame.draw.rect(SCREEN, Static.LIGHT_RED, (x9,y9,w9/2,h9))
                                        text_surf, text_rect = text_objects(str(config['points_to_win']), SMALL_TEXT, Static.WHITE)
                                        text_rect.center = (int(x9 +w9/4), int(y9 + h9/2))
                                        SCREEN.blit(text_surf, text_rect)
                if config['game modus'] == True:
                        pygame.draw.rect(SCREEN, Static.WHITE, (x9,y9,w9,h9))
                if button(u'Spiel starten', x10, y10, w10, h10, click):
                        try:
                                pygame.joystick.quit()
                                pygame.joystick.init()
                                if pygame.joystick.get_count() == 1:
                                        js = pygame.joystick.Joystick(0)
                                        js.init()
                                        start_game = True
                                else:
                                        no_buzzer_connected()
                        except:
                                no_buzzer_connected()
                elif button(u'Zurück', x7, y7, w7, h7, click):
                        settings_menu_running = False
                        choose_category(import_status="")
                if start_game:
                        while start_game:
                                start_game = game(SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT)
                                settings_menu_running = False
                                players_names_menu()
                pygame.display.update()
                clock.tick(100)


if __name__ == "__main__":
        # create folders for images, sounds and questions on raspberry
        required_folders = [b"Bilder/", b"Audio/", b"Questions/"]
        for f in required_folders:
                if not os.path.exists(b'/home/pi/Desktop/SdR/' + f):
                        dir_name = b'/home/pi/Desktop/SdR/' + f
                        os.mkdir(dir_name.decode('utf-8'))

        pygame.init()

        SCREEN_WIDTH, SCREEN_HEIGHT = int(pygame.display.Info().current_w), int(pygame.display.Info().current_h)
        SCREEN=pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), FULLSCREEN)

        BUTTON_WIDTH = int(SCREEN_WIDTH * 0.625 // 3)
        BUTTON_HEIGHT = int(SCREEN_HEIGHT * 5 // 81)
        button_x_start1 = ((SCREEN_WIDTH - 2*BUTTON_WIDTH) // 2) - (SCREEN_WIDTH/100*2)
        button_x_start2 = button_x_start1 + BUTTON_WIDTH + SCREEN_WIDTH/100*4
        button_x_start3 = button_x_start2 + BUTTON_WIDTH + SCREEN_WIDTH/100*4
        button_x_start0 = button_x_start1 - BUTTON_WIDTH - SCREEN_WIDTH/100*4
        button_layout_28 = [(button_x_start0, SCREEN_HEIGHT * 5 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start0, SCREEN_HEIGHT * 6 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start0, SCREEN_HEIGHT * 7 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start0, SCREEN_HEIGHT * 8 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start0, SCREEN_HEIGHT * 9 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start0, SCREEN_HEIGHT * 10 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start0, SCREEN_HEIGHT * 11 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start1, SCREEN_HEIGHT * 5 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start1, SCREEN_HEIGHT * 6 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start1, SCREEN_HEIGHT * 7 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start1, SCREEN_HEIGHT * 8 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start1, SCREEN_HEIGHT * 9 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start1, SCREEN_HEIGHT * 10 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start1, SCREEN_HEIGHT * 11 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start2, SCREEN_HEIGHT * 5 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start2, SCREEN_HEIGHT * 6 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start2, SCREEN_HEIGHT * 7 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start2, SCREEN_HEIGHT * 8 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start2, SCREEN_HEIGHT * 9 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start2, SCREEN_HEIGHT * 10 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start2, SCREEN_HEIGHT * 11 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start3, SCREEN_HEIGHT * 5 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start3, SCREEN_HEIGHT * 6 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start3, SCREEN_HEIGHT * 7 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start3, SCREEN_HEIGHT * 8 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start3, SCREEN_HEIGHT * 9 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start3, SCREEN_HEIGHT * 10 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                           (button_x_start3, SCREEN_HEIGHT * 11 // 13, BUTTON_WIDTH, BUTTON_HEIGHT)]
        TOGGLE_ADJ = int(BUTTON_WIDTH * 0.075)
        MENU_TEXT = pygame.font.SysFont("Ariel", int(SCREEN_HEIGHT / 5))
        MEDIUM_TEXT = pygame.font.SysFont("Ariel", int(SCREEN_HEIGHT / 9))
        SMALL_TEXT = pygame.font.SysFont("Ariel", int(SCREEN_HEIGHT / 25))

        pygame.display.set_caption('BUZZINGA')
        clock = pygame.time.Clock()

        players_names_menu()
