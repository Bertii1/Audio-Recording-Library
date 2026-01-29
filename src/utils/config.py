import json
import os
from pathlib import Path


DEFAULT_CONFIG = {
    "theme": "dark",
    "whisper_model": "base",
    "whisper_language": "auto",
    "default_import_path": "",
    "default_export_path": "",
    "supported_formats": ["mp3", "wav", "m4a", "flac", "ogg"],
    "view_mode": "list",
    "window_geometry": None,
    "recent_folders": [],
}


class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".audio_library_manager"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                self.data.update(saved)
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()
