import os
from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QToolBar, QStatusBar, QFileDialog,
    QMessageBox, QApplication,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QKeySequence

from src.core.database import Database
from src.core.audio_manager import AudioManager
from src.utils.config import Config
from src.ui.library_panel import LibraryPanel
from src.ui.player_panel import PlayerPanel
from src.ui.transcription_panel import TranscriptionPanel
from src.ui.rename_dialog import BatchRenameDialog
from src.ui.styles import DARK_THEME, LIGHT_THEME


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.db = Database()
        self.audio_manager = AudioManager(self.db)

        self.setWindowTitle("Audio Library Manager")
        self.setMinimumSize(1100, 700)
        self.resize(1400, 800)

        self._apply_theme()
        self._build_menu()
        self._build_toolbar()
        self._build_ui()
        self._build_statusbar()
        self._setup_shortcuts()

        geom = self.config.get("window_geometry")
        if geom:
            try:
                self.restoreGeometry(bytes.fromhex(geom))
            except Exception:
                pass

    def _apply_theme(self):
        theme = self.config.get("theme", "dark")
        if theme == "dark":
            self.setStyleSheet(DARK_THEME)
        else:
            self.setStyleSheet(LIGHT_THEME)

    def _build_menu(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        act_import = QAction("Importa file...", self)
        act_import.setShortcut(QKeySequence("Ctrl+O"))
        act_import.triggered.connect(self._import_files)
        file_menu.addAction(act_import)

        act_folder = QAction("Importa cartella...", self)
        act_folder.setShortcut(QKeySequence("Ctrl+Shift+O"))
        act_folder.triggered.connect(self._import_folder)
        file_menu.addAction(act_folder)

        file_menu.addSeparator()

        act_export_lib = QAction("Esporta libreria (JSON)...", self)
        act_export_lib.triggered.connect(self._export_library_json)
        file_menu.addAction(act_export_lib)

        act_export_csv = QAction("Esporta libreria (CSV)...", self)
        act_export_csv.triggered.connect(self._export_library_csv)
        file_menu.addAction(act_export_csv)

        file_menu.addSeparator()

        act_backup = QAction("Backup database...", self)
        act_backup.triggered.connect(self._backup_db)
        file_menu.addAction(act_backup)

        file_menu.addSeparator()

        act_quit = QAction("Esci", self)
        act_quit.setShortcut(QKeySequence("Ctrl+Q"))
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)

        # Edit menu
        edit_menu = menu_bar.addMenu("&Modifica")

        act_rename_batch = QAction("Rinomina batch...", self)
        act_rename_batch.setShortcut(QKeySequence("Ctrl+R"))
        act_rename_batch.triggered.connect(self._batch_rename)
        edit_menu.addAction(act_rename_batch)

        # View menu
        view_menu = menu_bar.addMenu("&Vista")

        act_toggle_theme = QAction("Cambia tema", self)
        act_toggle_theme.setShortcut(QKeySequence("Ctrl+T"))
        act_toggle_theme.triggered.connect(self._toggle_theme)
        view_menu.addAction(act_toggle_theme)

        act_refresh = QAction("Aggiorna libreria", self)
        act_refresh.setShortcut(QKeySequence("F5"))
        act_refresh.triggered.connect(lambda: self.library_panel.refresh())
        view_menu.addAction(act_refresh)

        # Help menu
        help_menu = menu_bar.addMenu("&?")

        act_about = QAction("Info", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    def _build_toolbar(self):
        toolbar = QToolBar("Azioni")
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction("Importa", self._import_files)
        toolbar.addAction("Cartella", self._import_folder)
        toolbar.addSeparator()
        toolbar.addAction("Rinomina", self._batch_rename)
        toolbar.addSeparator()
        toolbar.addAction("Tema", self._toggle_theme)

    def _build_ui(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.library_panel = LibraryPanel(self.db, self.audio_manager)
        self.player_panel = PlayerPanel()
        self.transcription_panel = TranscriptionPanel(self.db)

        splitter.addWidget(self.library_panel)
        splitter.addWidget(self.player_panel)
        splitter.addWidget(self.transcription_panel)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 3)

        self.setCentralWidget(splitter)

        # Connections
        self.library_panel.audio_selected.connect(self._on_audio_selected)
        self.library_panel.audio_double_clicked.connect(self._on_audio_play)
        self.player_panel.edit_applied.connect(self.library_panel.refresh)

    def _build_statusbar(self):
        status = QStatusBar()
        self.setStatusBar(status)
        total = len(self.db.get_all_audio())
        status.showMessage(f"Pronto | {total} file in libreria")

    def _setup_shortcuts(self):
        pass  # shortcuts handled by menu actions

    def _on_audio_selected(self, audio_id: int):
        self.transcription_panel.show_audio(audio_id)

    def _on_audio_play(self, audio_id: int):
        info = self.db.get_audio(audio_id)
        if not info:
            return
        if not os.path.isfile(info["file_path"]):
            QMessageBox.warning(
                self, "File non trovato",
                f"Il file non esiste:\n{info['file_path']}"
            )
            return
        self.player_panel.load_file(info["file_path"], audio_id)
        self.transcription_panel.show_audio(audio_id)

    def _import_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Importa file audio",
            self.config.get("default_import_path", ""),
            "Audio (*.mp3 *.wav *.m4a *.flac *.ogg);;Tutti (*)",
        )
        if files:
            count = 0
            for f in files:
                if self.audio_manager.import_file(f):
                    count += 1
            self.library_panel.refresh()
            self.statusBar().showMessage(f"Importati {count} file", 3000)

    def _import_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Seleziona cartella",
            self.config.get("default_import_path", ""),
        )
        if folder:
            ids = self.audio_manager.import_folder(folder)
            self.library_panel.refresh()
            self.statusBar().showMessage(
                f"Importati {len(ids)} file da {folder}", 3000
            )

    def _batch_rename(self):
        ids = self.library_panel.get_selected_ids()
        if not ids:
            QMessageBox.information(
                self, "Rinomina batch",
                "Seleziona uno o piu' file dalla libreria."
            )
            return
        dlg = BatchRenameDialog(self.db, self.audio_manager, ids, self)
        if dlg.exec():
            self.library_panel.refresh()
            self.statusBar().showMessage("File rinominati", 3000)

    def _toggle_theme(self):
        current = self.config.get("theme", "dark")
        new_theme = "light" if current == "dark" else "dark"
        self.config.set("theme", new_theme)
        self._apply_theme()

    def _export_library_json(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Esporta libreria", "", "JSON (*.json)"
        )
        if path:
            self.db.export_library_json(path)
            self.statusBar().showMessage(f"Libreria esportata: {path}", 3000)

    def _export_library_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Esporta libreria", "", "CSV (*.csv)"
        )
        if path:
            self.db.export_library_csv(path)
            self.statusBar().showMessage(f"Libreria esportata: {path}", 3000)

    def _backup_db(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Backup database", "", "SQLite (*.db *.sqlite)"
        )
        if path:
            self.db.backup(path)
            self.statusBar().showMessage(f"Backup creato: {path}", 3000)

    def _show_about(self):
        QMessageBox.about(
            self,
            "Audio Library Manager",
            "Audio Library Manager v1.0\n\n"
            "Gestione libreria di registrazioni audio\n"
            "con trascrizione Whisper e editing integrato.\n\n"
            "Python + PyQt6 + faster-whisper + pydub",
        )

    def closeEvent(self, event):
        geom = self.saveGeometry().toHex().data().decode()
        self.config.set("window_geometry", geom)
        event.accept()
