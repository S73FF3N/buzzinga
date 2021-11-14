# -*- coding: utf-8 -*-

import os, pygame, random, sys
#from pygame.locals import *
#from pygame import gfxdraw, KEYDOWN, MOUSEBUTTONDOWN, K_ESCAPE, K_RETURN, K_BACKSPACE, K_F4, K_LALT, K_RALT
from game_utilities import load_image
from static import Static
import json

def multiple_choice_game(players, playerNamesList, content_dir, screen, screenx, screeny, game_type, game_sounds, game_modus,
                points_to_win):
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()

    # declare and array for player names and initial score
    playerNames = playerNamesList
    playerScore = [0] * players
    # key definitions
    player1Keys = [1, 2, 3, 4]
    player2Keys = [6, 7, 8, 9]
    player3Keys = [11, 12, 13, 14]
    player4Keys = [16, 17, 18, 19]

    # Set the fonts for the textf
    myfont = pygame.font.SysFont("Ariel", 50)
    scorefont = pygame.font.SysFont("Ariel", 100)

    # defining the container for the graphical elements
    game_label_container_width = screenx / 10 * 8
    game_label_container_height = screeny / 10
    game_label_container = pygame.Rect(0, 0, game_label_container_width, game_label_container_height)
    picture_container_width = game_label_container_width
    picture_container_height = screeny / 10 * 8
    picture_container = pygame.Rect(0, game_label_container_height, picture_container_width, picture_container_height)
    question_container_width = game_label_container_width
    question_container_height = screeny / 10 * 3
    question_container = pygame.Rect(0, game_label_container_height, question_container_width, question_container_height)
    option_container_width = (game_label_container_width / 2)-10
    option_container_height = (screeny / 10 * 2.5)-10
    option1_container = pygame.Rect(10, game_label_container_height + question_container_height, option_container_width, option_container_height)
    option2_container = pygame.Rect(10+option_container_width, game_label_container_height + question_container_height, option_container_width,
                                    option_container_height)
    option3_container = pygame.Rect(10, game_label_container_height + question_container_height + option_container_height, option_container_width,
                                    option_container_height)
    option4_container = pygame.Rect(10+option_container_width, game_label_container_height + question_container_height + option_container_height, option_container_width,
                                    option_container_height)
    solution_container_width = picture_container_width
    solution_container_height = screeny / 10
    solution_container = pygame.Rect(0, (game_label_container_height + picture_container_height),
                                     solution_container_width, solution_container_height)
    picture_counter_container_width = screenx / 10 * 2
    picture_counter_container_height = screeny / 10
    picture_counter_container = pygame.Rect(game_label_container_width, 0, picture_counter_container_width,
                                            picture_counter_container_height)
    scoreboard_container_width = picture_counter_container_width
    scoreboard_container_height = screeny / 10 * 8
    player_container_width = scoreboard_container_width
    player_container_height = scoreboard_container_height / 4
    player_label_container_width = player_container_width
    player_label_container_height = player_container_height / 10 * 3
    player_buzzer_container_width = player_container_width / 2
    player_buzzer_container_height = player_container_height / 10 * 7
    player_score_container_width = player_container_width / 2
    player_score_container_height = player_container_height / 10 * 7

    # text displayed at the beginning
    head, tail = os.path.split(content_dir)
    game_name = tail[:-5].replace('_', ' ')
    welcome = u"Willkommen zu " + game_name

    logo = "BuzzingaLogo.bmp"
    picture = load_image(logo, 'images')

    content_dict = {}
    with open(content_dir) as json_file:
        data = json.load(json_file)
    for q in data:
        content_dict[q["fields"]["quiz_question"]] = {'solution': q["fields"]["solution"], 'option1': q["fields"]["option1"], 'option2': q["fields"]["option2"], 'option3': q["fields"]["option3"]}

    # loading info
    loading = myfont.render("loading...", 1, Static.RED)
    screen.fill(Static.WHITE)
    screen.blit(loading, loading.get_rect(center=picture_container.center))
    pygame.display.flip()

    amount_of_content = len(content_dict)

    global winner_found
    global player1_locked
    global player2_locked
    global player3_locked
    global player4_locked
    global random_key
    global random_val
    global solution_dict
    global player_answers
    winner_found = player1_locked = player2_locked = player3_locked = player4_locked = False

    # randomly chosing content from content dictionary
    def random_pick_content():
        global winner_found
        global player1_locked
        global player2_locked
        global player3_locked
        global player4_locked
        global random_key
        global random_val
        global solution_dict
        global player_answers
        try:
            random_key = random.choice(list(content_dict.keys()))
            random_val = content_dict[random_key]
            del content_dict[random_key]
        except:
            winner_found = True
        if not winner_found:
            player1_locked = player2_locked = player3_locked = player4_locked = False
            player_answers = {1:False, 2:False, 3:False, 4:False}
            pygame.draw.rect(screen, Static.WHITE, picture_container)
            question = myfont.render(random_key, 1, Static.RED)
            screen.blit(question, question.get_rect(center=question_container.center))
            options = [random_val["option1"], random_val["option2"], random_val["option3"], random_val["solution"]]
            random.shuffle(options)
            solution_dict = {}
            pygame.draw.rect(screen, Static.BLUE, option1_container)
            pygame.draw.rect(screen, Static.RED, option1_container, 10)
            option1 = myfont.render(options[0], 1, Static.RED)
            solution_dict[4] = options[0]
            del options[0]
            pygame.draw.rect(screen, Static.ORANGE, option2_container)
            pygame.draw.rect(screen, Static.RED, option2_container, 10)
            option2 = myfont.render(options[0], 1, Static.RED)
            solution_dict[3] = options[0]
            del options[0]
            pygame.draw.rect(screen, Static.GREEN, option3_container)
            pygame.draw.rect(screen, Static.RED, option3_container, 10)
            option3 = myfont.render(options[0], 1, Static.RED)
            solution_dict[2] = options[0]
            del options[0]
            pygame.draw.rect(screen, Static.YELLOW, option4_container)
            pygame.draw.rect(screen, Static.RED, option4_container, 10)
            option4 = myfont.render(options[0], 1, Static.RED)
            solution_dict[1] = options[0]
            screen.blit(option1, option1.get_rect(center=option1_container.center))
            screen.blit(option2, option2.get_rect(center=option2_container.center))
            screen.blit(option3, option3.get_rect(center=option3_container.center))
            screen.blit(option4, option4.get_rect(center=option4_container.center))
            screen.blit(progress, progress.get_rect(center=picture_counter_container.center))
        else:
            show_winner()
        return random_key, winner_found

    def show_winner():
        pygame.draw.rect(screen, Static.WHITE, picture_container)
        pygame.draw.rect(screen, Static.WHITE, picture_counter_container)
        pygame.draw.rect(screen, Static.WHITE, solution_container)
        winner_ix = [i for i, x in enumerate(playerScore) if x == max(playerScore)]
        winners = [scorefont.render("Gewinner:", 1, Static.RED)]
        [winners.append(scorefont.render(playerNames[i], 1, Static.RED)) for i in winner_ix]
        scorefont_width, scorefont_height = scorefont.size("Test")
        for line in range(len(winners)):
            screen.blit(winners[line], (0 + picture_container_width / 3,
                                        game_label_container_height + picture_container_height / 4 + (
                                                    line * scorefont_height) + (15 * line)))

    # show solution
    def show_solution():
        if solution_dict[4] == random_val["solution"]:
            pygame.draw.rect(screen, Static.LIGHT_GREEN, option1_container, 20)
        elif solution_dict[3] == random_val["solution"]:
            pygame.draw.rect(screen, Static.LIGHT_GREEN, option2_container, 20)
        elif solution_dict[2] == random_val["solution"]:
            pygame.draw.rect(screen, Static.LIGHT_GREEN, option3_container, 20)
        elif solution_dict[1] == random_val["solution"]:
            pygame.draw.rect(screen, Static.LIGHT_GREEN, option4_container, 20)

    def points_reached():
        global winner_found
        if not game_modus:
            if points_to_win == max(playerScore):
                winner_found = True

    screen.fill(Static.WHITE)
    pygame.display.set_caption(game_name)

    # Created Variable for the text on the screen
    game_label = myfont.render(game_name, 1, Static.RED)
    solution_label = myfont.render(welcome, 1, Static.RED)
    nr = 1
    progress = myfont.render(str(amount_of_content) + " Dateien", 1, Static.RED)
    screen.blit(game_label, game_label.get_rect(center=game_label_container.center))
    screen.blit(progress, progress.get_rect(center=picture_counter_container.center))
    screen.blit(picture, picture.get_rect(center=picture_container.center))
    screen.blit(solution_label, solution_label.get_rect(center=solution_container.center))

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

    question_answered = False  # all players have answered the question
    solution_shown = "Waiting"
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
                    running = False
                if event.key == pygame.K_RETURN and winner_found:
                    show_winner()
                    pygame.display.flip()
        while initialize and not break_flag:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        os.chdir("/home/pi/Desktop/venv/mycode/")
                        break_flag = True
                        running = False
                    if event.key == pygame.K_RETURN:
                        pygame.draw.rect(screen, Static.WHITE, picture_container)
                        pygame.display.flip()
                        try:
                            random_pick_content()
                            pygame.display.flip()
                        except Exception as e:
                            break_flag = True
                            running = False
                        initialize = False

        # player provide answer, game coordinator closes question eventually
        while not question_answered and not winner_found and not break_flag:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        os.chdir("/home/pi/Desktop/venv/mycode/")
                        break_flag = True
                        running = False
                    if event.key == pygame.K_RETURN:
                        question_answered = True
                        solution_shown = "Prepared"
                        for n in range(0, players):
                            player_buzzer_container = pygame.Rect(picture_container_width, (
                                        game_label_container_height + player_label_container_height + n * player_container_height),
                                                                  player_buzzer_container_width,
                                                                  player_buzzer_container_height)
                            buzzer_blocked = scorefont.render("X", 1, Static.RED)
                            screen.blit(buzzer_blocked,
                                        buzzer_blocked.get_rect(center=player_buzzer_container.center))
                        pygame.display.flip()

                if event.type == pygame.JOYBUTTONDOWN:
                    buttonpressed = event.button
                    if buttonpressed in player1Keys and not player1_locked:
                        player1_locked = True
                        player_answers[1] = solution_dict[buttonpressed]
                        player_buzzer_container = pygame.Rect(picture_container_width, (
                                    game_label_container_height + player_label_container_height + 0 * player_container_height),
                                                              player_buzzer_container_width,
                                                              player_buzzer_container_height)
                        pygame.draw.rect(screen, Static.RED, player_buzzer_container)
                    elif buttonpressed in player2Keys and not player2_locked:
                        player2_locked = True
                        player_answers[2] = solution_dict[buttonpressed-5]
                        player_buzzer_container = pygame.Rect(picture_container_width, (
                                game_label_container_height + player_label_container_height + 1 * player_container_height),
                                                              player_buzzer_container_width,
                                                              player_buzzer_container_height)
                        pygame.draw.rect(screen, Static.RED, player_buzzer_container)
                    elif buttonpressed in player3Keys and not player3_locked:
                        player3_locked = True
                        player_answers[3] = solution_dict[buttonpressed - 10]
                        player_buzzer_container = pygame.Rect(picture_container_width, (
                                game_label_container_height + player_label_container_height + 2 * player_container_height),
                                                              player_buzzer_container_width,
                                                              player_buzzer_container_height)
                        pygame.draw.rect(screen, Static.RED, player_buzzer_container)
                    elif buttonpressed in player4Keys and not player4_locked:
                        player4_locked = True
                        player_answers[4] = solution_dict[buttonpressed - 15]
                        player_buzzer_container = pygame.Rect(picture_container_width, (
                                game_label_container_height + player_label_container_height + 3 * player_container_height),
                                                              player_buzzer_container_width,
                                                              player_buzzer_container_height)
                        pygame.draw.rect(screen, Static.RED, player_buzzer_container)
                    if player1_locked and player2_locked and player3_locked and player4_locked:
                        solution_shown = "Prepared"
                        question_answered = True
                    pygame.display.flip()

        # all player have given an answer or game coordinator has closed the question
        # points are given by K_RETURN
        while question_answered and not winner_found and not break_flag:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    buttonpressed = event.key
                    if buttonpressed == pygame.K_F4 and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]):
                        sys.exit()
                    if buttonpressed == pygame.K_ESCAPE:
                        os.chdir("/home/pi/Desktop/venv/mycode/")
                        break_flag = True
                        running = False
                    # Show solution
                    if buttonpressed == pygame.K_RETURN and solution_shown == "Prepared":
                        pygame.draw.rect(screen, Static.WHITE, solution_container)
                        show_solution()
                        question_answered = False
                        solution_shown = "Done"
                        pygame.display.flip()

            #solution has been displayed
            while solution_shown == "Done" and not break_flag:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        buttonpressed = event.key
                        if buttonpressed == pygame.K_F4 and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]):
                            sys.exit()
                        if buttonpressed == pygame.K_ESCAPE:
                            os.chdir("/home/pi/Desktop/venv/mycode/")
                            break_flag = True
                            running = False
                    # Check if answer is correct to increase score
                    if buttonpressed == pygame.K_RETURN:
                        for n in range(1, players+1):
                            if player_answers[n] == random_val["solution"]:
                                player_buzzer_container = pygame.Rect(picture_container_width, (
                                        game_label_container_height + player_label_container_height + (n-1) * player_container_height),
                                                                      player_buzzer_container_width,
                                                                      player_buzzer_container_height)
                                pygame.draw.rect(screen, Static.GREEN, player_buzzer_container)
                                player_score_container = pygame.Rect(
                                    (picture_container_width + player_buzzer_container_width), (
                                                game_label_container_height + player_label_container_height + (n-1) * player_container_height),
                                    player_score_container_width, player_score_container_height)
                                pygame.draw.rect(screen, Static.WHITE, player_score_container)
                                playerScore[(n-1)] = playerScore[(n-1)] + 1
                                player_score = scorefont.render(str(playerScore[(n-1)]), 1, Static.BLACK)
                                screen.blit(player_score, player_score.get_rect(center=player_score_container.center))
                                points_reached()
                        solution_shown = "Reset"
                        pygame.display.flip()

            while solution_shown == "Reset" and not break_flag:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        buttonpressed = event.key
                        if buttonpressed == pygame.K_F4 and (pressed_keys[pygame.K_LALT] or pressed_keys[pygame.K_RALT]):
                            sys.exit()
                        if buttonpressed == pygame.K_ESCAPE:
                            os.chdir("/home/pi/Desktop/venv/mycode/")
                            break_flag = True
                            running = False
                    if buttonpressed == pygame.K_RETURN:
                        pygame.draw.rect(screen, Static.WHITE, solution_container)
                        pygame.display.flip()
                        # reset the buzzers to black
                        for n in range(0, players):
                            player_buzzer_container = pygame.Rect(picture_container_width, (
                                        game_label_container_height + player_label_container_height + n * player_container_height),
                                                                  player_buzzer_container_width,
                                                                  player_buzzer_container_height)
                            pygame.draw.rect(screen, Static.BLACK, player_buzzer_container)
                        pygame.draw.rect(screen, Static.WHITE, picture_counter_container)
                        nr += 1
                        progress = myfont.render(str(nr) + "/" + str(amount_of_content), 1, Static.RED)
                        pygame.display.flip()
                        random_pick_content()
                        pygame.display.flip()
                        question_answered = False
                        solution_shown = "Waiting"
                        pygame.display.flip()
        if break_flag:
            break


if __name__ == "__main__":
    multiple_choice_game(players, PlayersNameList, content_dir, screen, screenx, screeny, game_type)