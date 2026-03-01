import keyboard
import threading
import logging

class ShortcutListener:
    def __init__(self, hotkeys, on_clipboard, on_voice, on_stop, on_l_stop):
        self.logger = logging.getLogger(__name__)
        self.hotkeys = hotkeys
        self.on_clipboard = on_clipboard
        self.on_voice = on_voice
        self.on_stop = on_stop
        self.on_l_stop = on_l_stop
        self.running = False

    def start(self):
        self.logger.info("Starting shortcut listener...")
        try:
            keyboard.add_hotkey(self.hotkeys['clipboard_mode'], self.on_clipboard)
            keyboard.add_hotkey(self.hotkeys['voice_mode'], self.on_voice)
            keyboard.add_hotkey(self.hotkeys['emergency_stop'], self.on_stop)
            self.running = True
        except Exception as e:
            self.logger.error(f"Failed to register main hotkeys: {e}")

    def register_l(self):
        self.logger.info("Registering 'L' hotkey.")
        try:
            # use suppress=True to prevent 'L' from being typed in apps while listening
            keyboard.add_hotkey('l', self.on_l_stop, suppress=True)
        except Exception as e:
            self.logger.error(f"Failed to register 'L': {e}")

    def unregister_l(self):
        self.logger.info("Unregistering 'L' hotkey.")
        try:
            keyboard.remove_hotkey('l')
        except Exception:
            pass

    def stop(self):
        self.logger.info("Stopping shortcut listener...")
        keyboard.unhook_all()
        self.running = False

# Example usage (will be integrated in main.py)
# listener = ShortcutListener(config['hotkeys'], trigger_clipboard, trigger_voice, trigger_stop)
