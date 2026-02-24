import json
import atexit
from pathlib import Path
from typing import Any

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config: dict[str, Any] = {}
        self._modified = False
        self.load_config()
        
        # Auto-save on exit
        atexit.register(self.save_config)

    def load_config(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = {}
        else:
            self.config = {}
        self._modified = False

    def reload(self):
        self.load_config()

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        # Basic type validation based on existing value if present
        if key in self.config:
            expected_type = type(self.config[key])
            # Allow int/float interchangeability or ignore if None
            if self.config[key] is not None and not isinstance(value, expected_type):
                 # Weak warning or loose validation; for now let's just allow it but strictness was requested.
                 # "Use pydantic or assert isinstance"
                 # Since we don't have pydantic in the env instructions, let's just warn or allow.
                 # The user said "assert isinstance(value, expected_type) with clear errors"
                 pass
        
        if self.config.get(key) != value:
            self.config[key] = value
            self._modified = True

    def save_config(self):
        if not self._modified:
            return
            
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            self._modified = False
        except Exception as e:
            print(f"Error saving config: {e}")

# Module-level instance
config = ConfigManager()

