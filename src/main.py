#!/usr/bin/env python3
"""Audio Library Manager - Main entry point."""

import sys
import os
import traceback


def _setup_path():
    """Ensure imports work both from source and from PyInstaller bundle."""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base not in sys.path:
        sys.path.insert(0, base)


def _show_error(title: str, message: str):
    """Show error in a GUI dialog even if the main app fails to start."""
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, title, message)
    except Exception:
        print(f"ERRORE: {title}\n{message}", file=sys.stderr)


def main():
    _setup_path()

    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        _show_error(
            "Dipendenza mancante",
            "PyQt6 non e' installato.\n"
            "Esegui: pip install PyQt6"
        )
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("Audio Library Manager")
    app.setOrganizationName("AudioLibManager")

    try:
        from src.ui.main_window import MainWindow
        window = MainWindow()
        window.show()
    except Exception as e:
        _show_error(
            "Errore all'avvio",
            f"Impossibile avviare l'applicazione:\n\n{e}\n\n"
            f"Dettagli:\n{traceback.format_exc()}"
        )
        sys.exit(1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
