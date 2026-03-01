import os
import json
import threading
import logging
import time
import sys
import asyncio
import websockets
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

# Import core modules
from core.typing_engine import typing_engine
from core.clipboard_engine import clipboard_engine
from core.text_processor import text_processor
from core.shortcut_listener import ShortcutListener
from core.state_manager import state_manager, State
from core.notification_manager import notification_manager
from ui.settings_window import SettingsWindow
from ui.voice_overlay import VoiceOverlay

class AutoTyperApp:
    def __init__(self):
        self.load_config()
        self.setup_logging()
        self.icon = None
        self.listener = None
        self.voice_engine = None 
        self.voice_overlay = VoiceOverlay()
        self.enabled = True
        
        # State change callback
        state_manager.on_state_change = self.on_app_state_change
        
        # Start WebSocket Bridge for Browser Extension
        threading.Thread(target=self.start_ws_server, daemon=True).start()

    def load_config(self):
        config_path = os.path.join(os.getcwd(), 'config.json')
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except Exception:
            self.config = {
                "hotkeys": {"clipboard_mode": "ctrl+alt+v", "voice_mode": "ctrl+alt+s", "emergency_stop": "ctrl+alt+x"},
                "typing": {"speed": 0.05, "initial_delay": 0.5, "human_like_delay": True, "paste_mode": False},
                "voice": {"model_size": "tiny", "device": "cpu", "compute_type": "int8", "silence_timeout": 1.5}
            }

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("AutoTyper")

    def on_app_state_change(self, old_state, new_state):
        self.logger.info(f"App State: {new_state.name}")
        if new_state == State.LISTENING:
            self.voice_overlay.show()
            self.listener.register_l()
        elif old_state == State.LISTENING:
            self.voice_overlay.hide()
            self.listener.unregister_l()
        elif new_state == State.IDLE:
            # When returning to IDLE, ensure everything is clean
            self.voice_overlay.hide()
            self.listener.unregister_l()

    def trigger_clipboard(self):
        if not self.enabled: return
        
        current_state = state_manager.state
        
        if current_state == State.READY_TO_TYPE:
            source = state_manager.active_source
            text = ""
            if source == 'voice':
                text = state_manager.voice_buffer
            elif source == 'clipboard':
                text = state_manager.clipboard_buffer
            
            if text:
                state_manager.stop_event.clear() # Reset stop event before typing
                state_manager.transition_to(State.TYPING)
                threading.Thread(target=self.run_typing, args=(text,)).start()
            else:
                notification_manager.notify("AutoTyper", "Buffer is empty.")
                state_manager.transition_to(State.IDLE)
        
        elif current_state == State.IDLE:
            self.logger.info("Clipboard trigger activated.")
            text = clipboard_engine.get_text()
            clean_text = text_processor.clean_text(text)
            if text_processor.is_valid_typing_text(clean_text):
                state_manager.set_buffers(clipboard=clean_text)
                state_manager.transition_to(State.READY_TO_TYPE, active_source='clipboard')
                # For clipboard mode, we might want to type immediately or wait for another Ctrl+Alt+V
                # The user requirement say "Ctrl+Alt+V types based on active_source"
                # Let's make it consistent: Ctrl+Alt+V once to "load", second time to "type"?
                # Actually, standard behavior is usually immediate for clipboard.
                # But requirement 6 says "types based on active_source".
                # Let's stick to immediate for IDLE -> clipboard, but buffered for voice.
                state_manager.stop_event.clear()
                state_manager.transition_to(State.TYPING)
                threading.Thread(target=self.run_typing, args=(clean_text,)).start()
                self.broadcast_to_browser(clean_text)
        
        else:
            self.logger.warning(f"Trigger ignored in state {current_state.name}")

    def trigger_voice(self):
        if not self.enabled: return
        if state_manager.state != State.IDLE:
            notification_manager.notify("AutoTyper", "System busy.")
            return

        self.logger.info("Voice trigger activated.")
        state_manager.stop_event.clear() # Clear stop event before starting
        
        if self.voice_engine is None:
            notification_manager.notify("AutoTyper", "Loading Voice Engine...")
            from core.voice_engine import VoiceEngine
            v_cfg = self.config['voice']
            self.voice_engine = VoiceEngine(v_cfg['model_size'], v_cfg['device'], v_cfg['compute_type'])
        
        state_manager.transition_to(State.LISTENING)
        self.voice_engine.record_start()

    def trigger_l_stop(self):
        if state_manager.state != State.LISTENING: return
        
        self.logger.info("Manual stop 'L' pressed.")
        if self.voice_engine:
            audio_data = self.voice_engine.record_stop()
            state_manager.transition_to(State.PROCESSING)
            threading.Thread(target=self.run_transcription, args=(audio_data,)).start()

    def run_transcription(self, audio_data):
        if state_manager.stop_event.is_set():
            state_manager.transition_to(State.IDLE)
            return

        text = self.voice_engine.transcribe(audio_data)
        clean_text = text_processor.clean_text(text)
        
        if clean_text and not state_manager.stop_event.is_set():
            state_manager.set_buffers(voice=clean_text)
            state_manager.transition_to(State.READY_TO_TYPE, active_source='voice')
            notification_manager.notify("AutoTyper", "Voice text ready! Press Ctrl+Alt+V to type.")
            # Broadcast to browser extension
            self.broadcast_to_browser(clean_text)
        else:
            state_manager.transition_to(State.IDLE)
            if not state_manager.stop_event.is_set():
                notification_manager.notify("AutoTyper", "No speech detected.")

    def broadcast_to_browser(self, text):
        if hasattr(self, 'ws_clients') and self.ws_clients:
            msg = json.dumps({"action": "type", "text": text})
            
            async def send():
                for client in list(self.ws_clients):
                    try:
                        await client.send(msg)
                    except Exception as e:
                        self.logger.debug(f"Failed to send to client: {e}")
            
            try:
                # Use the existing loop if possible, but this is called from a thread
                # This might need refinement if called from outside the main thread
                # For now, let's use asyncio.run for simplicity if in a separate thread
                asyncio.run(send())
            except Exception as e:
                self.logger.debug(f"Broadcast failed: {e}")

    async def ws_handler(self, websocket):
        if not hasattr(self, 'ws_clients'): self.ws_clients = set()
        self.ws_clients.add(websocket)
        try:
            async for message in websocket:
                pass # Ext doesn't need to talk back yet
        finally:
            self.ws_clients.remove(websocket)

    async def run_ws_server(self):
        async with websockets.serve(self.ws_handler, "localhost", 8765):
            await asyncio.Future() # Run forever

    def start_ws_server(self):
        self.logger.info("WebSocket bridge starting on ws://localhost:8765")
        try:
            asyncio.run(self.run_ws_server())
        except Exception as e:
            self.logger.error(f"WebSocket server failed: {e}")

    def trigger_stop(self):
        self.logger.warning("EMERGENCY STOP TRIGGERED!")
        state_manager.reset() # This sets stop_event and resets state to IDLE
        
        if self.voice_engine:
            self.voice_engine.stop_recording()
        
        # UI cleanup
        self.voice_overlay.hide()
        if self.listener:
            self.listener.unregister_l()
            
        notification_manager.notify("AutoTyper", "Emergency Stop: Reset to IDLE")

    def run_typing(self, text):
        t_cfg = self.config['typing']
        try:
            typing_engine.type_text(
                text, 
                speed=t_cfg['speed'], 
                initial_delay=t_cfg['initial_delay'], 
                human_like=t_cfg['human_like_delay'], 
                paste_mode=t_cfg['paste_mode']
            )
        finally:
            # Only reset and clear if we weren't interrupted by a NEW stop event
            if not state_manager.stop_event.is_set():
                state_manager.clear_buffers()
                state_manager.transition_to(State.IDLE)
            else:
                # If we were stopped, StateManager.reset() already handled it
                pass

    def create_icon_image(self):
        icon_path = os.path.join(os.getcwd(), 'assets', 'icon.ico')
        if os.path.exists(icon_path):
            return Image.open(icon_path)
            
        image = Image.new('RGB', (64, 64), color=(31, 31, 31))
        d = ImageDraw.Draw(image)
        # Draw a simple circle for the icon
        d.ellipse([10, 10, 54, 54], fill=(255, 75, 75))
        return image

    def toggle_enabled(self, icon, item):
        self.enabled = not self.enabled
        self.logger.info(f"App {'Enabled' if self.enabled else 'Disabled'}")

    def open_settings(self, icon, item):
        self.logger.info("Opening settings...")
        SettingsWindow(self.config, self.on_config_save)

    def on_config_save(self, new_config):
        self.config = new_config
        self.logger.info("Config updated. Restarting listener...")
        if self.listener:
            self.listener.stop()
            self.listener = ShortcutListener(
                self.config['hotkeys'], 
                self.trigger_clipboard, 
                self.trigger_voice, 
                self.trigger_stop,
                self.trigger_l_stop
            )
            self.listener.start()

    def exit_app(self, icon, item):
        self.logger.info("Exiting...")
        if self.listener:
            self.listener.stop()
        icon.stop()
        sys.exit(0)

    def run(self):
        # Start shortcut listener
        self.listener = ShortcutListener(
            self.config['hotkeys'], 
            self.trigger_clipboard, 
            self.trigger_voice, 
            self.trigger_stop,
            self.trigger_l_stop
        )
        self.listener.start()

        # System Tray Setup
        menu = Menu(
            MenuItem('Enabled', self.toggle_enabled, checked=lambda item: self.enabled),
            MenuItem('Settings', self.open_settings),
            MenuItem('Ready to Type', lambda: None, enabled=False, visible=lambda item: state_manager.state == State.READY_TO_TYPE),
            MenuItem('Exit', self.exit_app)
        )
        
        icon_img = self.create_icon_image()
        self.icon = Icon("AutoTyper", icon_img, "AutoTyper Service", menu)
        notification_manager.set_icon(self.icon)
        self.icon.run()

if __name__ == "__main__":
    app = AutoTyperApp()
    app.run()
