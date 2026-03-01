import logging

class NotificationManager:
    def __init__(self):
        self.logger = logging.getLogger("NotificationManager")
        self.icon = None # Set this from main.py after tray icon is created

    def set_icon(self, icon):
        self.icon = icon

    def notify(self, title, message):
        self.logger.info(f"Notification: {title} - {message}")
        if self.icon:
            # pystray's notify method
            try:
                self.icon.notify(message, title)
            except Exception as e:
                self.logger.error(f"Failed to show notification: {e}")

notification_manager = NotificationManager()
