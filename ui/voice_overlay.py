import tkinter as tk
import threading
import time

class VoiceOverlay:
    def __init__(self):
        self.root = None
        self.label = None
        self.running = False
        self.should_show = False
        self._lock = threading.Lock()
        # Start a persistent UI thread that waits for show requests
        self._thread = threading.Thread(target=self._ui_loop, daemon=True)
        self._thread.start()

    def show(self):
        with self._lock:
            self.should_show = True

    def hide(self):
        with self._lock:
            self.should_show = False

    def _ui_loop(self):
        """Persistent loop that creates/destroys root as needed."""
        while True:
            if self.should_show and not self.root:
                self._create_root()
            elif not self.should_show and self.root:
                self._destroy_root()
            time.sleep(0.1)

    def _create_root(self):
        try:
            self.root = tk.Tk()
            self.running = True
            self.root.title("AutoTyper Listening")
            self.root.overrideredirect(True)
            self.root.attributes("-topmost", True)
            self.root.attributes("-alpha", 0.9)
            self.root.configure(bg="#1e1e1e")

            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            width, height = 250, 100
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            self.root.geometry(f"{width}x{height}+{x}+{y}")

            frame = tk.Frame(self.root, bg="#1e1e1e", highlightthickness=1, highlightbackground="#3d3d3d")
            frame.pack(expand=True, fill='both')

            tk.Label(frame, text="🎙", font=("Segoe UI Emoji", 24), bg="#1e1e1e", fg="#ff4b4b").pack(pady=(10,0))
            self.label = tk.Label(frame, text="Listening...", font=("Segoe UI", 12, "bold"), bg="#1e1e1e", fg="white")
            self.label.pack()
            tk.Label(frame, text="Press 'L' to stop", font=("Segoe UI", 9), bg="#1e1e1e", fg="#aaaaaa").pack(pady=(0,10))

            self._animate()
            
            # Check for hide request within mainloop
            def check_hide():
                if not self.should_show:
                    self._destroy_root()
                elif self.root:
                    self.root.after(100, check_hide)
            
            self.root.after(100, check_hide)
            self.root.mainloop()
        except Exception:
            self.root = None

    def _destroy_root(self):
        if self.root:
            try:
                self.root.quit() # Stop mainloop
                self.root.destroy()
            except:
                pass
            self.root = None
            self.running = False

    def _animate(self):
        if not self.root or not self.label: return
        try:
            current_text = self.label.cget("text")
            if "..." in current_text: self.label.config(text="Listening")
            else: self.label.config(text=current_text + ".")
            self.root.after(500, self._animate)
        except:
            pass

# Example usage/test
if __name__ == "__main__":
    overlay = VoiceOverlay()
    overlay.show()
    time.sleep(5)
    overlay.hide()
