import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider,
    QLabel, QFileDialog, QMessageBox, QGroupBox, QSpinBox,
    QComboBox,
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from src.core.editor import AudioEditor
from src.ui.waveform_widget import WaveformWidget
from src.utils.file_utils import format_duration


class PlayerPanel(QWidget):
    edit_applied = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = AudioEditor()
        self._current_file: str = ""
        self._current_audio_id: int = 0
        self._duration_ms: int = 0

        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)
        self._audio_output.setVolume(0.7)

        self._timer = QTimer()
        self._timer.setInterval(50)
        self._timer.timeout.connect(self._update_position)

        self._player.durationChanged.connect(self._on_duration)
        self._player.mediaStatusChanged.connect(self._on_status)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel("Player / Editor")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        self.file_label = QLabel("Nessun file caricato")
        layout.addWidget(self.file_label)

        # Waveform
        self.waveform = WaveformWidget()
        self.waveform.position_clicked.connect(self._seek_ratio)
        self.waveform.selection_changed.connect(self._on_waveform_selection)
        layout.addWidget(self.waveform)

        # Time display
        time_row = QHBoxLayout()
        self.time_label = QLabel("0:00")
        self.time_label.setFixedWidth(60)
        time_row.addWidget(self.time_label)

        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.sliderPressed.connect(self._slider_pressed)
        self.seek_slider.sliderReleased.connect(self._slider_released)
        self.seek_slider.sliderMoved.connect(self._slider_moved)
        time_row.addWidget(self.seek_slider)

        self.duration_label = QLabel("0:00")
        self.duration_label.setFixedWidth(60)
        self.duration_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        time_row.addWidget(self.duration_label)
        layout.addLayout(time_row)

        # Playback controls
        ctrl_row = QHBoxLayout()
        ctrl_row.addStretch()

        self.btn_stop = QPushButton("\u23F9")
        self.btn_stop.setFixedSize(36, 36)
        self.btn_stop.clicked.connect(self.stop)
        ctrl_row.addWidget(self.btn_stop)

        self.btn_play = QPushButton("\u25B6")
        self.btn_play.setFixedSize(48, 48)
        self.btn_play.setObjectName("primary")
        self.btn_play.clicked.connect(self.toggle_play)
        ctrl_row.addWidget(self.btn_play)

        self.btn_skip = QPushButton("\u23ED")
        self.btn_skip.setFixedSize(36, 36)
        ctrl_row.addWidget(self.btn_skip)

        ctrl_row.addSpacing(16)

        vol_label = QLabel("Vol:")
        ctrl_row.addWidget(vol_label)
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(70)
        self.vol_slider.setFixedWidth(100)
        self.vol_slider.valueChanged.connect(
            lambda v: self._audio_output.setVolume(v / 100)
        )
        ctrl_row.addWidget(self.vol_slider)

        ctrl_row.addStretch()
        layout.addLayout(ctrl_row)

        # Editor section
        edit_group = QGroupBox("Editing")
        edit_layout = QVBoxLayout(edit_group)

        # Selection info
        sel_row = QHBoxLayout()
        sel_row.addWidget(QLabel("Selezione:"))
        self.sel_start_label = QLabel("--")
        sel_row.addWidget(self.sel_start_label)
        sel_row.addWidget(QLabel("-"))
        self.sel_end_label = QLabel("--")
        sel_row.addWidget(self.sel_end_label)
        sel_row.addStretch()
        edit_layout.addLayout(sel_row)

        # Edit buttons row 1
        edit_row1 = QHBoxLayout()

        btn_trim = QPushButton("Trim selezione")
        btn_trim.clicked.connect(self._trim_selection)
        edit_row1.addWidget(btn_trim)

        btn_cut = QPushButton("Taglia selezione")
        btn_cut.clicked.connect(self._cut_selection)
        edit_row1.addWidget(btn_cut)

        btn_normalize = QPushButton("Normalizza")
        btn_normalize.clicked.connect(self._normalize)
        edit_row1.addWidget(btn_normalize)

        edit_layout.addLayout(edit_row1)

        # Edit buttons row 2
        edit_row2 = QHBoxLayout()

        btn_undo = QPushButton("Annulla")
        btn_undo.clicked.connect(self._undo)
        edit_row2.addWidget(btn_undo)

        btn_redo = QPushButton("Ripeti")
        btn_redo.clicked.connect(self._redo)
        edit_row2.addWidget(btn_redo)

        edit_row2.addStretch()

        btn_export = QPushButton("Esporta...")
        btn_export.setObjectName("primary")
        btn_export.clicked.connect(self._export)
        edit_row2.addWidget(btn_export)

        edit_layout.addLayout(edit_row2)

        layout.addWidget(edit_group)
        layout.addStretch()

    def load_file(self, file_path: str, audio_id: int = 0):
        self.stop()
        self._current_file = file_path
        self._current_audio_id = audio_id

        name = os.path.basename(file_path)
        self.file_label.setText(name)

        self._player.setSource(QUrl.fromLocalFile(file_path))
        self.editor.load(file_path)

        waveform_data = self.editor.get_waveform_data(800)
        self.waveform.set_data(waveform_data)

    def toggle_play(self):
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
            self._timer.stop()
            self.btn_play.setText("\u25B6")
        else:
            self._player.play()
            self._timer.start()
            self.btn_play.setText("\u23F8")

    def stop(self):
        self._player.stop()
        self._timer.stop()
        self.btn_play.setText("\u25B6")
        self.waveform.set_position(0)
        self.seek_slider.setValue(0)
        self.time_label.setText("0:00")

    def _on_duration(self, ms):
        self._duration_ms = ms
        self.duration_label.setText(format_duration(ms / 1000))

    def _on_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.stop()

    def _update_position(self):
        if self._duration_ms <= 0:
            return
        pos = self._player.position()
        ratio = pos / self._duration_ms
        self.waveform.set_position(ratio)
        self.seek_slider.setValue(int(ratio * 1000))
        self.time_label.setText(format_duration(pos / 1000))

    def _seek_ratio(self, ratio: float):
        if self._duration_ms > 0:
            self._player.setPosition(int(ratio * self._duration_ms))

    def _slider_pressed(self):
        self._timer.stop()

    def _slider_released(self):
        val = self.seek_slider.value() / 1000
        self._seek_ratio(val)
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._timer.start()

    def _slider_moved(self, val):
        ratio = val / 1000
        self.waveform.set_position(ratio)
        if self._duration_ms > 0:
            self.time_label.setText(
                format_duration(ratio * self._duration_ms / 1000)
            )

    def _on_waveform_selection(self, start: float, end: float):
        if self._duration_ms > 0:
            s_ms = start * self._duration_ms
            e_ms = end * self._duration_ms
            self.sel_start_label.setText(format_duration(s_ms / 1000))
            self.sel_end_label.setText(format_duration(e_ms / 1000))

    def _get_selection_ms(self) -> tuple[int, int] | None:
        sel = self.waveform.get_selection()
        if sel is None:
            QMessageBox.information(
                self, "Selezione",
                "Seleziona una porzione del waveform\n"
                "(Shift + click e trascina)"
            )
            return None
        s = int(sel[0] * self.editor.duration_ms)
        e = int(sel[1] * self.editor.duration_ms)
        return (s, e)

    def _trim_selection(self):
        sel = self._get_selection_ms()
        if sel and self.editor.trim(sel[0], sel[1]):
            self._reload_from_editor()

    def _cut_selection(self):
        sel = self._get_selection_ms()
        if sel and self.editor.cut_section(sel[0], sel[1]):
            self._reload_from_editor()

    def _normalize(self):
        if self.editor.normalize():
            self._reload_from_editor()

    def _undo(self):
        if self.editor.undo():
            self._reload_from_editor()

    def _redo(self):
        if self.editor.redo():
            self._reload_from_editor()

    def _reload_from_editor(self):
        self.stop()
        data = self.editor.get_waveform_data(800)
        self.waveform.set_data(data)
        self.waveform.clear_selection()
        self.sel_start_label.setText("--")
        self.sel_end_label.setText("--")
        self._duration_ms = self.editor.duration_ms
        self.duration_label.setText(format_duration(self._duration_ms / 1000))
        self.edit_applied.emit()

    def _export(self):
        if not self.editor.is_loaded:
            return
        fmt_map = {
            "MP3 (*.mp3)": "mp3",
            "WAV (*.wav)": "wav",
            "FLAC (*.flac)": "flac",
            "OGG (*.ogg)": "ogg",
        }
        filter_str = ";;".join(fmt_map.keys())
        path, selected = QFileDialog.getSaveFileName(
            self, "Esporta audio", "", filter_str
        )
        if path:
            fmt = fmt_map.get(selected, "mp3")
            if self.editor.export(path, fmt):
                self.window().statusBar().showMessage(
                    f"Esportato: {path}", 3000
                )
            else:
                QMessageBox.warning(self, "Errore", "Errore durante l'esportazione")
