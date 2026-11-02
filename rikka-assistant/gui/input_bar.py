"""
Input bar: auto-expanding plain-text editor, vector action buttons,
privacy toggles (Screen Context & System Tools), and send button.
"""
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from gui.icons import get_vector_icon


class _ExpandingEdit(QPlainTextEdit):
    """
    A QPlainTextEdit that grows vertically with its content (1–5 lines).
    Emits send_requested when Enter is pressed without Shift.
    """

    send_requested = pyqtSignal()

    _LINE_HEIGHT = 20
    _MIN_H = 40
    _MAX_H = 120

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("InputEdit")
        self.setPlaceholderText(
            "Invoke a command…  (Enter ↵ to send  |  Shift+Enter for newline)"
        )
        self.setFixedHeight(self._MIN_H)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.document().contentsChanged.connect(self._adjust_height)

    def _adjust_height(self) -> None:
        doc_h = self.document().size().height()
        margins = self.contentsMargins()
        new_h = int(doc_h) + margins.top() + margins.bottom() + 14
        new_h = max(self._MIN_H, min(new_h, self._MAX_H))
        self.setFixedHeight(new_h)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        enter_keys = (Qt.Key.Key_Return, Qt.Key.Key_Enter)
        if event.key() in enter_keys and not (
            event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        ):
            self.send_requested.emit()
            return
        super().keyPressEvent(event)

    def sizeHint(self) -> QSize:
        return QSize(super().sizeHint().width(), self._MIN_H)


