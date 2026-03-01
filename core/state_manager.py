from enum import Enum, auto
import threading
import logging

class State(Enum):
    IDLE = auto()
    LISTENING = auto()
    PROCESSING = auto()
    READY_TO_TYPE = auto()
    TYPING = auto()

class StateManager:
    def __init__(self):
        self._state = State.IDLE
        self._voice_buffer = ""
        self._clipboard_buffer = ""
        self._active_source = None # 'voice' or 'clipboard'
        self.stop_event = threading.Event()
        self._lock = threading.Lock()
        self.logger = logging.getLogger("StateManager")
        self.on_state_change = None # Callback for UI/Main

    @property
    def state(self):
        with self._lock:
            return self._state

    @property
    def active_source(self):
        with self._lock:
            return self._active_source

    @property
    def voice_buffer(self):
        with self._lock:
            return self._voice_buffer

    @property
    def clipboard_buffer(self):
        with self._lock:
            return self._clipboard_buffer

    def transition_to(self, new_state, active_source=None):
        with self._lock:
            old_state = self._state
            if old_state == new_state and old_state != State.IDLE:
                return False
                
            self.logger.info(f"Transition: {old_state.name} -> {new_state.name}")
            self._state = new_state
            if active_source is not None:
                self._active_source = active_source
            
            if self.on_state_change:
                threading.Thread(target=self.on_state_change, args=(old_state, new_state)).start()
            return True

    def set_buffers(self, voice=None, clipboard=None):
        with self._lock:
            if voice is not None: self._voice_buffer = voice
            if clipboard is not None: self._clipboard_buffer = clipboard

    def clear_buffers(self):
        with self._lock:
            self._voice_buffer = ""
            self._clipboard_buffer = ""
            self._active_source = None

    def reset(self):
        self.stop_event.set()
        with self._lock:
            self._state = State.IDLE
            self._voice_buffer = ""
            self._clipboard_buffer = ""
            self._active_source = None
            self.logger.info("StateManager RESET to IDLE (Stop Event Set)")

state_manager = StateManager()
