from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal, Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QMouseEvent, QLinearGradient


class WaveformWidget(QWidget):
    position_clicked = pyqtSignal(float)  # ratio 0..1
    selection_changed = pyqtSignal(float, float)  # start, end ratios

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: list[float] = []
        self._position: float = 0.0  # 0..1
        self._selection_start: float = -1
        self._selection_end: float = -1
        self._dragging = False
        self._selecting = False
        self.setMinimumHeight(80)
        self.setMaximumHeight(120)

    def set_data(self, data: list[float]):
        self._data = data
        self._position = 0
        self._selection_start = -1
        self._selection_end = -1
        self.update()

    def set_position(self, ratio: float):
        self._position = max(0.0, min(1.0, ratio))
        self.update()

    def clear_selection(self):
        self._selection_start = -1
        self._selection_end = -1
        self.update()

    def get_selection(self) -> tuple[float, float] | None:
        if self._selection_start < 0 or self._selection_end < 0:
            return None
        s = min(self._selection_start, self._selection_end)
        e = max(self._selection_start, self._selection_end)
        return (s, e)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()

        # Background
        painter.fillRect(0, 0, w, h, QColor("#1a1a2e"))

        if not self._data:
            painter.setPen(QColor("#45475a"))
            painter.drawText(
                QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter,
                "Nessun audio caricato"
            )
            painter.end()
            return

        # Selection highlight
        if self._selection_start >= 0 and self._selection_end >= 0:
            s = min(self._selection_start, self._selection_end)
            e = max(self._selection_start, self._selection_end)
            sx = int(s * w)
            ex = int(e * w)
            painter.fillRect(sx, 0, ex - sx, h, QColor(137, 180, 250, 40))

        # Waveform bars
        mid = h / 2
        n = len(self._data)
        bar_w = max(1, w / n)

        gradient = QLinearGradient(0, 0, 0, h)
        gradient.setColorAt(0, QColor("#89b4fa"))
        gradient.setColorAt(0.5, QColor("#74c7ec"))
        gradient.setColorAt(1, QColor("#89b4fa"))

        played_gradient = QLinearGradient(0, 0, 0, h)
        played_gradient.setColorAt(0, QColor("#a6e3a1"))
        played_gradient.setColorAt(0.5, QColor("#94e2d5"))
        played_gradient.setColorAt(1, QColor("#a6e3a1"))

        pos_x = self._position * w

        for i, val in enumerate(self._data):
            x = i * bar_w
            bar_h = val * (mid - 4)
            if bar_h < 1:
                bar_h = 1

            if x < pos_x:
                painter.setBrush(played_gradient)
            else:
                painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRectF(x, mid - bar_h, max(bar_w - 1, 1), bar_h * 2))

        # Position line
        pen = QPen(QColor("#f38ba8"), 2)
        painter.setPen(pen)
        px = int(pos_x)
        painter.drawLine(px, 0, px, h)

        painter.end()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self._selecting = True
                self._selection_start = event.position().x() / self.width()
                self._selection_end = self._selection_start
            else:
                self._dragging = True
                ratio = event.position().x() / self.width()
                self._position = max(0.0, min(1.0, ratio))
                self.position_clicked.emit(self._position)
                self.clear_selection()
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging:
            ratio = event.position().x() / self.width()
            self._position = max(0.0, min(1.0, ratio))
            self.position_clicked.emit(self._position)
            self.update()
        elif self._selecting:
            self._selection_end = max(
                0.0, min(1.0, event.position().x() / self.width())
            )
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._selecting:
            self._selecting = False
            sel = self.get_selection()
            if sel:
                self.selection_changed.emit(sel[0], sel[1])
        self._dragging = False
