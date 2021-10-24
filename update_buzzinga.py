#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import subprocess
import time
import os

time_consumed = 0

def run_update_buzzinga():
    try:
        os.chdir("/home/pi/Desktop/venv/mycode/")
        os.system("git pull origin v300")
        return ""
    except:
        return "Update nicht erfolgreich."


if __name__ == '__main__':
	print(run_update_buzzinga())
