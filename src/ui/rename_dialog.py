from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox,
)
from PyQt6.QtCore import Qt

from src.core.database import Database
from src.core.audio_manager import AudioManager
from src.utils.file_utils import apply_rename_pattern


class BatchRenameDialog(QDialog):
    def __init__(self, db: Database, audio_manager: AudioManager,
                 audio_ids: list[int], parent=None):
        super().__init__(parent)
        self.db = db
        self.audio_manager = audio_manager
        self.audio_ids = audio_ids
        self.setWindowTitle("Rinomina batch")
        self.setMinimumSize(600, 400)
        self._build_ui()
        self._update_preview()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Pattern input
        pat_row = QHBoxLayout()
        pat_row.addWidget(QLabel("Pattern:"))
        self.pattern_input = QLineEdit("[titolo]")
        self.pattern_input.textChanged.connect(self._update_preview)
        pat_row.addWidget(self.pattern_input)

        presets = QComboBox()
        presets.addItems([
            "[titolo]",
            "[data]_[titolo]",
            "[data]_[titolo]_[numero]",
            "[numero]_[titolo]",
        ])
        presets.currentTextChanged.connect(self.pattern_input.setText)
        pat_row.addWidget(presets)
        layout.addLayout(pat_row)

        hint = QLabel("Variabili: [titolo] [data] [numero] [formato]")
        hint.setStyleSheet("color: #a6adc8; font-size: 11px;")
        layout.addWidget(hint)

        # Preview table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Nome attuale", "Nuovo nome"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        layout.addWidget(self.table)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("Annulla")
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_apply = QPushButton("Applica")
        btn_apply.setObjectName("primary")
        btn_apply.clicked.connect(self._apply)
        btn_row.addWidget(btn_apply)
        layout.addLayout(btn_row)

    def _update_preview(self):
        pattern = self.pattern_input.text()
        self.table.setRowCount(len(self.audio_ids))
        self._previews = []
        for i, aid in enumerate(self.audio_ids):
            info = self.db.get_audio(aid)
            if not info:
                continue
            old_name = info["file_name"]
            meta = {
                "title": info["title"],
                "format": info["format"],
            }
            new_stem = apply_rename_pattern(pattern, meta, i + 1)
            new_name = f"{new_stem}.{info['format']}"

            self.table.setItem(i, 0, QTableWidgetItem(old_name))
            self.table.setItem(i, 1, QTableWidgetItem(new_name))
            self._previews.append((aid, new_stem))

    def _apply(self):
        for aid, new_stem in self._previews:
            self.audio_manager.rename_file(aid, new_stem)
        self.accept()
