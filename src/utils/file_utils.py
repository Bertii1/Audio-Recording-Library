import os
import re
from pathlib import Path
from datetime import datetime

from mutagen import File as MutagenFile
from pydub import AudioSegment

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}


def is_audio_file(path: str) -> bool:
    return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS


def scan_folder(folder: str) -> list[str]:
    results = []
    for root, _, files in os.walk(folder):
        for f in files:
            full = os.path.join(root, f)
            if is_audio_file(full):
                results.append(full)
    return sorted(results)


def get_audio_metadata(path: str) -> dict:
    p = Path(path)
    stat = p.stat()
    meta = {
        "file_path": str(p.resolve()),
        "file_name": p.name,
        "title": p.stem,
        "format": p.suffix.lstrip(".").lower(),
        "file_size": stat.st_size,
        "date_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "date_added": datetime.now().isoformat(),
        "duration": 0.0,
        "sample_rate": 0,
        "channels": 0,
        "bitrate": 0,
    }

    try:
        mf = MutagenFile(path)
        if mf is not None:
            if mf.info:
                meta["duration"] = round(mf.info.length, 2)
                meta["sample_rate"] = getattr(mf.info, "sample_rate", 0)
                meta["channels"] = getattr(mf.info, "channels", 0)
                meta["bitrate"] = getattr(mf.info, "bitrate", 0)
    except Exception:
        try:
            seg = AudioSegment.from_file(path)
            meta["duration"] = round(len(seg) / 1000.0, 2)
            meta["sample_rate"] = seg.frame_rate
            meta["channels"] = seg.channels
        except Exception:
            pass

    return meta


def format_duration(seconds: float) -> str:
    if seconds <= 0:
        return "0:00"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_file_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def apply_rename_pattern(pattern: str, metadata: dict, index: int = 1) -> str:
    now = datetime.now()
    replacements = {
        "[titolo]": metadata.get("title", "untitled"),
        "[title]": metadata.get("title", "untitled"),
        "[data]": now.strftime("%Y-%m-%d"),
        "[date]": now.strftime("%Y-%m-%d"),
        "[numero]": str(index).zfill(3),
        "[number]": str(index).zfill(3),
        "[formato]": metadata.get("format", ""),
        "[format]": metadata.get("format", ""),
    }
    result = pattern
    for key, val in replacements.items():
        result = result.replace(key, val)
    result = re.sub(r'[<>:"/\\|?*]', '_', result)
    return result
