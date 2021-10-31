# -*- coding: latin-1 -*-
import os, sys

def run_wifi_settings():
    try:
        running = False
        os.system("sudo raspi-config")
        sys.exit()
        return
    except:
        return "Wifi Settings nicht erreichbar."


if __name__ == '__main__':
	run_wifi_settings()