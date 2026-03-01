import time
import threading
import pyautogui
import keyboard
import random

from core.state_manager import state_manager

class TypingEngine:
    def __init__(self):
        self._lock = threading.Lock()

    def type_text(self, text, speed=0.05, initial_delay=0.5, human_like=True, paste_mode=False):
        # Clear stop event before starting (though usually managed by StateManager)
        # state_manager.stop_event.clear()
        
        # Small delay before starting
        start_time = time.time()
        while time.time() - start_time < initial_delay:
            if state_manager.stop_event.is_set():
                return
            time.sleep(0.01)

        if paste_mode:
            if state_manager.stop_event.is_set(): return
            pyautogui.write(text)
            return

        for char in text:
            if state_manager.stop_event.is_set():
                break
            
            keyboard.write(char)
            
            current_delay = speed
            if human_like:
                variance = speed * 0.3
                current_delay += random.uniform(-variance, variance)
            
            # Sub-delay loop to keep it responsive to stop_event
            delay_start = time.time()
            while time.time() - delay_start < max(0.001, current_delay):
                if state_manager.stop_event.is_set():
                    return
                time.sleep(0.005)

typing_engine = TypingEngine()
