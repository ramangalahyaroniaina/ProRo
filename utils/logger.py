from datetime import datetime


class Logger:
    def __init__(self, enable=True):
        self.enable = enable

    def log(self, msg):
        if not self.enable:
            return
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def info(self, msg):
        self.log("INFO: " + msg)

    def success(self, msg):
        self.log("SUCCESS: " + msg)

    def warning(self, msg):
        self.log("WARNING: " + msg)

    def error(self, msg):
        self.log("ERROR: " + msg)