import PyInstaller.__main__
import os
import sys

def build():
    # Define paths
    script_path = "main.py"
    icon_path = os.path.join("assets", "icon.ico")
    
    # Ensure icon exists or use a default if missing during build
    if not os.path.exists(icon_path):
        print(f"Warning: Icon not found at {icon_path}. Build will proceed without it.")
        icon_path = None

    params = [
        script_path,
        "--name=AutoTyper",
        "--noconsole",          # Windows app, no terminal
        "--onefile",           # Bundle into a single .exe
        f"--icon={icon_path}" if icon_path else "",
        "--add-data=config.json;.", # Include config
        "--add-data=core/*.py;core", # Include core modules
        "--add-data=ui/*.py;ui",     # Include UI modules
        "--hidden-import=keyboard",
        "--hidden-import=pyperclip",
        "--hidden-import=pyautogui",
        "--hidden-import=faster_whisper",
        "--hidden-import=sounddevice",
        "--hidden-import=pystray",
        "--hidden-import=PIL",
        "--hidden-import=winshell",
        "--hidden-import=win32com.client",
        "--hidden-import=websockets",
        "--hidden-import=asyncio",
        "--collect-all=faster_whisper", 
        "--collect-all=websockets",
    ]

    # Filter out empty strings
    params = [p for p in params if p]

    print(f"Starting build with command: pyinstaller {' '.join(params)}")
    PyInstaller.__main__.run(params)

if __name__ == "__main__":
    build()
