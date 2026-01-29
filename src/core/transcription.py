import json
from pathlib import Path
from datetime import datetime

from PyQt6.QtCore import QThread, pyqtSignal


class TranscriptionWorker(QThread):
    progress = pyqtSignal(int)
    segment_ready = pyqtSignal(dict)
    finished_transcription = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, file_path: str, model_name: str = "base",
                 language: str | None = None, device: str = "cpu",
                 compute_type: str = "int8"):
        super().__init__()
        self.file_path = file_path
        self.model_name = model_name
        self.language = language if language and language != "auto" else None
        self.device = device
        self.compute_type = compute_type
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            from faster_whisper import WhisperModel

            self.progress.emit(5)
            model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
            )
            self.progress.emit(15)

            segments_gen, info = model.transcribe(
                self.file_path,
                language=self.language,
                beam_size=5,
                vad_filter=True,
            )

            detected_lang = info.language
            total_duration = info.duration
            segments_list = []
            full_text_parts = []

            for seg in segments_gen:
                if self._cancelled:
                    return
                seg_dict = {
                    "start": round(seg.start, 2),
                    "end": round(seg.end, 2),
                    "text": seg.text.strip(),
                }
                segments_list.append(seg_dict)
                full_text_parts.append(seg.text.strip())
                self.segment_ready.emit(seg_dict)

                if total_duration > 0:
                    pct = min(95, int(15 + (seg.end / total_duration) * 80))
                    self.progress.emit(pct)

            full_text = " ".join(full_text_parts)
            self.progress.emit(100)
            self.finished_transcription.emit({
                "full_text": full_text,
                "language": detected_lang,
                "model": self.model_name,
                "segments": segments_list,
            })

        except ImportError:
            self.error.emit(
                "faster-whisper non installato.\n"
                "Installa con: pip install faster-whisper"
            )
        except Exception as e:
            self.error.emit(str(e))


def export_transcription_txt(transcription: dict, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(transcription.get("full_text", ""))


def export_transcription_srt(transcription: dict, output_path: str):
    def _fmt_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(transcription.get("segments", []), 1):
            f.write(f"{i}\n")
            f.write(f"{_fmt_time(seg['start'])} --> {_fmt_time(seg['end'])}\n")
            f.write(f"{seg['text']}\n\n")


def export_transcription_json(transcription: dict, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcription, f, indent=2, ensure_ascii=False)
