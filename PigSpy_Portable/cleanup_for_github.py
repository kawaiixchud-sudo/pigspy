#!/usr/bin/env python3
"""
PigSpy Cleanup and GitHub Preparation Script
This script cleans up the PigSpy project for public release on GitHub.
"""

import os
import shutil
import subprocess
import sys

def remove_directories(dirs_to_remove):
    """Remove specified directories if they exist."""
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            print(f"Removing directory: {dir_path}")
            shutil.rmtree(dir_path)
        else:
            print(f"Directory not found: {dir_path}")

def remove_files(files_to_remove):
    """Remove specified files if they exist."""
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            print(f"Removing file: {file_path}")
            os.remove(file_path)
        else:
            print(f"File not found: {file_path}")

def clean_config():
    """Clean config.py to remove identifying information."""
    config_path = "config.py"
    if not os.path.exists(config_path):
        print("config.py not found, skipping config cleanup")
        return

    with open(config_path, 'r') as f:
        content = f.read()

    # Replace specific stream URL with a placeholder
    content = content.replace(
        'STREAM_URL = "https://broadcastify.cdnstream1.com/19080"',
        'STREAM_URL = "YOUR_STREAM_URL_HERE"  # Replace with your broadcastify stream URL'
    )

    with open(config_path, 'w') as f:
        f.write(content)

    print("Cleaned config.py")

def create_readme():
    """Create a clean README.md file."""
    readme_content = """# PigSpy - Police Scanner Monitor

A real-time police scanner monitoring application with speech recognition and keyword detection.

## Features

- Real-time audio stream monitoring
- Speech-to-text transcription using Whisper
- Keyword detection with notifications
- Textual-based TUI (Terminal User Interface)
- Cross-platform support (Windows/Linux/macOS)

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio processing)
- VLC Media Player (optional, for MP3 playback)

### Quick Install

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pigspy.git
cd pigspy
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your stream URL in `config.py`:
```python
STREAM_URL = "https://your-stream-url-here"
```

## Usage

Run the application:
```bash
python main.py
```

### Controls

- `1` - Start monitoring
- `2` - Stop monitoring
- `3` - Toggle audio passthrough
- `S` - Toggle silence mode
- `N` - Toggle notifications
- `C` - Clear logs

## Configuration

Edit `config.py` to customize:

- Stream URL
- Keywords to detect
- Audio settings
- Notification preferences

## License

MIT License - see LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes only. Ensure you comply with all local laws and regulations regarding scanner monitoring.
"""

    with open("README.md", "w") as f:
        f.write(readme_content)

    print("Created README.md")

def create_gitignore():
    """Create .gitignore file."""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
.venv/
env/
ENV/

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/

# Temporary files
*.tmp
*.temp
"""

    with open(".gitignore", "w") as f:
        f.write(gitignore_content)

    print("Created .gitignore")

def init_git():
    """Initialize git repository."""
    if os.path.exists(".git"):
        print("Git repository already initialized")
        return True

    try:
        subprocess.run(["git", "init"], check=True)
        
        # Check if user is configured
        result = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
        if result.returncode != 0:
            print("Git user not configured. Please run:")
            print('git config --global user.name "Your Name"')
            print('git config --global user.email "your.email@example.com"')
            print("Then run: git commit -m 'Initial commit'")
            return False
            
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
        print("Git repository initialized and initial commit made")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error initializing git: {e}")
        return False

def main():
    print("Starting PigSpy cleanup for GitHub...")

    # Directories to remove
    dirs_to_remove = [
        "logs",
        "build",
        "dist",
        "__pycache__",
        ".venv",
        "venv",
        "PigSpy_Portable"  # Remove duplicate folder if exists
    ]

    # Files to remove
    files_to_remove = [
        "main.spec",  # PyInstaller spec file
        "START_HERE.txt",  # Windows-specific instructions
        "install_and_run.bat",
        "run.bat",
        "run_pigspy.bat",
        "setup_portable.py"
    ]

    remove_directories(dirs_to_remove)
    remove_files(files_to_remove)

    clean_config()
    create_readme()
    create_gitignore()

    if init_git():
        print("\nNext steps:")
        print("1. Create a new repository on GitHub")
        print("2. Run: git remote add origin https://github.com/yourusername/pigspy.git")
        print("3. Run: git push -u origin main")
        print("4. Update README.md with your repository URL")

    print("\nCleanup complete!")

if __name__ == "__main__":
    main()