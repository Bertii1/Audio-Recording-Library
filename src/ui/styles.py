DARK_THEME = """
QMainWindow, QDialog {
    background-color: #1e1e2e;
    color: #cdd6f4;
}
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
}
QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
    border-bottom: 1px solid #313244;
}
QMenuBar::item:selected {
    background-color: #313244;
}
QMenu {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #313244;
}
QMenu::item:selected {
    background-color: #313244;
}
QToolBar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
    spacing: 4px;
    padding: 4px;
}
QToolButton {
    background-color: transparent;
    color: #cdd6f4;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 6px 10px;
}
QToolButton:hover {
    background-color: #313244;
    border-color: #45475a;
}
QToolButton:pressed {
    background-color: #45475a;
}
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 16px;
    min-height: 28px;
}
QPushButton:hover {
    background-color: #45475a;
    border-color: #585b70;
}
QPushButton:pressed {
    background-color: #585b70;
}
QPushButton#primary {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    font-weight: bold;
}
QPushButton#primary:hover {
    background-color: #74c7ec;
}
QLineEdit, QComboBox, QSpinBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 28px;
}
QLineEdit:focus, QComboBox:focus {
    border-color: #89b4fa;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    selection-background-color: #45475a;
}
QTableWidget, QTreeWidget, QListWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    gridline-color: #313244;
    selection-background-color: #313244;
    outline: none;
}
QTableWidget::item, QTreeWidget::item, QListWidget::item {
    padding: 4px;
}
QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #313244;
    color: #cdd6f4;
}
QHeaderView::section {
    background-color: #181825;
    color: #a6adc8;
    border: none;
    border-right: 1px solid #313244;
    border-bottom: 1px solid #313244;
    padding: 6px 8px;
    font-weight: bold;
}
QScrollBar:vertical {
    background: #1e1e2e;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #45475a;
    min-height: 30px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #585b70;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #1e1e2e;
    height: 10px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #45475a;
    min-width: 30px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
    background: #585b70;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}
QSlider::groove:horizontal {
    background: #313244;
    height: 6px;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #89b4fa;
    width: 14px;
    height: 14px;
    margin: -4px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: #89b4fa;
    border-radius: 3px;
}
QProgressBar {
    background-color: #313244;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: #cdd6f4;
    min-height: 18px;
}
QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 4px;
}
QSplitter::handle {
    background-color: #313244;
    width: 2px;
    height: 2px;
}
QTabWidget::pane {
    border: 1px solid #313244;
    border-radius: 6px;
}
QTabBar::tab {
    background-color: #181825;
    color: #a6adc8;
    border: none;
    padding: 8px 16px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #313244;
    color: #cdd6f4;
    border-bottom: 2px solid #89b4fa;
}
QTabBar::tab:hover:!selected {
    background-color: #313244;
}
QGroupBox {
    border: 1px solid #313244;
    border-radius: 6px;
    margin-top: 8px;
    padding-top: 8px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
QLabel#sectionTitle {
    font-size: 15px;
    font-weight: bold;
    color: #89b4fa;
}
QTextEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px;
}
QStatusBar {
    background-color: #181825;
    color: #a6adc8;
    border-top: 1px solid #313244;
}
"""

LIGHT_THEME = """
QMainWindow, QDialog {
    background-color: #eff1f5;
    color: #4c4f69;
}
QWidget {
    background-color: #eff1f5;
    color: #4c4f69;
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
}
QMenuBar {
    background-color: #e6e9ef;
    color: #4c4f69;
    border-bottom: 1px solid #ccd0da;
}
QMenuBar::item:selected {
    background-color: #ccd0da;
}
QMenu {
    background-color: #eff1f5;
    color: #4c4f69;
    border: 1px solid #ccd0da;
}
QMenu::item:selected {
    background-color: #ccd0da;
}
QToolBar {
    background-color: #e6e9ef;
    border-bottom: 1px solid #ccd0da;
    spacing: 4px;
    padding: 4px;
}
QToolButton {
    background-color: transparent;
    color: #4c4f69;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 6px 10px;
}
QToolButton:hover {
    background-color: #ccd0da;
}
QPushButton {
    background-color: #ccd0da;
    color: #4c4f69;
    border: 1px solid #bcc0cc;
    border-radius: 6px;
    padding: 6px 16px;
    min-height: 28px;
}
QPushButton:hover {
    background-color: #bcc0cc;
}
QPushButton#primary {
    background-color: #1e66f5;
    color: #ffffff;
    border: none;
    font-weight: bold;
}
QPushButton#primary:hover {
    background-color: #2a6ef7;
}
QLineEdit, QComboBox, QSpinBox {
    background-color: #ffffff;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 28px;
}
QLineEdit:focus, QComboBox:focus {
    border-color: #1e66f5;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    selection-background-color: #ccd0da;
}
QTableWidget, QTreeWidget, QListWidget {
    background-color: #ffffff;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    gridline-color: #e6e9ef;
    selection-background-color: #ccd0da;
    outline: none;
}
QHeaderView::section {
    background-color: #e6e9ef;
    color: #5c5f77;
    border: none;
    border-right: 1px solid #ccd0da;
    border-bottom: 1px solid #ccd0da;
    padding: 6px 8px;
    font-weight: bold;
}
QScrollBar:vertical {
    background: #eff1f5;
    width: 10px;
}
QScrollBar::handle:vertical {
    background: #bcc0cc;
    min-height: 30px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #acb0be;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #eff1f5;
    height: 10px;
}
QScrollBar::handle:horizontal {
    background: #bcc0cc;
    min-width: 30px;
    border-radius: 5px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QSlider::groove:horizontal {
    background: #ccd0da;
    height: 6px;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #1e66f5;
    width: 14px;
    height: 14px;
    margin: -4px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: #1e66f5;
    border-radius: 3px;
}
QProgressBar {
    background-color: #ccd0da;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: #4c4f69;
    min-height: 18px;
}
QProgressBar::chunk {
    background-color: #1e66f5;
    border-radius: 4px;
}
QSplitter::handle {
    background-color: #ccd0da;
    width: 2px;
    height: 2px;
}
QTabWidget::pane {
    border: 1px solid #ccd0da;
    border-radius: 6px;
}
QTabBar::tab {
    background-color: #e6e9ef;
    color: #5c5f77;
    border: none;
    padding: 8px 16px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #ccd0da;
    color: #4c4f69;
    border-bottom: 2px solid #1e66f5;
}
QGroupBox {
    border: 1px solid #ccd0da;
    border-radius: 6px;
    margin-top: 8px;
    padding-top: 8px;
    font-weight: bold;
}
QLabel#sectionTitle {
    font-size: 15px;
    font-weight: bold;
    color: #1e66f5;
}
QTextEdit {
    background-color: #ffffff;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    padding: 6px;
}
QStatusBar {
    background-color: #e6e9ef;
    color: #5c5f77;
    border-top: 1px solid #ccd0da;
}
"""
