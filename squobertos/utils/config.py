"""
Configuration management for SquobertOS
"""

import json
from pathlib import Path
from typing import Any, Dict


class Config:
    """Manages application configuration using JSON"""

    def __init__(self, config_path: str = "~/.config/squobertos/config.json"):
        self.config_path = Path(config_path).expanduser()
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load configuration from JSON file"""
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                self._config = json.load(f)
        else:
            # Create default config
            self._config = {
                "squobert_ui": {
                    "url": "https://squobert.vercel.app",
                }
            }
            self._save()

    def _save(self) -> None:
        """Save configuration to JSON file"""
        with open(self.config_path, "w") as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation (e.g., 'squobert_ui.url')"""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value using dot notation (e.g., 'squobert_ui.url')"""
        keys = key.split(".")
        config = self._config

        # Navigate to the correct nested dict
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value
        self._save()

    def reload(self) -> None:
        """Reload configuration from file"""
        self._load()


# Global config instance
_config_instance: Config | None = None


def get_config() -> Config:
    """Get the global config instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
