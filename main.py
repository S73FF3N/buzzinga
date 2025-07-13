import os
import subprocess
import sys

def main():
    # Check if we're running inside a PyInstaller-built executable
    # Always use sys.executable for creating venv
    python_executable = sys.executable

    # Use correct base directory for venv and target script
    if getattr(sys, 'frozen', False):
        # PyInstaller: use directory of the executable
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(script_dir, 'buzzinga-venv')
    target_script = os.path.join(script_dir, 'buzzinga_class.py')


    # Determine the path to the Python executable inside the virtual environment
    if os.name == 'nt':
        # Windows
        venv_python_executable = os.path.join(venv_path, 'Scripts', 'python.exe')
    else:
        # macOS and Linux
        venv_python_executable = os.path.join(venv_path, 'bin', 'python')

    # Execute the target script using the virtual environment's Python executable
    print(f"Executing {target_script} using the virtual environment...")
    try:
        subprocess.check_call([venv_python_executable, target_script])
    except subprocess.CalledProcessError as e:
        print(f"Error executing the script: {e}")
        sys.exit(e.returncode)


if __name__ == '__main__':
    main()