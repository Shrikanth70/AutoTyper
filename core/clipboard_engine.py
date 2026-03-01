import pyperclip
import logging

class ClipboardEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_text(self):
        try:
            text = pyperclip.paste()
            if not text:
                self.logger.warning("Clipboard is empty.")
                return ""
            return text
        except Exception as e:
            self.logger.error(f"Failed to read clipboard: {e}")
            return ""

clipboard_engine = ClipboardEngine()
