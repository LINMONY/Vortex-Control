import json
import os
from datetime import datetime

LOGS_FILE = "logs.json"

class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.logs = []
            cls._instance.load_logs()
        return cls._instance

    def load_logs(self):
        if os.path.exists(LOGS_FILE):
            try:
                with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                    self.logs = json.load(f)
            except Exception as e:
                print(f"Error loading logs: {e}")
                self.logs = []
        else:
            self.logs = []

    def log_restore_point(self, name, description="User initiated"):
        entry = {
            "id": int(datetime.now().timestamp()), # Simple ID
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": name,
            "description": description,
            "action": "create"
        }
        self.logs.insert(0, entry) # Newest first
        self.save_logs()
        return entry

    def delete_log(self, log_id):
        self.logs = [log for log in self.logs if log.get("id") != log_id]
        self.save_logs()

    def get_logs(self):
        return self.logs

    def save_logs(self):
        try:
            with open(LOGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving logs: {e}")
