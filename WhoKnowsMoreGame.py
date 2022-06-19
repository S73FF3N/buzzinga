# -*- coding: utf-8 -*-

import os, pygame, random, sys
from game_utilities import load_image
from static import Static
import json


def who_knows_more_game(players, playerNamesList, content_dir, screen, screenx, screeny, game_sounds, game_modus,
                points_to_win):
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    game_sound_channel = pygame.mixer.Channel(0)

    # declare and array for player names and initial score
    playerNames = playerNamesList
    playerScore = [0] * players
    # key definitions
    playerKeys = [0, 5, 10, 15]
    answer = [pygame.K_r, pygame.K_f]

    # Set the fonts for the textf
    myfont = pygame.font.SysFont("Ariel", 50)
    scorefont = pygame.font.SysFont("Ariel", 100)

    # defining the container for the graphical elements
    game_label_container_width = screenx / 10 * 9
    game_label_container_height = screeny / 10
    game_label_container = pygame.Rect(0, 0, game_label_container_width, game_label_container_height)
    picture_container_width = game_label_container_width
    picture_container_height = screeny / 10 * 9
    picture_container = pygame.Rect(0, game_label_container_height, picture_container_width, picture_container_height)
    answer_container_width = (game_label_container_width / 3) - 5
    answer_container_height = (picture_container_height / 7) - 2

    picture_counter_container_width = screenx / 10
    picture_counter_container_height = screeny / 10
    picture_counter_container = pygame.Rect(game_label_container_width, 0, picture_counter_container_width,
                                            picture_counter_container_height)
    countdown_container_width = picture_counter_container_width
    countdown_container_height = screeny / 10
    countdown_container = pygame.Rect(picture_container_width,
                                      (game_label_container_height + picture_container_height),
                                      countdown_container_width, countdown_container_height)
    player_container_width = picture_counter_container_width
    player_container_height = screeny / 10 * 2
    player_label_container_width = player_container_width
    player_label_container_height = player_container_height / 10 * 3
    player_buzzer_container_width = player_container_width / 2
    player_buzzer_container_height = player_container_height / 10 * 7
    player_score_container_width = player_container_width / 2
    player_score_container_height = player_container_height / 10 * 7

    # text displayed at the beginning
    head, tail = os.path.split(content_dir)
    game_name = tail[:-5].replace('_', ' ')

    logo = "BuzzingaLogo.bmp"
    picture = load_image(logo, 'images')

    content_dict = {}
    with open(content_dir) as json_file:
        data = json.load(json_file)
    for q in data:
        solution_link = "5/" + str(q["id"])
        content_dict[q["fields"]["solution"]] = {'solution_link': solution_link, 'answers':{}}
        for a in q["fields"]["answers"]:
            content_dict[q["fields"]["solution"]]["answers"][a["fields"]["count_id"]] = a["fields"]["answer"]

    # loading info
    loading = myfont.render("loading...", 1, Static.RED)
    screen.fill(Static.WHITE)
    screen.blit(loading, loading.get_rect(center=picture_container.center))
    pygame.display.flip()

    amount_of_content = len(content_dict)

    winner_found = False
    hint_n = 1

    # randomly chosing content from content dictionary and updating solution label
    def random_pick_content():
        global random_key
        global random_val
        global winner_found
        winner_found = False
        try:
            random_key = random.choice(list(content_dict.keys()))
            random_val = content_dict[random_key]
            if len(random_val["answers"]):
                answer_container_width = (game_label_container_width / 6) - 5
                answer_container_height = (picture_container_height / 10) - 2
            del content_dict[random_key]
        except:
            winner_found = True
        if not winner_found:
            pygame.draw.rect(screen, Static.WHITE, picture_container)
            screen.blit(progress, progress.get_rect(center=picture_counter_container.center))
        else:
            show_winner()
        return random_key, random_val, winner_found

    def show_winner():
        pygame.draw.rect(screen, Static.WHITE, picture_container)
        pygame.draw.rect(screen, Static.WHITE, picture_counter_container)
        winner_ix = [i for i, x in enumerate(playerScore) if x == max(playerScore)]
        winners = [scorefont.render("Gewinner:", 1, Static.RED)]
        [winners.append(scorefont.render(playerNames[i], 1, Static.RED)) for i in winner_ix]
        scorefont_width, scorefont_height = scorefont.size("Test")
        for line in range(len(winners)):
            screen.blit(winners[line], (0 + picture_container_width / 3,
                                        game_label_container_height + picture_container_height / 4 + (
                                                    line * scorefont_height) + (15 * line)))

    # countdown printed in solution label
    def countdown(count_from):
        for i in range(1, count_from):
            time_left = count_from - i
            time_left = str(time_left)
            countdown = myfont.render(time_left, 1, Static.RED)
            screen.blit(countdown, countdown.get_rect(center=countdown_container.center))
            pygame.display.flip()
            pygame.time.wait(1000)
            if time_left != 0:
                pygame.draw.rect(screen, Static.WHITE, countdown_container)
                pygame.display.flip()
        if game_sounds:
            countdown_sound = pygame.mixer.Sound("/home/pi/Desktop/venv/mycode/sounds/wrong-answer.wav")
            game_sound_channel.play(countdown_sound)

    def points_reached():
        global winner_found
        if not game_modus:
            if points_to_win == max(playerScore):
                winner_found = True

    def print_answer(n):
        global random_val
        pygame.draw.rect(screen, Static.BLUE, hint_match_dict[n][0])
        hint1 = myfont.render(random_val[hint_match_dict[n][1]], 1, Static.WHITE)
        screen.blit(hint1, hint1.get_rect(center=hint_match_dict[n][0].center))
        pygame.display.flip()

    screen.fill(Static.WHITE)
    pygame.display.set_caption(game_name)

    # Created Variable for the text on the screen
    game_label = myfont.render(game_name, 1, Static.RED)
    nr = 1
    progress = myfont.render(str(amount_of_content) + " Dateien", 1, Static.RED)
    screen.blit(game_label, game_label.get_rect(center=game_label_container.center))
    screen.blit(progress, progress.get_rect(center=picture_counter_container.center))
    screen.blit(picture, picture.get_rect(center=picture_container.center))

    # Draw name of players, 4 empty rectangles and players score
    for n in range(0, players):
        player_label = myfont.render(playerNames[n], 1, Static.BLACK)
        player_label_container = pygame.Rect(picture_container_width,
                                             (picture_counter_container_height + n * player_container_height),
                                             player_label_container_width, player_label_container_height)
        screen.blit(player_label, player_label.get_rect(center=player_label_container.center))
        player_buzzer_container = pygame.Rect(picture_container_width, (
                    game_label_container_height + player_label_container_height + n * player_container_height),
                                              player_buzzer_container_width, player_buzzer_container_height)
        pygame.draw.rect(screen, Static.BLACK, player_buzzer_container)
        player_score = scorefont.render(str(playerScore[n]), 1, Static.BLACK)
        player_score_container = pygame.Rect((picture_container_width + player_buzzer_container_width), (
                    game_label_container_height + player_label_container_height + n * player_container_height),
                                             player_score_container_width, player_score_container_height)
        screen.blit(player_score, player_score.get_rect(center=player_score_container.center))

    pygame.display.flip()

    no_points = False
    show_solution_var = 1
    initialize = True
    running = True
    break_flag = False
    while running:
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == pygame.KEYDOWN and (
                    event.key == pygame.K_F4 and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT])))
            if alt_f4:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    os.chdir("/home/pi/Desktop/venv/mycode/")
                    break_flag = True
                    break
                if event.key == pygame.K_RETURN and winner_found:
                    show_winner()
                    pygame.display.flip()

        while initialize:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        os.chdir("/home/pi/Desktop/venv/mycode/")
                        break_flag = True
                        break
                    if event.key == pygame.K_RETURN:
                        try:
                            random_pick_content()
                            pygame.display.flip()
                        except Exception as e:
                            os.chdir("/home/pi/Desktop/venv/mycode/")
                            break_flag = True
                            break
                        initialize = False

        while not winner_found and not break_flag:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        os.chdir("/home/pi/Desktop/venv/mycode/")
                        break_flag = True
                        break
                    if event.key == pygame.K_RETURN:
                        no_points = True
                        try:
                            show_solution_var = 1
                            for n in range(0, players):
                                player_buzzer_container = pygame.Rect(picture_container_width, (
                                            game_label_container_height + player_label_container_height + n * player_container_height),
                                                                      player_buzzer_container_width,
                                                                      player_buzzer_container_height)
                                buzzer_blocked = scorefont.render("X", 1, Static.RED)
                                screen.blit(buzzer_blocked,
                                            buzzer_blocked.get_rect(center=player_buzzer_container.center))
                            pygame.display.flip()
                        except:
                            show_solution_var = 2
                    if event.key == pygame.K_n:
                        print_answer(hint_n)
                        if hint_n != 10:
                            hint_n += 1

            # now go to the reset code
        # loop waiting until the 'button' are reset

        while not winner_found and not break_flag:
            for event in pygame.event.get():
                # User pressed down on a key
                if event.type == pygame.KEYDOWN:
                    keypressed = event.key
                    if event.key == pygame.K_ESCAPE:
                        os.chdir("/home/pi/Desktop/venv/mycode/")
                        break_flag = True
                        break
                    # Check if Key Pressed to increase score
                    if not no_points and keypressed in answer:
                        player_score_container = pygame.Rect((picture_container_width + player_buzzer_container_width),
                                                             (
                                                                         game_label_container_height + player_label_container_height + first_buzz * player_container_height),
                                                             player_score_container_width,
                                                             player_score_container_height)
                        pygame.draw.rect(screen, Static.WHITE, player_score_container)
                        if keypressed == answer[0]:
                            playerScore[first_buzz] = playerScore[first_buzz] + 1
                        if keypressed == answer[1]:
                            playerScore[first_buzz] = playerScore[first_buzz] - 1
                            first = False
                        player_score = scorefont.render(str(playerScore[first_buzz]), 1, Static.BLACK)
                        screen.blit(player_score, player_score.get_rect(center=player_score_container.center))
                        pygame.display.flip()
                        if not first:
                            for n in range(0, players):
                                player_buzzer_container = pygame.Rect(picture_container_width, (
                                        game_label_container_height + player_label_container_height + n * player_container_height),
                                                                      player_buzzer_container_width,
                                                                      player_buzzer_container_height)
                                pygame.draw.rect(screen, Static.BLACK, player_buzzer_container)
                            pygame.display.flip()
                            break
                        points_reached()

                    if keypressed == pygame.K_n:
                        print_hint(hint_n)
                        if hint_n != 10:
                            hint_n += 1

                    if keypressed == pygame.K_RETURN and show_solution_var == 2:
                        pygame.draw.rect(screen, Static.WHITE, solution_container)
                        pygame.display.flip()
                        # reset the buzzers to black
                        for n in range(0, players):
                            player_buzzer_container = pygame.Rect(picture_container_width, (
                                        game_label_container_height + player_label_container_height + n * player_container_height),
                                                                  player_buzzer_container_width,
                                                                  player_buzzer_container_height)
                            pygame.draw.rect(screen, Static.BLACK, player_buzzer_container)
                        first = False
                        no_points = False
                        pygame.display.flip()
                        show_solution_var = 0

                    # solution is shown
                    if keypressed == pygame.K_RETURN and show_solution_var == 1:
                        pygame.draw.rect(screen, Static.WHITE, solution_container)
                        show_solution()
                        pygame.display.flip()
                        show_solution_var = 2

                    if keypressed == pygame.K_RETURN and show_solution_var == 0:
                        pygame.draw.rect(screen, Static.WHITE, picture_counter_container)
                        nr += 1
                        progress = myfont.render(str(nr) + "/" + str(amount_of_content), 1, Static.RED)
                        pygame.display.flip()
                        hint_n = 1
                        try:
                            random_pick_content()
                            pygame.display.flip()
                        except:
                            os.chdir("/home/pi/Desktop/venv/mycode/")
                            break_flag = True
                            break
                        show_solution_var = 1
        if break_flag:
            break


if __name__ == "__main__":
    buzzer_game(players, PlayersNameList, content_dir, screen, screenx, screeny, game_type)