class InputBar(QWidget):
    """
    Bottom bar containing:
      • Action buttons (stats, clear, settings)
      • Privacy toggles (Screen context, Web/Sys tools)
      • Expanding text input + Send button
    """

    send_requested = pyqtSignal(str)
    stats_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    settings_requested = pyqtSignal()

    screen_context_toggled = pyqtSignal(bool)
    system_tools_toggled = pyqtSignal(bool)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("InputBar")
        self._mode = "rikka"
        self._screen_enabled = False
        self._system_enabled = True

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 6, 12, 10)
        root.setSpacing(6)

        # ── Action & Privacy Toggles Row ────────────────────────────
        action_row = QHBoxLayout()
        action_row.setSpacing(6)
        action_row.setContentsMargins(0, 0, 0, 0)

        self._btn_stats = self._make_action_btn("stats", "System hardware metrics")
        self._btn_clear = self._make_action_btn("clear", "Clear conversation history")
        self._btn_settings = self._make_action_btn("settings", "Open Settings dialog")

        self._btn_stats.clicked.connect(self.stats_requested)
        self._btn_clear.clicked.connect(self.clear_requested)
        self._btn_settings.clicked.connect(self.settings_requested)

        action_row.addWidget(self._btn_stats)
        action_row.addWidget(self._btn_clear)
        action_row.addWidget(self._btn_settings)

        action_row.addSpacing(6)

        # Privacy Toggle: Screen Context
        self._btn_screen = QPushButton("Screen: OFF")
        self._btn_screen.setObjectName("PrivacyToggleBtn")
        self._btn_screen.setToolTip("Privacy Toggle: Attach active screen screenshot to queries")
        self._btn_screen.clicked.connect(self._on_toggle_screen)
        action_row.addWidget(self._btn_screen)

        # Privacy Toggle: System & Web Tools
        self._btn_system = QPushButton("Sys/Web: ON")
        self._btn_system.setObjectName("PrivacyToggleBtn")
        self._btn_system.setToolTip("Privacy Toggle: Allow web search and system execution")
        self._btn_system.clicked.connect(self._on_toggle_system)
        action_row.addWidget(self._btn_system)

        action_row.addStretch()
        root.addLayout(action_row)

        # ── Text input + Send row ───────────────────────────────────
        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        input_row.setContentsMargins(0, 0, 0, 0)

        self._edit = _ExpandingEdit()
        self._edit.send_requested.connect(self._on_send)

        self._send_btn = QPushButton()
        self._send_btn.setObjectName("SendBtn")
        self._send_btn.setFixedSize(40, 40)
        self._send_btn.setToolTip("Send message (Enter)")
        self._send_btn.setIcon(get_vector_icon("send", "#FFFFFF", 20))
        self._send_btn.setIconSize(QSize(18, 18))
        self._send_btn.clicked.connect(self._on_send)

        input_row.addWidget(self._edit)
        input_row.addWidget(self._send_btn, alignment=Qt.AlignmentFlag.AlignBottom)
        root.addLayout(input_row)

        self.update_theme_icons("rikka")

    # ------------------------------------------------------------------ #

    def set_privacy_states(self, screen_enabled: bool, system_enabled: bool) -> None:
        self._screen_enabled = screen_enabled
        self._system_enabled = system_enabled
        self._update_privacy_buttons()

    def is_screen_enabled(self) -> bool:
        return self._screen_enabled

    def is_system_enabled(self) -> bool:
        return self._system_enabled

    def _on_toggle_screen(self) -> None:
        self._screen_enabled = not self._screen_enabled
        self._update_privacy_buttons()
        self.screen_context_toggled.emit(self._screen_enabled)

    def _on_toggle_system(self) -> None:
        self._system_enabled = not self._system_enabled
        self._update_privacy_buttons()
        self.system_tools_toggled.emit(self._system_enabled)

    def _update_privacy_buttons(self) -> None:
        color = "#38BDF8" if self._mode == "normal" else "#4ADE80"

        # Screen toggle
        self._btn_screen.setText("Screen: ON" if self._screen_enabled else "Screen: OFF")
        self._btn_screen.setProperty("active", "true" if self._screen_enabled else "false")
        self._btn_screen.setIcon(get_vector_icon("screen", color if self._screen_enabled else "#94A3B8", 16))
        self._btn_screen.setIconSize(QSize(13, 13))
        self._btn_screen.style().unpolish(self._btn_screen)
        self._btn_screen.style().polish(self._btn_screen)

        # System/Web toggle
        self._btn_system.setText("Sys/Web: ON" if self._system_enabled else "Sys/Web: OFF")
        self._btn_system.setProperty("active", "true" if self._system_enabled else "false")
        self._btn_system.setIcon(get_vector_icon("globe", color if self._system_enabled else "#94A3B8", 16))
        self._btn_system.setIconSize(QSize(13, 13))
        self._btn_system.style().unpolish(self._btn_system)
        self._btn_system.style().polish(self._btn_system)

    def update_theme_icons(self, mode: str) -> None:
        """Update button icons according to the active theme palette."""
        color = "#38BDF8" if mode == "normal" else "#AE86FF"
        self._btn_stats.setIcon(get_vector_icon("stats", color, 20))
        self._btn_stats.setIconSize(QSize(18, 18))
        self._btn_clear.setIcon(get_vector_icon("clear", color, 20))
        self._btn_clear.setIconSize(QSize(18, 18))
        self._btn_settings.setIcon(get_vector_icon("settings", color, 20))
        self._btn_settings.setIconSize(QSize(18, 18))
        self._update_privacy_buttons()

    def set_mode(self, mode: str) -> None:
        """Update placeholder text and vector icon colors based on mode."""
        self._mode = mode
        self.update_theme_icons(mode)
        if mode == "normal":
            self._edit.setPlaceholderText(
                "Ask anything…  (Enter ↵ to send  |  Shift+Enter for newline)"
            )
        else:
            self._edit.setPlaceholderText(
                "Invoke a command…  (Enter ↵ to send  |  Shift+Enter for newline)"
            )

    def set_busy(self, busy: bool) -> None:
        """Disable / enable input while the LLM is generating."""
        self._send_btn.setEnabled(not busy)
        self._edit.setReadOnly(busy)
        if busy:
            self._edit.setPlaceholderText("Generating response…")
        else:
            self.set_mode(self._mode)

    def clear_input(self) -> None:
        self._edit.clear()

    def focus_input(self) -> None:
        self._edit.setFocus()

    # ------------------------------------------------------------------ #

    def _on_send(self) -> None:
        text = self._edit.toPlainText().strip()
        if text:
            self.send_requested.emit(text)
            self._edit.clear()

    @staticmethod
    def _make_action_btn(icon_name: str, tooltip: str) -> QPushButton:
        btn = QPushButton()
        btn.setObjectName("ActionBtn")
        btn.setToolTip(tooltip)
        btn.setFixedSize(30, 30)
        return btn
