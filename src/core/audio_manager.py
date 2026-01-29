import os
import shutil
from pathlib import Path

from pydub import AudioSegment

from src.utils.file_utils import get_audio_metadata, is_audio_file, scan_folder
from src.core.database import Database


class AudioManager:
    def __init__(self, db: Database):
        self.db = db

    def import_file(self, file_path: str) -> int | None:
        if not os.path.isfile(file_path) or not is_audio_file(file_path):
            return None
        meta = get_audio_metadata(file_path)
        return self.db.add_audio(meta)

    def import_folder(self, folder_path: str) -> list[int]:
        files = scan_folder(folder_path)
        ids = []
        for f in files:
            aid = self.import_file(f)
            if aid:
                ids.append(aid)
        return ids

    def remove_from_library(self, audio_id: int, delete_file: bool = False):
        if delete_file:
            info = self.db.get_audio(audio_id)
            if info and os.path.isfile(info["file_path"]):
                os.remove(info["file_path"])
        self.db.delete_audio(audio_id)

    def rename_file(self, audio_id: int, new_name: str) -> str | None:
        info = self.db.get_audio(audio_id)
        if not info:
            return None
        old_path = Path(info["file_path"])
        if not old_path.exists():
            return None
        ext = old_path.suffix
        if not new_name.endswith(ext):
            new_name += ext
        new_path = old_path.parent / new_name
        if new_path.exists():
            return None
        old_path.rename(new_path)
        self.db.update_audio(
            audio_id,
            file_path=str(new_path),
            file_name=new_path.name,
            title=new_path.stem,
        )
        return str(new_path)

    def get_audio_segment(self, file_path: str) -> AudioSegment | None:
        try:
            return AudioSegment.from_file(file_path)
        except Exception:
            return None
