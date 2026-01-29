import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QAbstractItemView, QMenu, QFileDialog, QMessageBox, QLabel,
    QInputDialog,
)
from PyQt6.QtCore import pyqtSignal, Qt, QMimeData
from PyQt6.QtGui import QAction, QDragEnterEvent, QDropEvent

from src.utils.file_utils import format_duration, format_file_size


class LibraryPanel(QWidget):
    audio_selected = pyqtSignal(int)  # audio_id
    audio_double_clicked = pyqtSignal(int)  # audio_id

    def __init__(self, db, audio_manager, parent=None):
        super().__init__(parent)
        self.db = db
        self.audio_manager = audio_manager
        self._audio_ids: list[int] = []
        self.setAcceptDrops(True)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel("Libreria")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        # Search bar
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cerca titolo, nome file, trascrizione...")
        self.search_input.textChanged.connect(self._on_search)
        search_row.addWidget(self.search_input)

        self.format_filter = QComboBox()
        self.format_filter.addItems(["Tutti", "mp3", "wav", "m4a", "flac", "ogg"])
        self.format_filter.setFixedWidth(80)
        self.format_filter.currentTextChanged.connect(self._on_search)
        search_row.addWidget(self.format_filter)
        layout.addLayout(search_row)

        # Action buttons
        btn_row = QHBoxLayout()

        btn_import = QPushButton("+ File")
        btn_import.clicked.connect(self._import_files)
        btn_row.addWidget(btn_import)

        btn_folder = QPushButton("+ Cartella")
        btn_folder.clicked.connect(self._import_folder)
        btn_row.addWidget(btn_folder)

        btn_row.addStretch()

        self.count_label = QLabel("0 file")
        btn_row.addWidget(self.count_label)
        layout.addLayout(btn_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Titolo", "Durata", "Formato", "Dim.", "Trascritto"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        for col in range(1, 5):
            self.table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents
            )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_selection)
        self.table.doubleClicked.connect(self._on_double_click)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.table)

    def refresh(self):
        self._on_search()

    def _on_search(self):
        query = self.search_input.text().strip()
        fmt = self.format_filter.currentText()
        if fmt == "Tutti":
            fmt = ""
        results = self.db.search_audio(query=query, fmt=fmt)
        self._populate_table(results)

    def _populate_table(self, rows: list[dict]):
        self.table.setRowCount(len(rows))
        self._audio_ids = []
        for i, row in enumerate(rows):
            self._audio_ids.append(row["id"])
            self.table.setItem(i, 0, QTableWidgetItem(row["title"]))
            self.table.setItem(
                i, 1, QTableWidgetItem(format_duration(row["duration"]))
            )
            self.table.setItem(i, 2, QTableWidgetItem(row["format"].upper()))
            self.table.setItem(
                i, 3, QTableWidgetItem(format_file_size(row["file_size"]))
            )
            icon = "\u2713" if row.get("is_transcribed") else ""
            self.table.setItem(i, 4, QTableWidgetItem(icon))

        self.count_label.setText(f"{len(rows)} file")

    def _on_selection(self):
        rows = self.table.selectionModel().selectedRows()
        if rows:
            idx = rows[0].row()
            if 0 <= idx < len(self._audio_ids):
                self.audio_selected.emit(self._audio_ids[idx])

    def _on_double_click(self, index):
        row = index.row()
        if 0 <= row < len(self._audio_ids):
            self.audio_double_clicked.emit(self._audio_ids[row])

    def get_selected_ids(self) -> list[int]:
        rows = self.table.selectionModel().selectedRows()
        return [self._audio_ids[r.row()] for r in rows if r.row() < len(self._audio_ids)]

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        ids = self.get_selected_ids()
        if not ids:
            return

        single = len(ids) == 1

        if single:
            act_play = menu.addAction("Riproduci")
            act_play.triggered.connect(lambda: self.audio_double_clicked.emit(ids[0]))

        act_rename = menu.addAction("Rinomina" if single else f"Rinomina {len(ids)} file")
        act_rename.triggered.connect(lambda: self._rename_selected(ids))

        act_tag = menu.addAction("Aggiungi tag")
        act_tag.triggered.connect(lambda: self._add_tag_to_selected(ids))

        menu.addSeparator()

        act_remove = menu.addAction("Rimuovi dalla libreria")
        act_remove.triggered.connect(lambda: self._remove_selected(ids))

        act_delete = menu.addAction("Elimina file da disco")
        act_delete.triggered.connect(lambda: self._delete_selected(ids))

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _import_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Importa file audio",
            "",
            "Audio (*.mp3 *.wav *.m4a *.flac *.ogg);;Tutti (*)",
        )
        if files:
            count = 0
            for f in files:
                if self.audio_manager.import_file(f):
                    count += 1
            self.refresh()
            self.window().statusBar().showMessage(
                f"Importati {count} file", 3000
            )

    def _import_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleziona cartella")
        if folder:
            ids = self.audio_manager.import_folder(folder)
            self.refresh()
            self.window().statusBar().showMessage(
                f"Importati {len(ids)} file da {folder}", 3000
            )

    def _rename_selected(self, ids: list[int]):
        for aid in ids:
            info = self.db.get_audio(aid)
            if not info:
                continue
            new_name, ok = QInputDialog.getText(
                self, "Rinomina", "Nuovo nome:", text=info["title"]
            )
            if ok and new_name.strip():
                self.audio_manager.rename_file(aid, new_name.strip())
        self.refresh()

    def _add_tag_to_selected(self, ids: list[int]):
        tag_name, ok = QInputDialog.getText(self, "Aggiungi tag", "Nome tag:")
        if ok and tag_name.strip():
            tag_id = self.db.add_tag(tag_name.strip())
            for aid in ids:
                self.db.tag_audio(aid, tag_id)
            self.window().statusBar().showMessage(
                f"Tag '{tag_name.strip()}' aggiunto", 3000
            )

    def _remove_selected(self, ids: list[int]):
        reply = QMessageBox.question(
            self,
            "Conferma",
            f"Rimuovere {len(ids)} file dalla libreria?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            for aid in ids:
                self.audio_manager.remove_from_library(aid, delete_file=False)
            self.refresh()

    def _delete_selected(self, ids: list[int]):
        reply = QMessageBox.warning(
            self,
            "Attenzione",
            f"Eliminare definitivamente {len(ids)} file dal disco?\n"
            "Questa azione non puo' essere annullata.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            for aid in ids:
                self.audio_manager.remove_from_library(aid, delete_file=True)
            self.refresh()

    # Drag & drop
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        count = 0
        for url in urls:
            path = url.toLocalFile()
            if os.path.isfile(path):
                if self.audio_manager.import_file(path):
                    count += 1
            elif os.path.isdir(path):
                ids = self.audio_manager.import_folder(path)
                count += len(ids)
        if count:
            self.refresh()
            self.window().statusBar().showMessage(
                f"Importati {count} file", 3000
            )
