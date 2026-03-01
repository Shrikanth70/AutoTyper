import os
import sys
import winshell
from win32com.client import Dispatch

class StartupManager:
    def __init__(self, app_name="AutoTyper"):
        self.app_name = app_name
        self.startup_path = winshell.startup()
        self.shortcut_path = os.path.join(self.startup_path, f"{self.app_name}.lnk")

    def is_enabled(self):
        return os.path.exists(self.shortcut_path)

    def set_startup(self, enabled=True):
        if enabled:
            if not os.path.exists(self.shortcut_path):
                self._create_shortcut()
        else:
            if os.path.exists(self.shortcut_path):
                os.remove(self.shortcut_path)

    def _create_shortcut(self):
        # Path to the current executable or script
        target = sys.executable
        if not getattr(sys, 'frozen', False):
            # If running as script, target the script itself (not recommended for startup)
            target = os.path.abspath(sys.argv[0])
            
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(self.shortcut_path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = os.getcwd()
        shortcut.IconLocation = target # Assuming icon is bundled in exe
        shortcut.save()

# Usage in settings toggles:
# manager = StartupManager()
# manager.set_startup(True)
