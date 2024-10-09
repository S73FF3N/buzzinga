import subprocess
import time
import sys
from pathlib import Path
import shutil
import platform

from static import Static

def get_mountedlist():
    if platform.system() == "Windows":
        try:
            result = subprocess.run(["wmic", "logicaldisk", "get", "caption"], capture_output=True, text=True, check=True)
            return [Path(drive.strip()) for drive in result.stdout.split('\n')[1:] if drive.strip()]
        except subprocess.CalledProcessError:
            print("Error executing wmic command")
            return []
    else:  # Linux and other Unix-like systems
        try:
            result = subprocess.run(["lsblk"], capture_output=True, text=True, check=True)
            return [Path(item.split()[-1]) for item in result.stdout.split('\n') if '/' in item]
        except subprocess.CalledProcessError:
            print("Error executing lsblk command")
            return []
	
def copy_and_rename_files(src_dir, dest_dir, allowed_extensions):
    for file in src_dir.iterdir():
        if file.is_file() and file.suffix.lower() in allowed_extensions:
            new_name = file.name.replace(' ', '_').replace('(', 'zzz').replace(')', 'uuu')
            new_file = dest_dir / new_name
            if not new_file.exists():
                shutil.copy2(file, new_file)
                if platform.system() != "Windows":
                    new_file.chmod(0o777)
                    
def usb_input_check(game_type):
    done = set()
    files_imported = False
    time_consumed = 0
    folder = Path(game_type)

    while True:
        mounted = set(get_mountedlist())
        newly_mounted = mounted - done

        for item in newly_mounted:
            if item not in {Path('/boot'), Path('/')}:
                game_folder = item / folder
                if game_folder.exists():
                    if game_type in ["images", "sounds"]:
                        for category in game_folder.iterdir():
                            if category.is_dir():
                                new_category = Path(Static.ROOT_EXTENDED) / folder / category.name.replace(' ', '_')
                                new_category.mkdir(parents=True, exist_ok=True)
                                copy_and_rename_files(category, new_category, {'.png', '.jpg', '.jpeg', '.bmp', '.mp3', '.wav'})
                    elif game_type in ["questions", "hints", "who-knows-more"]:
                        dest_folder = Path(Static.ROOT_EXTENDED) / folder
                        dest_folder.mkdir(parents=True, exist_ok=True)
                        copy_and_rename_files(game_folder, dest_folder, {'.json'})
                    
                    files_imported = True

                if files_imported:
                    if platform.system() != "Windows":
                        try:
                            subprocess.run(["sudo", "umount", str(item)], check=True)
                        except subprocess.CalledProcessError:
                            print(f"Error unmounting {item}")
                            return "Error during file import"
                    return "Files successfully imported"

        done = mounted
        time.sleep(2)
        time_consumed += 2
        if time_consumed >= 4:
            return "No files imported"


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide game type as an argument")
    else:
        result = usb_input_check(game_type=sys.argv[1])
        print(result)
