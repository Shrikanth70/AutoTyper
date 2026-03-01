import re

class TextProcessor:
    def __init__(self):
        pass

    def clean_text(self, text):
        if not text:
            return ""
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        # Normalize newlines
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Optional: Remove extra internal newlines (keep single ones)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text

    def is_valid_typing_text(self, text):
        # Prevent massive blocks if necessary or empty strings
        if not text or len(text) == 0:
            return False
        return True

text_processor = TextProcessor()
