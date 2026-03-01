import os
import threading
import queue
import numpy as np
import sounddevice as sd
import collections
from faster_whisper import WhisperModel
import logging

class VoiceEngine:
    def __init__(self, model_size="tiny", device="cpu", compute_type="int8"):
        self.logger = logging.getLogger(__name__)
        self.model_path = os.path.join(os.getcwd(), "models", "whisper_model")
        
        # Load model only once
        self.logger.info(f"Loading Whisper model: {model_size} on {device}...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type, download_root=self.model_path)
        
        self.sample_rate = 16000
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.chunk_size = 1024
        self._current_recording = []

    def audio_callback(self, indata, frames, time, status):
        if status:
            self.logger.error(f"Sounddevice status: {status}")
        self.audio_queue.put(indata.copy())

    def record_start(self):
        from core.state_manager import state_manager
        state_manager.stop_event.clear()
        
        self.is_recording = True
        self.audio_queue = queue.Queue()
        self._current_recording = []
        
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            callback=self.audio_callback,
            blocksize=self.chunk_size
        )
        self.stream.start()
        self.logger.info("Recording stream started.")
        
        # We need a way to monitor stops if we're in a separate thread, 
        # but usually main.py or record_stop handles this.
        # Added just in case some logic polls is_recording.

    def record_stop(self):
        self.is_recording = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        from core.state_manager import state_manager
        if state_manager.stop_event.is_set():
            self._current_recording = []
            return None

        # Collect all frames currently in queue
        while not self.audio_queue.empty():
            self._current_recording.append(self.audio_queue.get())
        
        self.logger.info("Recording stream stopped.")
        if not self._current_recording:
            return None
        return np.concatenate(self._current_recording).flatten()

    def transcribe(self, audio_data):
        if audio_data is None or len(audio_data) == 0:
            return ""
        
        self.logger.info("Transcribing...")
        try:
            segments, info = self.model.transcribe(audio_data, beam_size=5)
            transcription = " ".join([segment.text for segment in segments]).strip()
            self.logger.info(f"Transcription complete: {transcription}")
            return transcription
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return ""

    def stop_recording(self):
        # Emergency stop or overflow handling
        self.is_recording = False
