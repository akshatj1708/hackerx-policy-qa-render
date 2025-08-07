import os
import subprocess
import shutil

def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # Skip if it's a symbolic link
            if not os.path.islink(fp):
                try:
                    total_size += os.path.getsize(fp)
                except (OSError, FileNotFoundError):
                    pass
    return total_size

def main():
    # Create a virtual environment
    os.system('python -m venv venv')
    
    # Activate virtual environment and install requirements
    if os.name == 'nt':  # Windows
        pip_path = os.path.join('venv', 'Scripts', 'pip')
        activate_cmd = 'call venv\\Scripts\\activate.bat && '
    else:  # Unix/Linux/MacOS
        pip_path = os.path.join('venv', 'bin', 'pip')
        activate_cmd = 'source venv/bin/activate && '
    
    # Install requirements
    print("Installing requirements...")
    subprocess.run(f'{activate_cmd}pip install -r requirements-optimized.txt', shell=True, check=True)
    
    # Get size of the virtual environment
    venv_size = get_size('venv')
    print(f"Virtual environment size: {venv_size / (1024 * 1024):.2f} MB")
    
    # Get size of the project files
    project_size = get_size('.')
    print(f"Project files size: {project_size / (1024 * 1024):.2f} MB")
    
    total_size = venv_size + project_size
    print(f"Total deployment size: {total_size / (1024 * 1024):.2f} MB")
    
    if total_size > 450 * 1024 * 1024:  # 450MB threshold to be safe
        print("WARNING: Deployment size is approaching the 512MB limit!")
    else:
        print("Deployment size is within safe limits.")

if __name__ == "__main__":
    main()
