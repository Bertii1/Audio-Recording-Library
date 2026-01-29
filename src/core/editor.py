from pydub import AudioSegment
from pathlib import Path
from copy import deepcopy


class EditOperation:
    def __init__(self, description: str, segment_before: AudioSegment):
        self.description = description
        self.segment_before = segment_before


class AudioEditor:
    def __init__(self):
        self._segment: AudioSegment | None = None
        self._original_path: str = ""
        self._undo_stack: list[EditOperation] = []
        self._redo_stack: list[EditOperation] = []
        self.max_undo = 20

    @property
    def is_loaded(self) -> bool:
        return self._segment is not None

    @property
    def segment(self) -> AudioSegment | None:
        return self._segment

    @property
    def duration_ms(self) -> int:
        return len(self._segment) if self._segment else 0

    def load(self, file_path: str) -> bool:
        try:
            self._segment = AudioSegment.from_file(file_path)
            self._original_path = file_path
            self._undo_stack.clear()
            self._redo_stack.clear()
            return True
        except Exception:
            return False

    def _push_undo(self, description: str):
        if self._segment is None:
            return
        if len(self._undo_stack) >= self.max_undo:
            self._undo_stack.pop(0)
        self._undo_stack.append(EditOperation(description, self._segment))
        self._redo_stack.clear()

    def undo(self) -> bool:
        if not self._undo_stack or self._segment is None:
            return False
        op = self._undo_stack.pop()
        self._redo_stack.append(EditOperation("redo", self._segment))
        self._segment = op.segment_before
        return True

    def redo(self) -> bool:
        if not self._redo_stack or self._segment is None:
            return False
        op = self._redo_stack.pop()
        self._undo_stack.append(EditOperation("undo", self._segment))
        self._segment = op.segment_before
        return True

    @property
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def trim(self, start_ms: int, end_ms: int) -> bool:
        if self._segment is None:
            return False
        self._push_undo("trim")
        self._segment = self._segment[start_ms:end_ms]
        return True

    def cut_section(self, start_ms: int, end_ms: int) -> bool:
        if self._segment is None:
            return False
        self._push_undo("cut")
        before = self._segment[:start_ms]
        after = self._segment[end_ms:]
        self._segment = before + after
        return True

    def split(self, split_points_ms: list[int]) -> list[AudioSegment]:
        if self._segment is None:
            return []
        points = sorted(set(split_points_ms))
        parts = []
        prev = 0
        for pt in points:
            if 0 < pt < len(self._segment):
                parts.append(self._segment[prev:pt])
                prev = pt
        parts.append(self._segment[prev:])
        return parts

    def normalize(self, target_dbfs: float = -20.0) -> bool:
        if self._segment is None:
            return False
        self._push_undo("normalize")
        diff = target_dbfs - self._segment.dBFS
        self._segment = self._segment.apply_gain(diff)
        return True

    def change_volume(self, db: float) -> bool:
        if self._segment is None:
            return False
        self._push_undo("volume")
        self._segment = self._segment.apply_gain(db)
        return True

    def export(self, output_path: str, fmt: str = "mp3",
               bitrate: str = "192k") -> bool:
        if self._segment is None:
            return False
        try:
            params = {}
            if fmt == "mp3":
                params["bitrate"] = bitrate
            self._segment.export(output_path, format=fmt, **params)
            return True
        except Exception:
            return False

    def export_parts(self, parts: list[AudioSegment], output_dir: str,
                     base_name: str, fmt: str = "mp3") -> list[str]:
        paths = []
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        for i, part in enumerate(parts, 1):
            name = f"{base_name}_part{i:03d}.{fmt}"
            path = str(Path(output_dir) / name)
            try:
                part.export(path, format=fmt)
                paths.append(path)
            except Exception:
                pass
        return paths

    def get_waveform_data(self, num_points: int = 800) -> list[float]:
        if self._segment is None:
            return []
        import numpy as np
        samples = np.array(self._segment.get_array_of_samples(), dtype=np.float64)
        if self._segment.channels == 2:
            samples = samples[::2]
        if len(samples) == 0:
            return []
        chunk_size = max(1, len(samples) // num_points)
        points = []
        for i in range(0, len(samples), chunk_size):
            chunk = samples[i : i + chunk_size]
            points.append(float(np.max(np.abs(chunk))))
        if points:
            mx = max(points)
            if mx > 0:
                points = [p / mx for p in points]
        return points[:num_points]
