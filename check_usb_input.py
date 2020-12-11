#!/usr/bin/env python3
# -*- coding: iso-8859-1 -*-

import subprocess
import time
import os

def get_mountedlist():
	return [item[item.find("/"):] for item in subprocess.check_output(["/bin/bash", "-c", "lsblk"]).decode("utf-8").split("\n") if "/" in item]

done = []
images_imported = False
time_consumed = 0

def usb_input_check(done, images_imported, time_consumed):
	while True:
		mounted = get_mountedlist()
		newly_mounted = [dev for dev in mounted if not dev in done]
		valid = sum([[drive for drive in newly_mounted]], [])
		for item in valid:
			if item not in ['/boot', '/']:
				os.chdir(item)
				if os.path.exists(item+"/Bilder"):
					categories = os.listdir(item+"/Bilder")
					for category in categories:
						if not os.path.exists("/home/pi/Desktop/SdR/Bilder/"+category):
							os.mkdir("/home/pi/Desktop/SdR/Bilder/"+category)
							for f in os.listdir(item+"/Bilder/"+category):
								if not os.path.isfile("/home/pi/Desktop/SdR/Bilder/"+category+"/"+f) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
									file_to_copy = item+'/Bilder/'+category+'/'+f
									file_to_create = '/home/pi/Desktop/SdR/Bilder/'+category+'/'+f
									os.popen("cp {} {}".format(file_to_copy, file_to_create))
					images_imported = True
				else:
					images_imported = True
				if os.path.exists(item+"/Sounds"):
					categories = os.listdir(item+"/Bilder")
					for category in categories:
						if not os.path.exists("/home/pi/Desktop/SdR/Sounds/"+category):
							os.mkdir("/home/pi/Desktop/SdR/Sounds/"+category)
							for f in os.listdir(item+"/Sounds/"+category):
								if not os.path.isfile("/home/pi/Desktop/SdR/Sounds/"+category+"/"+f) and f.lower().endswith(('.mp3', '.wav')):
									file_to_copy = item+'/Sounds/'+category+'/'+f
									file_to_create = '/home/pi/Desktop/SdR/Sounds/'+category+'/'+f
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
