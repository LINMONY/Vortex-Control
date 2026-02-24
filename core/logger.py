import json
import atexit
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

LOGS_FILE = Path("logs.json")

class Logger:
    def __init__(self, max_entries: int = 1000):
        """
        Initialize the Logger.
        
        Args:
            max_entries: Maximum number of logs to keep. Defaults to 1000.
        """
        self.max_entries = max_entries
        self.logs: List[Dict[str, Any]] = []
        self._modified = False
        self.load_logs()
        
        # Ensure logs are saved on exit
        atexit.register(self.save_logs)

    def load_logs(self) -> None:
        """
        Load logs from the persistence file.
        """
        if LOGS_FILE.exists():
            try:
                with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                    self.logs = json.load(f)
            except Exception as e:
                print(f"Error loading logs: {e}")
                self.logs = []
        else:
            self.logs = []
        self._modified = False

    def log_system(self, message: str, level: str = "INFO") -> None:
        """
        Log a general system message.
        
        Args:
            message: The content of the log.
            level: Log level (INFO, WARNING, ERROR).
        """
        entry = {
            "id": int(datetime.now().timestamp() * 1000000), # Microsecond precision to avoid conflict
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": f"[{level}] System",
            "description": message,
            "action": "system_log"
        }
        print(f"[{level}] {message}") # Console output
        self.logs.insert(0, entry)
        self._enforce_rotation()
        self._modified = True

    def log_restore_point(self, name: str, description: str = "User initiated") -> Dict[str, Any]:
        """
        Log the creation of a restore point.
        
        Args:
            name: Name of the restore point.
            description: Description or source of request.
            
        Returns:
            The created log entry as a dictionary.
        """
        entry = {
            "id": int(datetime.now().timestamp() * 1000), 
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": name,
            "description": description,
            "action": "create"
        }
        
        self.logs.insert(0, entry) # Newest first
        self._enforce_rotation()
        self._modified = True
        return entry

    def delete_log(self, log_id: int) -> bool:
        initial_len = len(self.logs)
        # Efficiently filter in-place or create new list (O(n))
        self.logs = [log for log in self.logs if log.get("id") != log_id]
        
        if len(self.logs) != initial_len:
            self._modified = True
            return True
        return False

    def get_logs(self) -> List[Dict[str, Any]]:
        return self.logs

    def _enforce_rotation(self) -> None:
        if len(self.logs) > self.max_entries:
            self.logs = self.logs[:self.max_entries]

    def save_logs(self) -> None:
        if not self._modified:
            return

        try:
            with open(LOGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, indent=4, ensure_ascii=False)
            self._modified = False
        except Exception as e:
            print(f"Error saving logs: {e}")

# Module-level instance
logger = Logger()

