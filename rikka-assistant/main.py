"""
Application entry point.
Configures logging, creates the Qt application, and launches the main window.
"""
from __future__ import annotations

import logging
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from config import Config
from gui import AssistantWindow


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
    # Silence overly verbose third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def main() -> int:
    _configure_logging()
    log = logging.getLogger(__name__)

    app = QApplication(sys.argv)
    app.setApplicationName("Rikka Assistant")
    app.setApplicationVersion("1.0.0")

    # Enable high-DPI scaling
    app.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Base font
    font = QFont("Segoe UI", 10)
    font.setHintingPreference(QFont.HintingPreference.PreferDefaultHinting)
    app.setFont(font)

    config = Config.load()
    log.info(
        "Loaded config: backend=%s  model=%s",
        config.backend,
        config.ollama_model if config.backend == "ollama" else config.gemini_model,
    )

    window = AssistantWindow(config)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
