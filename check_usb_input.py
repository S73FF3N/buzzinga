#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import subprocess
import time
import os
import sys

def get_mountedlist():
	return [item[item.find(b'/'):] for item in subprocess.check_output(["/bin/bash", "-c", "lsblk"]).split(b'\n') if b'/' in item]

done = []
images_imported = False
time_consumed = 0

def usb_input_check(done, images_imported, time_consumed):
	while True:
		mounted = get_mountedlist()
		newly_mounted = [dev for dev in mounted if not dev in done]
		valid = sum([[drive for drive in newly_mounted]], [])
		for item in valid:
			if item not in [b'/boot', b'/']:
				os.chdir(item)
				if os.path.exists(item+b'/Bilder'):
					categories = os.listdir(item+b'/Bilder')
					for category in categories:
						if not os.path.exists(b'/home/pi/Desktop/SdR/Bilder/'+category):
							dir_name = b'/home/pi/Desktop/SdR/Bilder/'+category
							os.mkdir(dir_name.decode('utf-8'))
							for f in os.listdir(item+b'/Bilder/'+category):
								if not os.path.isfile(b'/home/pi/Desktop/SdR/Bilder/'+category+b'/'+f) and f.lower().endswith((b'.png', b'.jpg', b'.jpeg', b'.bmp')):
									file_to_copy = item+b'/Bilder/'+category+b'/'+f
									file_to_create = b'/home/pi/Desktop/SdR/Bilder/'+category+b'/'+f
									os.popen("cp {} {}".format(file_to_copy.decode('utf-8'), file_to_create.decode('utf-8')))
					images_imported = True
				else:
					images_imported = True
				if os.path.exists(item+b'/Audio'):
					categories = os.listdir(item+b'/Audio')
					for category in categories:
						if not os.path.exists(b'/home/pi/Desktop/SdR/Audio/'+category):
							os.mkdir(b'/home/pi/Desktop/SdR/Audio/'+category)
							for f in os.listdir(item+b'/Audio/'+category):
								if not os.path.isfile(b'/home/pi/Desktop/SdR/Audio/'+category+b'/'+f) and f.lower().endswith((b'.mp3', b'.wav')):
									file_to_copy = item+b'/Audio/'+category+b'/'+f
									file_to_create = b'/home/pi/Desktop/SdR/Audio/'+category+b'/'+f
									os.popen("cp {} {}".format(file_to_copy, file_to_create))
					if images_imported == True:
						os.system("umount item")
						return "Bilder und Sounds erfolgreich importiert"
					else:
						os.system("umount item")
						return "Sounds erfolgreich importiert"
				else:
					if images_imported == True:
						os.system("umount item")
						return "Bilder erfolgreich importiert"
		done = mounted
		time.sleep(2)
		time_consumed += 2
		if time_consumed >= 4:
			return "keine Dateien gefunden"
			break

if __name__ == '__main__':
	print(usb_input_check([], False, 0))
