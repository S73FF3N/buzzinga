import pygame

def return_layout(screenx, screeny):
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
    return game_label_container, picture_container, picture_counter_container, countdown_container