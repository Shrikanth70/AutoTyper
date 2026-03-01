import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class SettingsWindow:
    def __init__(self, current_config, on_save_callback):
        self.config = current_config
        self.on_save = on_save_callback
        self.root = tk.Tk()
        self.root.title("AutoTyper Settings")
        self.root.geometry("400x500")
        self.setup_ui()
        self.root.focus_force()
        self.root.mainloop()

    def setup_ui(self):
        # Padding
        padding = {'padx': 10, 'pady': 5}
        
        # Notebook for tabs
        nb = ttk.Notebook(self.root)
        nb.pack(expand=True, fill='both')

        # Tab 1: General/Typing
        typing_tab = ttk.Frame(nb)
        nb.add(typing_tab, text='Typing')
        
        ttk.Label(typing_tab, text="Typing Speed (seconds delay):").pack(**padding)
        self.speed_var = tk.DoubleVar(value=self.config['typing']['speed'])
        ttk.Entry(typing_tab, textvariable=self.speed_var).pack(**padding)

        ttk.Label(typing_tab, text="Initial Delay (s) before typing:").pack(**padding)
        self.init_delay_var = tk.DoubleVar(value=self.config['typing']['initial_delay'])
        ttk.Entry(typing_tab, textvariable=self.init_delay_var).pack(**padding)

        self.human_delay_var = tk.BooleanVar(value=self.config['typing']['human_like_delay'])
        ttk.Checkbutton(typing_tab, text="Human-like Delay (Random Variance)", variable=self.human_delay_var).pack(**padding)

        self.paste_mode_var = tk.BooleanVar(value=self.config['typing']['paste_mode'])
        ttk.Checkbutton(typing_tab, text="Use Paste Mode (Instantly paste text)", variable=self.paste_mode_var).pack(**padding)

        # Tab 2: Hotkeys
        hotkey_tab = ttk.Frame(nb)
        nb.add(hotkey_tab, text='Hotkeys')
        
        ttk.Label(hotkey_tab, text="Clipboard Mode:").pack(**padding)
        self.hk_clip = tk.StringVar(value=self.config['hotkeys']['clipboard_mode'])
        ttk.Entry(hotkey_tab, textvariable=self.hk_clip).pack(**padding)

        ttk.Label(hotkey_tab, text="Voice Mode:").pack(**padding)
        self.hk_voice = tk.StringVar(value=self.config['hotkeys']['voice_mode'])
        ttk.Entry(hotkey_tab, textvariable=self.hk_voice).pack(**padding)

        ttk.Label(hotkey_tab, text="Emergency Stop:").pack(**padding)
        self.hk_stop = tk.StringVar(value=self.config['hotkeys']['emergency_stop'])
        ttk.Entry(hotkey_tab, textvariable=self.hk_stop).pack(**padding)

        # Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(side='bottom', fill='x', **padding)
        
        ttk.Button(btn_frame, text="Save Settings", command=self.save).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.root.destroy).pack(side='right', padx=5)

    def save(self):
        try:
            new_config = {
                "hotkeys": {
                    "clipboard_mode": self.hk_clip.get().strip(),
                    "voice_mode": self.hk_voice.get().strip(),
                    "emergency_stop": self.hk_stop.get().strip()
                },
                "typing": {
                    "speed": float(self.speed_var.get()),
                    "initial_delay": float(self.init_delay_var.get()),
                    "human_like_delay": self.human_delay_var.get(),
                    "paste_mode": self.paste_mode_var.get()
                },
                "voice": self.config['voice'], # Keep voice settings from current
                "startup": self.config.get('startup', {"enabled": False}),
                "logging": self.config.get('logging', {"level": "INFO"})
            }

            # Write to file
            with open('config.json', 'w') as f:
                json.dump(new_config, f, indent=4)
            
            if self.on_save:
                self.on_save(new_config)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

if __name__ == "__main__":
    # Test UI standalone
    default_cfg = {
        "hotkeys": {"clipboard_mode": "ctrl+alt+v", "voice_mode": "ctrl+alt+s", "emergency_stop": "ctrl+alt+x"},
        "typing": {"speed": 0.05, "initial_delay": 0.5, "human_like_delay": True, "paste_mode": False},
        "voice": {"model_size": "tiny", "device": "cpu", "compute_type": "int8", "silence_timeout": 1.5}
    }
    SettingsWindow(default_cfg, None)
