import os
import subprocess
import sys

def main():
    # Check if we're running inside a PyInstaller-built executable
    if getattr(sys, 'frozen', False):
        # Use the original Python executable instead of the bundled executable
        python_executable = sys._MEIPASS  # Path to PyInstaller's temp folder
        python_executable = os.path.join(python_executable, 'python')
        print(python_executable)
    else:
        python_executable = sys.executable

    # Define the path to the virtual environment and the target script
    venv_path = os.path.join(os.getcwd(), 'buzzinga-venv')
    target_script = os.path.join(os.getcwd(), 'buzzinga_class.py')

    # Check if the virtual environment exists
    if not os.path.isdir(venv_path):
        print("Virtual environment not found. Creating one...")
        subprocess.check_call([python_executable, '-m', 'venv', venv_path])

    # Determine the path to the Python executable inside the virtual environment
    if os.name == 'nt':
        # Windows
        activate_script = os.path.join(venv_path, 'Scripts', 'activate.bat')
        venv_python_executable = os.path.join(venv_path, 'Scripts', 'python.exe')
    else:
        # macOS and Linux
        activate_script = os.path.join(venv_path, 'bin', 'activate')
        venv_python_executable = os.path.join(venv_path, 'bin', 'python')

    # Ensure the virtual environment's Python executable exists
    if not os.path.isfile(venv_python_executable):
        print(f"Error: Python executable not found in the virtual environment at {venv_python_executable}")
        sys.exit(1)

    # Install dependencies if needed
    print("Ensuring dependencies are installed...")
    subprocess.check_call([venv_python_executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

    # Execute the target script using the virtual environment's Python executable
    print(f"Executing {target_script} using the virtual environment...")
    try:
        if os.name == 'nt':
            # Windows: Use cmd.exe to call activate.bat and execute the script
            subprocess.check_call(
                f'cmd /c "{activate_script} && python {target_script}"',
                shell=True
            )
        else:
            # Unix: Use bash to source the activate script and execute the script
            subprocess.check_call(
                f'bash -c "source {activate_script} && python {target_script}"',
                shell=True
            )
    except subprocess.CalledProcessError as e:
        print(f"Error executing the script: {e}")
        sys.exit(e.returncode)


if __name__ == '__main__':
    main()