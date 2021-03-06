# -*- coding: utf-8 -*-

import os, pygame, sys
import subprocess
from game_utilities import load_image
from pygame.locals import *
from pygame import gfxdraw, KEYDOWN, MOUSEBUTTONDOWN, K_ESCAPE, K_RETURN, K_BACKSPACE
from BuzzerGame import buzzer_game
from static import Static

config = {'images': True,
          'playerNames': ['Spieler 1', 'Spieler 2', 'Spieler 3', 'Spieler 4'],
          'game dir': '/home/pi/Desktop/SdR/Bilder/Tiere/',
          'game choosen': False,
          'game sounds': True,
          'game modus': True,
          'points_to_win': 10}

def game(screen, screenx, screeny):
        buzzer_game(4, config['playerNames'], config['game dir'], screen, screenx, screeny, config['images'], config['game sounds'], config['game modus'], config['points_to_win'])
	
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
                image_file = pygame.transform.scale(image_file, (int(h/2*rela), h/2))
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
                pygame.draw.rect(SCREEN, enabled_color, (x + text_rect.width + SCREEN_WIDTH/50, y + h/4, TOGGLE_ADJ, rect_height))
                draw_circle(SCREEN, int(x + text_rect.width + SCREEN_WIDTH/50), y + h/2, h // 4, enabled_color)
                draw_circle(SCREEN, int(x + text_rect.width + SCREEN_WIDTH/50 + h/4 + TOGGLE_ADJ/2), y + h/2, h // 4, enabled_color)
                draw_circle(SCREEN, int(x + text_rect.width + SCREEN_WIDTH/50 + h/4 + TOGGLE_ADJ/2), y + h/2, h // 5, Static.WHITE)
        elif draw_toggle:
                pygame.draw.rect(SCREEN, enabled_color, (x + text_rect.width + SCREEN_WIDTH/50, y + h/4, TOGGLE_ADJ, rect_height))
                draw_circle(SCREEN, int(x + text_rect.width + SCREEN_WIDTH/50), y + h/2, h // 4, enabled_color)
                draw_circle(SCREEN, int(x + text_rect.width + SCREEN_WIDTH/50 + h/4 + TOGGLE_ADJ/2), y + h/2, h // 4, enabled_color)
                draw_circle(SCREEN, int(x + text_rect.width + SCREEN_WIDTH/50), y + h/2, h // 5, Static.WHITE)
        if blit_text:
                text_rect.topleft = (x, int(y + h/4))
                SCREEN.blit(text_surf, text_rect)
                text_surf2, text_rect2 = text_objects(text2, SMALL_TEXT, color=text_color)
                text_rect2.topleft = (x + text_rect.width + SCREEN_WIDTH/25 + h/4 + TOGGLE_ADJ, int(y + h/4))
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

def delete_category(game_dir):
        current_dir = os.getcwd()
        os.chdir(game_dir)
        for f in os.listdir(game_dir):
                if not os.path.isdir(game_dir+"/"+f):
                        os.remove(game_dir+"/"+f)
                else:
                        pass
        try:
                os.rmdir(game_dir)
        except:
                pass
        os.chdir(current_dir)

def print_player_name(x, playerName):
        x, y, w, h = button_layout_28[x+8]
        pygame.draw.rect(SCREEN, Static.WHITE, (x,y,w,h))
        pygame.draw.rect(SCREEN, Static.LIGHT_RED, (x,y,w,h), 5)
        pygame.draw.rect(SCREEN, Static.LIGHT_RED, (x-w/4,y-2,w/4,h+3))
        image_file = load_image('user.bmp', '/home/pi/Desktop/venv/mycode/images')
        image_size = image_file.get_rect().size
        rela = image_size[0]/float(image_size[1])
        image_file = pygame.transform.scale(image_file, (int(h/2*rela), h/2))
        SCREEN.blit(image_file, image_file.get_rect(center=pygame.Rect(x-w/4,y,w/4,h).center))
        text_surf, text_rect = text_objects(playerName, SMALL_TEXT, Static.RED)
        text_rect.center = (int(x +w/2), int(y + h/2))
        SCREEN.blit(text_surf, text_rect)
        pygame.display.update()

def choose_game_setup(import_status="", no_categories=False):
        SCREEN.fill(Static.WHITE)
        text_surf, text_rect = text_objects('S P I E L K A T E G O R I E', MEDIUM_TEXT)
        text_rect.center = (int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 4))
        SCREEN.blit(text_surf, text_rect)
        free_space = get_free_disk_space()
        text_surf, text_rect = text_objects(free_space+' % freier Speicherplatz', SMALL_TEXT)
        text_rect.center = (int(SCREEN_WIDTH / 15*13), int(SCREEN_HEIGHT / 18*17))
        SCREEN.blit(text_surf, text_rect)
        text_surf, text_rect = text_objects(import_status[:-1], SMALL_TEXT)
        text_rect.center = (int(SCREEN_WIDTH / 8), int(SCREEN_HEIGHT / 18*17))
        SCREEN.blit(text_surf, text_rect)
        if no_categories == True:
                text_surf, text_rect = text_objects('Keine Kategorien vorhanden!', SMALL_TEXT)
                x, y, w, h = button_layout_28[7]
                text_rect.center = (int(x+w/2), int(y+h/2))
                SCREEN.blit(text_surf, text_rect)
        pygame.display.update()

global delete_modus
delete_modus = False

def choose_game(import_status=""):
        
        def build_category_buttons_dict():
                global game_folder
                if config['images'] == True:
                        game_folder = "/home/pi/Desktop/SdR/Bilder/"               
                else:
                        game_folder = "/home/pi/Desktop/SdR/Audio/"
                global pages
                pages = (len(os.listdir(game_folder)) // 26) + 1
                global buttons
                buttons = {}
                for page in range(pages):
                        buttons['page '+str(page+1)] = []
                game_nr = 1
                page_nr = 1
                for folder in os.listdir(game_folder):
                        x, y, w, h = button_layout_28[int(game_nr-1)]
                        buttons['page '+str(page_nr)].append([unicode(folder, "utf-8"), x, y, w, h])
                        game_nr += 1
                        if game_nr == 26:
                                game_nr = 1
                                page_nr += 1
                return pages, buttons, game_folder

        global delete_modus
        build_category_buttons_dict()
        if len(buttons['page 1']) == 0:
                choose_game_setup(import_status=import_status, no_categories=True)
        else:
                choose_game_setup(import_status=import_status, no_categories=False)
        choose_game_menu = True
        game_options = []
        page_counter = 1
        while choose_game_menu:
                click = False
                for event in pygame.event.get():
                        if event.type == KEYDOWN:
                                if event.key == K_ESCAPE:
                                        delete_modus = False
                                        choose_game_menu = False
                        elif event.type == MOUSEBUTTONDOWN:
                                click = True
                if page_counter <= pages:
                        for game in buttons['page '+str(page_counter)]:
                                game_options.append([game[0], button(game[0], game[1], game[2], game[3], game[4], click), game[1], game[2], game[3], game[4]])
                if page_counter < pages:
                        x, y, w, h = button_layout_28[27]
                        if button('>>', x, y, w, h, click, inactive_color=Static.ORANGE):
                                delete_modus = False
                                choose_game_setup()
                                game_options = []
                                page_counter += 1
                                for game in buttons['page '+str(page_counter)]:
                                        game_options.append([game[0], button(game[0], game[1], game[2], game[3], game[4], click), game[1], game[2], game[3], game[4]])       
                x, y, w, h = button_layout_28[25]
                if delete_modus == False:
                        if button('delete.bmp', x, y, w/3, h, click, inactive_color=Static.ORANGE, image=True):
                                categories_to_delete = []
                                delete_modus = True
                else:
                        if button('delete.bmp', x, y, w/3, h, click, inactive_color=Static.LIGHT_RED, image=True):
                                for game_option in game_options:
                                        game_option[1] = False
                                delete_modus = False
                if button('trash-truck.bmp', x+w/3, y, w/3, h, click, inactive_color=Static.ORANGE, image=True):
                        if 'categories_to_delete' in locals():
                                for category in categories_to_delete:
                                        delete_category(game_folder+category)
                        categories_to_delete = []
                        delete_modus = False
                        choose_game()
                if button('flash-drive.bmp', x+(w/3)*2, y, w/3, h, click, inactive_color=Static.ORANGE, image=True):
                        text_surf, text_rect = text_objects('Importiere Dateien', SMALL_TEXT)
                        text_rect.center = (int(SCREEN_WIDTH / 11), int(SCREEN_HEIGHT / 18*17))
                        pygame.draw.rect(SCREEN, Static.WHITE, (text_rect[0], text_rect[1], text_rect[2]+SCREEN_WIDTH/3, text_rect[3]), 0)
                        SCREEN.blit(text_surf, text_rect)
                        pygame.display.update()
                        usb_input = subprocess.check_output("python3 check_usb_input.py".split())
                        choose_game(import_status=usb_input)
                        click=False
                x, y, w, h = button_layout_28[26]
                if button(u'Hauptmenü', x, y, w, h, click, inactive_color=Static.ORANGE):
                        delete_modus = False
                        choose_game_menu = False
                for game_option in game_options:
                        if game_option[1] == True:
                                if delete_modus == False:
                                        config['game choosen'] = True
                                        config['game dir'] = game_folder+game_option[0]+"/"
                                        choose_game_menu = False
                                else:
                                        pygame.draw.rect(SCREEN, Static.ORANGE, (game_option[2], game_option[3], game_option[4], game_option[5]))
                                        text_surf, text_rect = text_objects(game_option[0], SMALL_TEXT, color=Static.WHITE)
                                        text_rect.center = (int(game_option[2] +game_option[4]/2), int(game_option[3] + game_option[5]/2))
                                        SCREEN.blit(text_surf, text_rect)
                                        if game_option[0] not in categories_to_delete:
                                                categories_to_delete.append(game_option[0])
                pygame.display.update(button_layout_28)
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
        settings_menu_setup()
        settings_menu = True
        while settings_menu:
                click = False
                for event in pygame.event.get():
                        if event.type == MOUSEBUTTONDOWN:
                                click = True
                x2, y2, w2, h2 = button_layout_28[8]
                x8, y8, w8, h8 = button_layout_28[15]
                x9, y9, w9, h9 = button_layout_28[16]
                x10, y10, w10, h10 = button_layout_28[17]
                
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
                if button(u'Hauptmenü', x10, y10, w10, h10, click):
                        settings_menu = False
                pygame.display.update(button_layout_28)
                clock.tick(100)

def main_menu_setup():
        show_mouse()
        SCREEN.fill(Static.WHITE)
        logo = "BuzzingaLogo.bmp"
        picture = load_image(logo, 'images')
        picture_size = picture.get_rect().size
        rela = picture_size[0]/picture_size[0]
        picture = pygame.transform.scale(picture, (int(SCREEN_WIDTH / 5.5), int((SCREEN_WIDTH / 5.5)*rela)))
        SCREEN.blit(picture, picture.get_rect(center=(int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 5))))
        x, y, w, h = button_layout_28[7]
        pygame.draw.rect(SCREEN, Static.LIGHT_RED, (x,y,w,h))
        text_surf, text_rect = text_objects('S P I E L E R', SMALL_TEXT, Static.WHITE)
        text_rect.center = (int(x +w/2), int(y + h/2))
        SCREEN.blit(text_surf, text_rect)
        for i,player in enumerate(config['playerNames']):
                print_player_name(i, player)
        x, y, w, h = button_layout_28[14]
        pygame.draw.rect(SCREEN, Static.LIGHT_RED, (x,y,w,h))
        text_surf, text_rect = text_objects('S P I E L', SMALL_TEXT, Static.WHITE)
        text_rect.center = (int(x +w/2), int(y + h/2))
        SCREEN.blit(text_surf, text_rect)
        pygame.display.update()

def main_menu():
        def no_buzzer_connected():
                text_surf, text_rect = text_objects('Kein Buzzer verbunden!', SMALL_TEXT)
                text_rect.center = (int(SCREEN_WIDTH / 11), int(SCREEN_HEIGHT / 18*17))
                pygame.draw.rect(SCREEN, Static.WHITE, (text_rect[0], text_rect[1], text_rect[2]+SCREEN_WIDTH/3, text_rect[3]), 0)
                SCREEN.blit(text_surf, text_rect)
                pygame.display.update()

        main_menu_setup()
        start_game = view_choose_game = False
        playerNameInputsActive = [False, False, False, False]
        while True:
                click = False
                for event in pygame.event.get():
                        alt_f4 = (event.type == KEYDOWN and (event.key == K_F4 and (pressed_keys[K_LALT] or pressed_keys[K_RALT])))
                        if alt_f4:
                                sys.exit()
                        if event.type == KEYDOWN:
                                #if event.key == K_ESCAPE:
                                #        sys.exit()
                                if event.key == K_BACKSPACE:
                                        try:
                                                active = [i for i, x in enumerate(playerNameInputsActive) if x==True]
                                                config['playerNames'][active[0]] = config['playerNames'][active[0]][:-1]
                                                print_player_name(active[0], config['playerNames'][active[0]])
                                        except:
                                                pass
                                else:
                                        try:
                                                active = [i for i, x in enumerate(playerNameInputsActive) if x==True]
                                                config['playerNames'][active[0]] += event.unicode
                                                print_player_name(active[0], config['playerNames'][active[0]])
                                        except:
                                                pass
                        elif event.type == MOUSEBUTTONDOWN:
                                click = True
                x1, y1, w1, h1 = button_layout_28[8]
                x2, y2, w2, h2 = button_layout_28[9]
                x3, y3, w3, h3 = button_layout_28[10]
                x4, y4, w4, h4 = button_layout_28[11]
                x8, y8, w8, h8 = button_layout_28[15]
                x9, y9, w9, h9 = button_layout_28[16]
                x10, y10, w10, h10 = button_layout_28[17]
                x11, y11, w11, h11 = button_layout_28[18]
                
                if player_name_input(x1, y1, w1, h1, click):
                        playerNameInputsActive = [True, False, False, False]
                        active = [i for i, x in enumerate(playerNameInputsActive) if x==True]
                        config['playerNames'][active[0]] = ''
                        print_player_name(active[0], config['playerNames'][active[0]])
                elif player_name_input(x2, y2, w2, h2, click):
                        playerNameInputsActive = [False, True, False, False]
                        active = [i for i, x in enumerate(playerNameInputsActive) if x==True]
                        config['playerNames'][active[0]] = ''
                        print_player_name(active[0], config['playerNames'][active[0]])
                elif player_name_input(x3, y3, w3, h3, click):
                        playerNameInputsActive = [False, False, True, False]
                        active = [i for i, x in enumerate(playerNameInputsActive) if x==True]
                        config['playerNames'][active[0]] = ''
                        print_player_name(active[0], config['playerNames'][active[0]])
                elif player_name_input(x4, y4, w4, h4, click):
                        playerNameInputsActive = [False, False, False, True]
                        active = [i for i, x in enumerate(playerNameInputsActive) if x==True]
                        config['playerNames'][active[0]] = ''
                        print_player_name(active[0], config['playerNames'][active[0]])
                elif toggle_btn('Audio', 'Bilder', x8, y8, w8, h8, click, enabled=config['images']):
                        config['images'] = not config['images']
                        draw_bg_toggle = True
                elif button('Kategorie', x9, y9, w9, h9, click):
                        choose_game(import_status="")
                        main_menu_setup()
                elif button('Start', x10, y10, w10, h10, click):
                        if config['game choosen'] == False:
                                choose_game(import_status="")
                                main_menu_setup()
                        else:
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
                elif button('Einstellungen', x11, y11, w11, h11, click):
                        settings_menu()
                        main_menu_setup()
                if start_game:
                        while start_game:
                                start_game = game(SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT)
                                main_menu_setup()
                pygame.display.update(button_layout_28)
                clock.tick(100)
        

if __name__ == "__main__":
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

        main_menu()
