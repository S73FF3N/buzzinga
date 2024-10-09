#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import os
import subprocess
from static import Static

time_consumed = 0

def run_update_buzzinga():
    try:
        git_directory = Static.GIT_DIRECTORY
        
        commands = [
            ["git", "remote", "prune", "origin"],
            ["git", "pull", "origin", "master"]
            # Uncomment the following lines if needed:
            #["git", "reset", "--hard", "origin/master"]
        ]
        
        for command in commands:
            result = subprocess.run(command, cwd=git_directory, capture_output=True, text=True)
            
            if result.returncode != 0:
                return f"Error: Command '{' '.join(command)}' failed with error: {result.stderr.strip()}"
        
        return "Update erfolgreich!"  # Update successful message
    
    except Exception as e:
        return f"Update nicht erfolgreich: {str(e)}"


if __name__ == '__main__':
    result = run_update_buzzinga()
    if result:
        print(result)
