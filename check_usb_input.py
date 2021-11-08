#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import subprocess
import time
import os
import sys


def get_mountedlist():
	return [item[item.find(b'/'):] for item in subprocess.check_output(["/bin/bash", "-c", "lsblk"]).split(b'\n') if b'/' in item]


def usb_input_check(done=[], files_imported=False, time_consumed=0, game_type=sys.argv[1]):
	while True:
		mounted = get_mountedlist()
		newly_mounted = [dev for dev in mounted if dev not in done]
		valid = sum([[drive for drive in newly_mounted]], [])

		if game_type == "images":
			folder = b'/Bilder/'
		elif game_type == "sounds":
			folder = b'/Audio/'
		elif game_type == "questions":
			folder = b'/Questions/'

		# get files from usb and copy them to raspberry
		for item in valid:
			if item not in [b'/boot', b'/']:
				os.chdir(item)
				if os.path.exists(item + folder) and game_type in ["images", "sounds"]:
					categories = os.listdir(item + folder)
					for category in categories:  # type: bytes
						c_renamed = category.replace(b' ', b'_')
						path_old = item + folder + category
						path_new = item + folder + c_renamed
						if category != c_renamed:
							os.rename(path_old.decode('utf-8'), path_new.decode('utf-8'))
						if not os.path.isdir(item + folder + c_renamed):
							continue
						if not os.path.exists(b'/home/pi/Desktop/SdR' + folder + c_renamed):
							dir_name = b'/home/pi/Desktop/SdR' + folder + c_renamed
							os.mkdir(dir_name.decode('utf-8'))
						# remove whitespaces from file names
						for f in os.listdir(item + folder + c_renamed):
							file = item + folder + c_renamed + b'/' + f
							f_renamed = f.replace(b' ', b'_')
							f_renamed = f_renamed.replace(b'(', b'zzz')
							f_renamed = f_renamed.replace(b')', b'uuu')
							file_renamed = item + b'/home/pi/Desktop/SdR' + folder + c_renamed + b'/' + f_renamed
							if f != f_renamed:
								os.rename(file.decode('utf-8'), file_renamed.decode('utf-8'))
						for f in os.listdir(item + folder + c_renamed):
							if not os.path.isfile(b'/home/pi/Desktop/SdR' + folder + c_renamed+b'/'+f) and f.lower().endswith((b'.png', b'.jpg', b'.jpeg', b'.bmp')):
								file_to_copy = item + folder + c_renamed + b'/' + f
								file_to_create = b'/home/pi/Desktop/SdR' + folder + b'/' + c_renamed + b'/' + f
								os.popen("cp {} {}".format(file_to_copy.decode('utf-8'), file_to_create.decode('utf-8')))
								os.popen("sudo chmod 777 {}".format(file_to_create.decode('utf-8')))
					files_imported = True

				if os.path.exists(item + folder) and game_type in ["questions"]:
					for f in os.listdir(item + folder):
						f_renamed = f.replace(b' ', b'_')
						path_old = item + folder + f
						path_new = item + folder + f_renamed
						if f != f_renamed:
							os.rename(path_old.decode('utf-8'), path_new.decode('utf-8'))
						if not os.path.isfile(
								b'/home/pi/Desktop/SdR' + folder + b'/' + f_renamed) and f_renamed.lower().endswith(b'.json'):
							file_to_copy = item + folder + b'/' + f_renamed
							os.putenv("file_to_copy", file_to_copy.decode('utf-8').strip())
							file_to_create = b'/home/pi/Desktop/SdR' + folder + b'/' + f_renamed
							os.putenv("file_to_create", file_to_create.decode('utf-8').strip())
							os.popen('cp "$file_to_copy" "$file_to_create"')
							os.popen('sudo chmod 777 "$file_to_create"')
					files_imported = True

			# unmount usb and print message
			if files_imported:
				os.putenv("item", item.decode('utf-8').strip())
				os.system('sudo umount "$item"')
				return "Dateien erfolgreich importiert"
			else:
				os.putenv("item", item.decode('utf-8').strip())
				os.system('sudo umount "$item"')
				return "Keine Dateien importiert"

		done = mounted
		time.sleep(2)
		time_consumed += 2
		if time_consumed >= 4:
			return "keine Dateien importiert"


if __name__ == '__main__':
	usb_input_check(done=[], files_imported=False, time_consumed=0, game_type="images")
