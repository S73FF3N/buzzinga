#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import subprocess
import time
import os

time_consumed = 0

def run_update_buzzinga():
    try:
        os.system("sudo add-apt-repository universe")
        os.system("sudo apt -qq update")
        os.system("sudo apt -qq autoremove")
        os.system("sudo apt -qq install libavcodec58")
        os.system("sudo apt -qq install libwebpmux3")
        os.system("sudo apt -qq --yes --assume-yes install ffmpeg")
        os.chdir("/home/pi/Desktop/venv/mycode/")
        os.system("git pull origin master")
        return
    except:
        return "Update nicht erfolgreich."


if __name__ == '__main__':
	run_update_buzzinga()
