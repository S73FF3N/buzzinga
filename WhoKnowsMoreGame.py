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
    answer_key = [pygame.K_r, pygame.K_f]

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

    picture_counter_container_width = screenx / 10
    picture_counter_container_height = screeny / 10
    picture_counter_container = pygame.Rect(game_label_container_width, 0, picture_counter_container_width,
                                            picture_counter_container_height)
    countdown_container_width = picture_counter_container_width
    countdown_container_height = screeny / 10
    countdown_container = pygame.Rect(picture_container_width,
                                      picture_container_height,
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
        content_dict[q["solution"]] = {'solution_link': solution_link, 'answers':{}}
        for a in q["answers"]:
            content_dict[q["solution"]]["answers"][a["count_id"]] = a["answer"]

    # loading info
    loading = myfont.render("loading...", 1, Static.RED)
    screen.fill(Static.WHITE)
    screen.blit(loading, loading.get_rect(center=picture_container.center))
    pygame.display.flip()

    amount_of_content = len(content_dict)

    winner_found = False

    # randomly chosing content from content dictionary
    def random_pick_content():
        global random_key
        global random_val
        global winner_found
        winner_found = False
        try:
            random_key = random.choice(list(content_dict.keys()))
            random_val = content_dict[random_key]
            del content_dict[random_key]
        except:
            winner_found = True
        if not winner_found:
            pygame.draw.rect(screen, Static.WHITE, picture_container)
            pygame.draw.rect(screen, Static.WHITE, game_label_container)
            game_label = myfont.render(random_key+" ("+random_val["solution_link"]+")", 1, Static.RED)
            screen.blit(game_label, game_label.get_rect(center=game_label_container.center))
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

    def points_reached():
        global winner_found
        if not game_modus:
            if points_to_win == max(playerScore):
                winner_found = True

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

    initialize = True
    running = True
    break_flag = False
    first_element_of_question = True
    active_player = 0
    countdown = False
    countdown_seconds_left = 30
    countdown_ended = False
    correct_answer = False
    incorrect_answer = False
    answer_id = ""
    answers_solved = []
    skip_print_answer = False
    number_keys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]
    active_players = [True] * players
    active_player_found = False

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
            active_players = [True] * players
            for n in range(0, players):
                player_buzzer_container = pygame.Rect(picture_container_width, (
                        game_label_container_height + player_label_container_height + n * player_container_height),
                                                      player_buzzer_container_width,
                                                      player_buzzer_container_height)
                pygame.draw.rect(screen, Static.BLACK, player_buzzer_container)
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

        while not winner_found and not break_flag and first_element_of_question:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        os.chdir("/home/pi/Desktop/venv/mycode/")
                        break_flag = True
                        break
                    if event.key == pygame.K_RETURN:
                        first_element_of_question = False
                        # mark player to give answer
                        player_buzzer_container = pygame.Rect(picture_container_width, (
                                game_label_container_height + player_label_container_height + active_player * player_container_height),
                                                              player_buzzer_container_width,
                                                              player_buzzer_container_height)
                        pygame.draw.rect(screen, Static.RED, player_buzzer_container)
                        pygame.display.flip()
                        # start countdown
                        countdown = True

        while countdown:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        os.chdir("/home/pi/Desktop/venv/mycode/")
                        countdown = False
                        break_flag = True
                        break
                    # answer is correct:
                    if event.key == pygame.K_r:
                        countdown = False
                        correct_answer = True
                    # answer is incorrect:
                    if event.key == pygame.K_f:
                        countdown = False
                        incorrect_answer = True

            if not countdown_ended:
                countdown_seconds_left -= 1
            time_left = str(countdown_seconds_left)
            time_left_rendered = myfont.render(time_left, 1, Static.RED)
            screen.blit(time_left_rendered, time_left_rendered.get_rect(center=countdown_container.center))
            pygame.display.flip()
            pygame.time.wait(1000)
            pygame.draw.rect(screen, Static.WHITE, countdown_container)
            pygame.display.flip()
            if countdown_seconds_left == 0:
                if game_sounds and not countdown_ended:
                    countdown_sound = pygame.mixer.Sound("/home/pi/Desktop/venv/mycode/sounds/wrong-answer.wav")
                    game_sound_channel.play(countdown_sound)
                countdown_ended = True

        while correct_answer:
            global random_val
            countdown_ended = False
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        os.chdir("/home/pi/Desktop/venv/mycode/")
                        break_flag = True
                        break
                    if event.key == pygame.K_BACKSPACE:
                        try:
                            answer_id = answer_id[:-1]
                            pygame.draw.rect(screen, Static.WHITE, countdown_container)
                            answer_id_input = myfont.render(answer_id, 1, Static.BLUE)
                            screen.blit(answer_id_input, answer_id_input.get_rect(center=countdown_container.center))
                            pygame.display.flip()
                        except Exception as e:
                            pass
                    if event.key in number_keys:
                        try:
                            # let game master provide id of given answer from pool of answers
                            answer_id += event.unicode
                            pygame.draw.rect(screen, Static.WHITE, countdown_container)
                            answer_id_input = myfont.render(answer_id, 1, Static.BLUE)
                            screen.blit(answer_id_input, answer_id_input.get_rect(center=countdown_container.center))
                            pygame.display.flip()
                        except Exception as e:
                            pass
                    if event.key == pygame.K_RETURN:
                        try:
                            # print answer on screen
                            answer_id_int = int(answer_id)
                            if random_val["answers"][answer_id_int] in answers_solved:
                                pygame.draw.rect(screen, Static.WHITE, countdown_container)
                                incorrect_input = myfont.render('Gelöst!', 1, Static.BLUE)
                                screen.blit(incorrect_input,
                                            incorrect_input.get_rect(center=countdown_container.center))
                                pygame.display.flip()
                                answer_id = ""
                                skip_print_answer = True
                            if not skip_print_answer:
                                answer = myfont.render(random_val["answers"][answer_id_int], 1, Static.WHITE)
                                # store solved answers to avoid that id can be accidentally used again
                                answers_solved.append(random_val["answers"][answer_id_int])
                                if len(random_val["answers"]) > 28:
                                    answer_container_width = (game_label_container_width / 6) - 5
                                    answer_container_height = (picture_container_height / 10) - 2
                                    x = ((answer_id_int - 1) % 6) * (answer_container_width + 5)
                                    y = ((answer_id_int - 1) // 6) * (answer_container_height + 2) + game_label_container_height
                                else:
                                    answer_container_width = (game_label_container_width / 4) - 5
                                    answer_container_height = (picture_container_height / 7) - 2
                                    x = ((answer_id_int - 1) % 4) * (answer_container_width + 5)
                                    y = ((answer_id_int - 1) // 4) * (answer_container_height + 2) + game_label_container_height
                                answer_container = pygame.Rect(x, y, answer_container_width,
                                                               answer_container_height)
                                pygame.draw.rect(screen, Static.BLUE, answer_container)
                                screen.blit(answer, answer.get_rect(center=answer_container.center))
                                pygame.display.flip()
                                answer_id = ""
                                # if answers left:
                                if len(random_val["answers"]) != len(answers_solved):
                                    #   mark player to give next answer
                                    active_player_found = False
                                    while not active_player_found:
                                        active_player += 1
                                        if active_player == players:
                                            active_player = 0
                                        if active_players[active_player]:
                                            active_player_found = True
                                    for n in range(0, players):
                                        player_buzzer_container = pygame.Rect(picture_container_width, (
                                                game_label_container_height + player_label_container_height + n * player_container_height),
                                                                              player_buzzer_container_width,
                                                                              player_buzzer_container_height)
                                        pygame.draw.rect(screen, Static.BLACK, player_buzzer_container)
                                        if not active_players[n]:
                                            buzzer_blocked = scorefont.render("X", 1, Static.RED)
                                            screen.blit(buzzer_blocked,
                                                        buzzer_blocked.get_rect(center=player_buzzer_container.center))
                                    player_buzzer_container = pygame.Rect(picture_container_width, (
                                            game_label_container_height + player_label_container_height + active_player * player_container_height),
                                                                          player_buzzer_container_width,
                                                                          player_buzzer_container_height)
                                    pygame.draw.rect(screen, Static.RED, player_buzzer_container)
                                    pygame.display.flip()
                                    #if active_player + 1 == players:
                                    #    active_player = 0
                                    #else:
                                    #    active_player += 1
                                    # start countdown
                                    correct_answer = False
                                    countdown_seconds_left = 30
                                    countdown = True
                                # no answers left
                                else:
                                #   set variable to start next round
                                    correct_answer = False
                                    initialize = True
                                    first_element_of_question = True
                                    answers_solved = []
                                    countdown_seconds_left = 30
                                #   no points assigned
                            skip_print_answer = False
                        except Exception as e:
                            pygame.draw.rect(screen, Static.WHITE, countdown_container)
                            incorrect_input = myfont.render('Falsche ID', 1, Static.BLUE)
                            screen.blit(incorrect_input, incorrect_input.get_rect(center=countdown_container.center))
                            pygame.display.flip()
                            answer_id = ""

            game_sound_channel.stop()
            pygame.draw.rect(screen, Static.WHITE, countdown_container)

        while incorrect_answer:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        os.chdir("/home/pi/Desktop/venv/mycode/")
                        break_flag = True
                        break

            game_sound_channel.stop()
            pygame.draw.rect(screen, Static.WHITE, countdown_container)
            incorrect_answer = False

            # exlude player from round
            active_players[active_player] = False

            pygame.display.flip()
            active_player_found = False
            while not active_player_found:
                active_player += 1
                if active_player == players:
                    active_player = 0
                if active_players[active_player]:
                    active_player_found = True
            #   mark player to give next answer
            for n in range(0, players):
                player_buzzer_container = pygame.Rect(picture_container_width, (
                        game_label_container_height + player_label_container_height + n * player_container_height),
                                                      player_buzzer_container_width,
                                                      player_buzzer_container_height)
                pygame.draw.rect(screen, Static.BLACK, player_buzzer_container)
                if not active_players[n]:
                    buzzer_blocked = scorefont.render("X", 1, Static.RED)
                    screen.blit(buzzer_blocked,
                                buzzer_blocked.get_rect(center=player_buzzer_container.center))
            player_buzzer_container = pygame.Rect(picture_container_width, (
                    game_label_container_height + player_label_container_height + active_player * player_container_height),
                                                  player_buzzer_container_width,
                                                  player_buzzer_container_height)
            pygame.draw.rect(screen, Static.RED, player_buzzer_container)
            pygame.display.flip()
            # only one player is left in round
            if sum(active_players) == 1:
                #   set variable to start next round
                initialize = True
                first_element_of_question = True
                answers_solved = []
                countdown_seconds_left = 30
                #   print all answers left
                #   assign point to winning player
                player_score_container = pygame.Rect((picture_container_width + player_buzzer_container_width),
                                                     (
                                                             game_label_container_height + player_label_container_height + active_player * player_container_height),
                                                     player_score_container_width,
                                                     player_score_container_height)
                pygame.draw.rect(screen, Static.WHITE, player_score_container)
                playerScore[active_player] += 1
                player_score = scorefont.render(str(playerScore[active_player]), 1, Static.BLACK)
                screen.blit(player_score, player_score.get_rect(center=player_score_container.center))
                pygame.display.flip()
            else:
                # start countdown
                countdown_seconds_left = 30
                countdown = True

        if break_flag:
            break


if __name__ == "__main__":
    buzzer_game(players, PlayersNameList, content_dir, screen, screenx, screeny, game_type)
