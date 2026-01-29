from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QTextEdit, QProgressBar, QFileDialog, QGroupBox,
    QMessageBox, QTabWidget,
)
from PyQt6.QtCore import pyqtSignal, Qt

from src.core.database import Database
from src.core.transcription import (
    TranscriptionWorker,
    export_transcription_txt,
    export_transcription_srt,
    export_transcription_json,
)


class TranscriptionPanel(QWidget):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._current_audio_id: int = 0
        self._current_file: str = ""
        self._worker: TranscriptionWorker | None = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel("Dettagli & Trascrizione")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        # --- Info tab ---
        self.tabs = QTabWidget()

        # Details tab
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(160)
        details_layout.addWidget(self.info_text)

        # Tags section
        tags_group = QGroupBox("Tags")
        tags_layout = QVBoxLayout(tags_group)
        self.tags_label = QLabel("Nessun tag")
        tags_layout.addWidget(self.tags_label)
        details_layout.addWidget(tags_group)

        details_layout.addStretch()
        self.tabs.addTab(details_widget, "Info")

        # Transcription tab
        trans_widget = QWidget()
        trans_layout = QVBoxLayout(trans_widget)

        # Model selection
        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("Modello:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large-v3"])
        self.model_combo.setCurrentText("base")
        model_row.addWidget(self.model_combo)

        model_row.addWidget(QLabel("Lingua:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            "auto", "it", "en", "es", "fr", "de", "pt", "ja", "zh", "ko", "ru",
        ])
        self.lang_combo.setCurrentText("auto")
        model_row.addWidget(self.lang_combo)
        trans_layout.addLayout(model_row)

        # Transcribe button + progress
        action_row = QHBoxLayout()
        self.btn_transcribe = QPushButton("Trascrivi")
        self.btn_transcribe.setObjectName("primary")
        self.btn_transcribe.clicked.connect(self._start_transcription)
        action_row.addWidget(self.btn_transcribe)

        self.btn_cancel = QPushButton("Annulla")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self._cancel_transcription)
        action_row.addWidget(self.btn_cancel)
        trans_layout.addLayout(action_row)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        trans_layout.addWidget(self.progress)

        self.status_label = QLabel("")
        trans_layout.addWidget(self.status_label)

        # Transcription text
        self.trans_text = QTextEdit()
        self.trans_text.setReadOnly(True)
        self.trans_text.setPlaceholderText(
            "La trascrizione apparira' qui..."
        )
        trans_layout.addWidget(self.trans_text)

        # Export buttons
        export_row = QHBoxLayout()
        btn_txt = QPushButton("Esporta TXT")
        btn_txt.clicked.connect(lambda: self._export("txt"))
        export_row.addWidget(btn_txt)

        btn_srt = QPushButton("Esporta SRT")
        btn_srt.clicked.connect(lambda: self._export("srt"))
        export_row.addWidget(btn_srt)

        btn_json = QPushButton("Esporta JSON")
        btn_json.clicked.connect(lambda: self._export("json"))
        export_row.addWidget(btn_json)
        trans_layout.addLayout(export_row)

        self.tabs.addTab(trans_widget, "Trascrizione")

        layout.addWidget(self.tabs)

    def show_audio(self, audio_id: int):
        self._current_audio_id = audio_id
        info = self.db.get_audio(audio_id)
        if not info:
            return

        self._current_file = info["file_path"]

        from src.utils.file_utils import format_duration, format_file_size

        details = (
            f"Titolo: {info['title']}\n"
            f"File: {info['file_name']}\n"
            f"Formato: {info['format'].upper()}\n"
            f"Durata: {format_duration(info['duration'])}\n"
            f"Dimensione: {format_file_size(info['file_size'])}\n"
            f"Sample Rate: {info['sample_rate']} Hz\n"
            f"Canali: {info['channels']}\n"
            f"Bitrate: {info.get('bitrate', 0)} bps\n"
            f"Aggiunto: {info['date_added'][:10]}\n"
            f"Percorso: {info['file_path']}"
        )
        self.info_text.setText(details)

        # Tags
        tags = self.db.get_audio_tags(audio_id)
        if tags:
            self.tags_label.setText(
                ", ".join(t["name"] for t in tags)
            )
        else:
            self.tags_label.setText("Nessun tag")

        # Load transcription if exists
        trans = self.db.get_transcription(audio_id)
        if trans:
            self._display_transcription(trans)
            self.status_label.setText(
                f"Lingua: {trans['language']} | Modello: {trans['model_used']} | "
                f"{trans.get('date_transcribed', '')[:10]}"
            )
        else:
            self.trans_text.clear()
            self.status_label.setText("")

    def _display_transcription(self, trans: dict):
        segments = trans.get("segments", [])
        if segments:
            lines = []
            for seg in segments:
                ts = self._fmt_ts(seg["start"])
                lines.append(f"[{ts}] {seg['text']}")
            self.trans_text.setText("\n".join(lines))
        else:
            self.trans_text.setText(trans.get("full_text", ""))

    @staticmethod
    def _fmt_ts(seconds: float) -> str:
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02d}:{s:02d}"

    def _start_transcription(self):
        if not self._current_file or not self._current_audio_id:
            return

        model = self.model_combo.currentText()
        lang = self.lang_combo.currentText()

        self._worker = TranscriptionWorker(
            self._current_file, model_name=model, language=lang
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.segment_ready.connect(self._on_segment)
        self._worker.finished_transcription.connect(self._on_finished)
        self._worker.error.connect(self._on_error)

        self.btn_transcribe.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.trans_text.clear()
        self.status_label.setText("Trascrizione in corso...")

        self._worker.start()

    def _cancel_transcription(self):
        if self._worker:
            self._worker.cancel()
            self._cleanup_worker()
            self.status_label.setText("Trascrizione annullata")

    def _on_progress(self, pct: int):
        self.progress.setValue(pct)

    def _on_segment(self, seg: dict):
        ts = self._fmt_ts(seg["start"])
        self.trans_text.append(f"[{ts}] {seg['text']}")

    def _on_finished(self, result: dict):
        self.db.save_transcription(
            self._current_audio_id,
            result["full_text"],
            result["language"],
            result["model"],
            result["segments"],
        )
        self.status_label.setText(
            f"Completato | Lingua: {result['language']} | Modello: {result['model']}"
        )
        self._cleanup_worker()

    def _on_error(self, msg: str):
        QMessageBox.warning(self, "Errore trascrizione", msg)
        self.status_label.setText("Errore")
        self._cleanup_worker()

    def _cleanup_worker(self):
        self.btn_transcribe.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.progress.setVisible(False)
        self._worker = None

    def _export(self, fmt: str):
        trans = self.db.get_transcription(self._current_audio_id)
        if not trans:
            QMessageBox.information(
                self, "Esporta",
                "Nessuna trascrizione disponibile per questo file."
            )
            return

        ext_map = {"txt": "Text (*.txt)", "srt": "SRT (*.srt)", "json": "JSON (*.json)"}
        path, _ = QFileDialog.getSaveFileName(
            self, "Esporta trascrizione", "", ext_map.get(fmt, "")
        )
        if not path:
            return

        if fmt == "txt":
            export_transcription_txt(trans, path)
        elif fmt == "srt":
            export_transcription_srt(trans, path)
        elif fmt == "json":
            export_transcription_json(trans, path)

        self.window().statusBar().showMessage(
            f"Trascrizione esportata: {path}", 3000
        )
