# -*- coding: utf-8 -*-

import os, pygame, random
from pygame.locals import *
from game_utilities import convert_image_to, load_image
from static import Static

def buzzer_game(players, playerNamesList, content_dir, screen, screenx, screeny, image_game, game_sounds, game_modus, points_to_win):
	pygame.mixer.pre_init(44100, -16, 2, 2048)
	pygame.mixer.init()

	# declare and array for player names and initial score
	playerNames = playerNamesList
	playerScore = [0]*players
	# key definitions
	playerKeys = [0, 5, 10, 15]
	answer = [K_r, K_f]

	# Set the fonts for the textf
	myfont = pygame.font.SysFont("Ariel", 50)
	scorefont = pygame.font.SysFont("Ariel", 100)
	
	# defining the container for the graphical elements
	game_label_container_width = screenx/10*8
	game_label_container_height = screeny/10
	game_label_container = pygame.Rect(0, 0, game_label_container_width, game_label_container_height)
	picture_container_width = game_label_container_width
	picture_container_height = screeny/10*8
	picture_container = pygame.Rect(0, game_label_container_height, picture_container_width, picture_container_height)
	solution_container_width = picture_container_width
	solution_container_height = screeny/10
	solution_container = pygame.Rect(0, (game_label_container_height + picture_container_height), solution_container_width, solution_container_height)
	picture_counter_container_width = screenx/10*2
	picture_counter_container_height = screeny/10
	picture_counter_container = pygame.Rect(game_label_container_width, 0, picture_counter_container_width, picture_counter_container_height)
	scoreboard_container_width = picture_counter_container_width
	scoreboard_container_height = screeny/10*8
	scoreboard_container = pygame.Rect(picture_container_width, picture_container_height, scoreboard_container_width, scoreboard_container_height)
	countdown_container_width = scoreboard_container_width
	countdown_container_height = screeny/10
	countdown_container = pygame.Rect(solution_container_width, ( game_label_container_height + picture_container_height), countdown_container_width, countdown_container_height)
	player_container_width = scoreboard_container_width
	player_container_height = scoreboard_container_height/4
	player_label_container_width = player_container_width
	player_label_container_height = player_container_height/10*3
	player_buzzer_container_width = player_container_width/2
	player_buzzer_container_height = player_container_height/10*7
	player_score_container_width = player_container_width/2
	player_score_container_height = player_container_height/10*7
	
	# define picture format
	picture_width = int(picture_container_width/10*9)
	picture_length = int(picture_container_height/10*9)
	
	# text displayed at the beginning
	game_name = os.path.basename(os.path.dirname(content_dir))
	welcome = u"Willkommen zu " + game_name
	
	# build content dictionary from content directory
	
	content_list = os.listdir(content_dir)
	
	logo = "BuzzingaLogo.bmp"
	picture = load_image(logo, 'images')

	game_started_from_path = os.getcwd()
	os.chdir(content_dir)
	
	content_dict = {}
	
	def build_content_dict(content):
		base=os.path.basename(content_dir+content)
		name_o=os.path.splitext(base)[0]
		name=name_o.replace("_"," ")
		content_dict[name] = content_dir+content

	#loading info
	loading = myfont.render("loading...", 1, Static.RED)
	screen.fill(Static.WHITE)
	screen.blit(loading, loading.get_rect(center=picture_container.center))
	pygame.display.flip()

	for file_in in content_list:
		if os.path.isdir(file_in):
			continue
		if file_in.startswith("."):
			continue
		elif file_in.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.mp3', '.wav')):
			try:
				if image_game == True:
					# images in image directory are converted into .bmp
					file_in = convert_image_to(file_in, "bmp")
				build_content_dict(file_in)
			except:
				continue
		else:
			continue

	amount_of_content = len(content_dict)

	global winner_found
	winner_found = False
	
	# randomly chosing content from content dictionary and updating solution label
	sound_channel = pygame.mixer.Channel(0)
	game_sound_channel = pygame.mixer.Channel(1)
	def random_pick_content():
		global random_key
		global random_val
		global winner_found
		try:
			random_key = random.choice(list(content_dict.keys()))
			random_val = content_dict[random_key]
			del content_dict[random_key]
		except:
			winner_found = True
		if image_game == True:
			if winner_found == False:
				random_content = load_image(random_val, content_dir)
				image_size = random_content.get_rect().size
				if image_size[0] >= image_size[1]:
					if int((image_size[1]/float(image_size[0]))*picture_width) < picture_length:
						image_size = (picture_width, int((image_size[1]/float(image_size[0]))*picture_width))
					else:
						image_size = (int((image_size[0]/float(image_size[1]))*picture_length), picture_length)
				else:
					if int((image_size[0]/float(image_size[1]))*picture_length) < picture_width:
						image_size = (int((image_size[0]/float(image_size[1]))*picture_length), picture_length)
					else:
						image_size = (picture_width, int((image_size[1]/float(image_size[0]))*picture_width))
				random_content = pygame.transform.scale(random_content, image_size)
				pygame.draw.rect(screen, Static.WHITE, picture_container)
				screen.blit(random_content, random_content.get_rect(center=picture_container.center))
			else:
				show_winner()
		else:
			random_sound = pygame.mixer.Sound(random_val)
			sound_channel.play(random_sound)
			if winner_found == False:
				pygame.draw.rect(screen, Static.WHITE, solution_container)
			"""else:
				show_winner()"""
		screen.blit(progress, progress.get_rect(center=picture_counter_container.center))
		return random_key, winner_found

	def show_winner():
		pygame.draw.rect(screen, Static.WHITE, picture_container)
		winner_ix = [i for i,x in enumerate(playerScore) if x==max(playerScore)]
		winners = [scorefont.render("Gewinner:", 1, Static.RED)]
		[winners.append(scorefont.render(playerNames[i], 1, Static.RED)) for i in winner_ix]
		scorefont_width, scorefont_height = scorefont.size("Test")
		for line in range(len(winners)):
			screen.blit(winners[line], (0+ picture_container_width/3, game_label_container_height + picture_container_height/4+(line*scorefont_height)+(15*line)))

	# print solution in solution label     
	def show_solution():
		solution = myfont.render(random_key, 1, Static.RED)
		screen.blit(solution, solution.get_rect(center=solution_container.center))
	
	#countdown printed in solution label
	def countdown(count_from):
		for i in range(1,count_from):
			time_left = count_from - i
			time_left =str(time_left)
			countdown = myfont.render(time_left, 1, Static.RED)
			screen.blit(countdown, countdown.get_rect(center=countdown_container.center))
			pygame.display.flip()
			pygame.time.wait(1000)
			if time_left != 0:
				pygame.draw.rect(screen, Static.WHITE, countdown_container)
				pygame.display.flip()
		if game_sounds == True:
			countdown_sound = pygame.mixer.Sound("/home/pi/Desktop/venv/mycode/sounds/wrong-answer.wav")
			game_sound_channel.play(countdown_sound)

	def points_reached():
		global winner_found
		if game_modus == False:
			if points_to_win == max(playerScore):
				winner_found = True

	screen.fill(Static.WHITE)
	pygame.display.set_caption(game_name)
	
	# Created Variable for the text on the screen
	#picture = pygame.transform.scale(picture, (picture_width, picture_length))
	game_label = myfont.render(game_name, 1, Static.RED)
	solution_label = myfont.render(welcome, 1, Static.RED)
	nr = 1
	progress = myfont.render(str(amount_of_content)+" Dateien", 1, Static.RED)
	screen.blit(game_label, game_label.get_rect(center=game_label_container.center))
	screen.blit(progress, progress.get_rect(center=picture_counter_container.center))
	screen.blit(picture, picture.get_rect(center=picture_container.center))
	screen.blit(solution_label, solution_label.get_rect(center=solution_container.center))
	
	# Draw name of players, 4 empty rectangles and players score
	for n in range (0, players):
		player_label = myfont.render(playerNames[n], 1, Static.BLACK)
		player_label_container = pygame.Rect(picture_container_width, (picture_counter_container_height + n*player_container_height), player_label_container_width, player_label_container_height)
		screen.blit(player_label, player_label.get_rect(center=player_label_container.center))
		player_buzzer_container = pygame.Rect(picture_container_width, (game_label_container_height + player_label_container_height + n*player_container_height), player_buzzer_container_width, player_buzzer_container_height)
		pygame.draw.rect(screen, Static.BLACK, player_buzzer_container)
		player_score = scorefont.render(str(playerScore[n]), 1, Static.BLACK)
		player_score_container = pygame.Rect((picture_container_width + player_buzzer_container_width), (game_label_container_height + player_label_container_height + n*player_container_height), player_score_container_width, player_score_container_height)
		screen.blit(player_score, player_score.get_rect(center=player_score_container.center))
	
	pygame.display.flip()
	
	first = 0 # used to signify the first key pressed and stops other being used
	waitReset = 1 # Reset section for the while loop
	show_solution_var = 1
	initialize = 1

	def return_to_main_menu():
		if image_game == False:
			sound_channel.stop()
		os.chdir("/home/pi/Desktop/venv/mycode/")
		return 'Main Menu'
	
	while True:
		while initialize == 1:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == K_ESCAPE:
						if image_game == False:
							sound_channel.stop()
						os.chdir("/home/pi/Desktop/venv/mycode/")
						return 'Main Menu'
					if event.key == K_RETURN:
						if image_game == True:
							pygame.draw.rect(screen, Static.WHITE, picture_container)
							pygame.display.flip()
						try:
							random_pick_content()
							pygame.display.flip()
						except:
							if image_game == False:
								sound_channel.stop()
							os.chdir("/home/pi/Desktop/venv/mycode/")
							return 'Main Menu'
						initialize = 0
					else:
						pass

		while first == 0:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == K_ESCAPE:
						if image_game == False:
							sound_channel.stop()
						os.chdir("/home/pi/Desktop/venv/mycode/")
						return 'Main Menu'
					if event.key == K_RETURN:
						first = 1
						try:
							if winner_found == False:
								show_solution_var = 1
								for n in range (0, players):
									player_buzzer_container = pygame.Rect(picture_container_width, (game_label_container_height + player_label_container_height + n*player_container_height), player_buzzer_container_width, player_buzzer_container_height)
									buzzer_blocked = scorefont.render("X", 1, Static.RED)
									screen.blit(buzzer_blocked, buzzer_blocked.get_rect(center=player_buzzer_container.center))
								pygame.display.flip()
						except:
							show_solution_var = 2

				if event.type == pygame.JOYBUTTONDOWN:
					buttonpressed = event.button
		                
					for n in range (0,players):
						if buttonpressed == playerKeys[n]:
							if image_game == False:
								sound_channel.pause()
							first_buzz = playerKeys.index(buttonpressed)
							player_buzzer_container = pygame.Rect(picture_container_width, (game_label_container_height + player_label_container_height + first_buzz*player_container_height), player_buzzer_container_width, player_buzzer_container_height)
							pygame.draw.rect(screen, Static.RED, player_buzzer_container)
							# buzzer sound
							if game_sounds == True:
								buzzerHit = pygame.mixer.Sound("/home/pi/Desktop/venv/mycode/sounds/buzzer_hit.wav")
								game_sound_channel.play(buzzerHit)
							first = 1
							countdown(5)
					pygame.display.flip()
					# a 'buzzer' was pressed and shown on screen
		            # now go to the reset code
		
		# loop waiting until the 'button' are reset
		waitReset=0
		
		while waitReset == 0:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
					if image_game == False:
						sound_channel.stop()
					os.chdir("/home/pi/Desktop/venv/mycode/")
					return 'Main Menu'

				# User pressed down on a key
				if event.type == pygame.KEYDOWN:
					keypressed = event.key

					# Check if Key Pressed to increase score
					if keypressed in answer:
						try:
							player_score_container = pygame.Rect((picture_container_width + player_buzzer_container_width), (game_label_container_height + player_label_container_height + first_buzz*player_container_height), player_score_container_width, player_score_container_height)
							pygame.draw.rect(screen, Static.WHITE, player_score_container)
							if keypressed == answer[0]:
								playerScore[first_buzz] = playerScore[first_buzz] + 1
							if keypressed == answer[1]:
								playerScore[first_buzz] = playerScore[first_buzz] - 1
							player_score = scorefont.render(str(playerScore[first_buzz]), 1, Static.BLACK)
							screen.blit(player_score, player_score.get_rect(center=player_score_container.center))
							pygame.display.flip()
							points_reached()
							if winner_found == True:
								show_winner()
						except:
							pass

					# After buzzer was pressed, referee shows solution and decides if answer was right or wrong
					if keypressed == K_RETURN and show_solution_var == 2:
						if image_game == False:
							sound_channel.stop()
						pygame.draw.rect(screen, Static.WHITE, solution_container)
						pygame.display.flip()
						# reset the buzzers to black
						for n in range (0, players):
							player_buzzer_container = pygame.Rect(picture_container_width, (game_label_container_height + player_label_container_height + n*player_container_height), player_buzzer_container_width, player_buzzer_container_height)
							pygame.draw.rect(screen, Static.BLACK, player_buzzer_container)
						first=0
						waitReset=1
						pygame.display.flip()
						show_solution_var = 0

					# solution is shown
					if keypressed == K_RETURN and show_solution_var == 1:
						try:
							if winner_found == False:
								if image_game == False:
									sound_channel.unpause()
								pygame.draw.rect(screen, Static.WHITE, solution_container)
								show_solution()
						except:
							pass
						pygame.display.flip()
						show_solution_var = 2

					if keypressed == K_RETURN and show_solution_var == 0:
						if winner_found == False:
							pygame.draw.rect(screen, Static.WHITE, picture_counter_container)
							nr += 1
							progress = myfont.render(str(nr)+"/"+str(amount_of_content), 1, Static.RED)
							pygame.display.flip()
							try:
								random_pick_content()
								pygame.display.flip()
							except:
								if image_game == False:
									sound_channel.stop()
								os.chdir("/home/pi/Desktop/venv/mycode/")
								return 'Main Menu'
							show_solution_var = 1

if __name__ == "__main__":
	buzzer_game(players, PlayersNameList, content_dir, screen, screenx, screeny, image_game)
