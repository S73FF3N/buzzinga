#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import subprocess
import time
import os

time_consumed = 0

def run_update_buzzinga():
    try:
        #os.system("sudo apt-get -qq update")
        #os.system("sudo apt-get -qq upgrade")
        #os.system("sudo apt-get -qq --yes --assume-yes install lame")
        #os.chdir("/home/pi/Desktop/venv/mycode/")
        os.system("git remote prune origin")
        os.system("git pull origin master")
        #os.system("sudo git reset --hard origin/master")
        return
    except:
        return "Update nicht erfolgreich."


if __name__ == '__main__':
	run_update_buzzinga()
