import os
import json
from utils.logger import get_logger

logger = get_logger()

CONFIG_FILE = "config.json"

class ConfigManager:
    """
    Manages user configuration (API key, paths, model preference) using a JSON file.
    """
    def __init__(self):
        self.config = {
            "api_key": "",
            "base_url": "https://api.deepseek.com",
            "model": "DeepSeek-V3 (Chat)",
            "last_file_dir": "",
            "last_output_dir": ""
        }
        self.load_config()

    def load_config(self):
        """Loads configuration from file."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                logger.info("Configuration loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        else:
            logger.info("No config file found. Using defaults.")

    def save_config(self):
        """Saves current configuration to file."""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info("Configuration saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
