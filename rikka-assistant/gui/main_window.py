"""
Main floating assistant window.

Layout:
  TitleBar   — drag handle, window title, backend toggle (Local/Cloud), mode toggle (Rikka/AI Assistant), min/close
  AvatarRow  — animated avatar (Rikka portrait or Frosted Iridescent Orb), name, live engine status badge
  ChatWidget — scrollable message history with streaming tokens
  InputBar   — privacy toggles (Screen Context, System Tools), vector action buttons, expanding text editor, send button
"""
from __future__ import annotations

import math
from typing import Optional

from PyQt6.QtCore import QPoint, QPointF, QRectF, QSize, Qt, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QMouseEvent,
    QPainter,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from config import Config
from llm_engine import LLMEngine
from gui.avatar_widget import AssistantState, AvatarWidget
from gui.chat_widget import ChatWidget
from gui.icons import get_vector_icon
from gui.input_bar import InputBar
from gui.settings_dialog import SettingsDialog
from gui.styles import get_theme_qss
from gui.wave_transition import WaveTransitionOverlay
import tools


# ------------------------------------------------------------------ #
#  Animated Engine Status Badge (Pulsing LED dot + Model info)        #
# ------------------------------------------------------------------ #

class EngineBadge(QWidget):
    """
    Shows active backend (Local vs Cloud) with a breathing LED pulse animation
    and model name.
    """

    def __init__(self, backend: str, model: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._backend = backend
        self._model = model
        self._pulse_phase = 0.0

        self._timer = QTimer(self)
        self._timer.setInterval(35)
        self._timer.timeout.connect(self._on_tick)
        self._timer.start()

        self.setFixedHeight(18)
        self.setToolTip("Active engine connection status")

    def set_engine_info(self, backend: str, model: str) -> None:
        self._backend = backend
        self._model = model
        self._pulse_phase = 0.0
        self.update()

    def _on_tick(self) -> None:
        self._pulse_phase = (self._pulse_phase + 0.08) % (2.0 * math.pi)
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        is_local = (self._backend == "ollama")
        dot_color = QColor("#4ADE80") if is_local else QColor("#38BDF8")

        pulse = 0.5 + 0.5 * math.sin(self._pulse_phase)

        halo_r = 4.0 + 2.5 * pulse
        halo = QRadialGradient(8.0, 9.0, halo_r)
        halo.setColorAt(0.0, QColor(dot_color.red(), dot_color.green(), dot_color.blue(), int(160 * pulse)))
        halo.setColorAt(1.0, QColor(dot_color.red(), dot_color.green(), dot_color.blue(), 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(halo))
        painter.drawEllipse(QPointF(8.0, 9.0), halo_r, halo_r)

        painter.setBrush(QBrush(dot_color))
        painter.drawEllipse(QPointF(8.0, 9.0), 3.2, 3.2)

        tag = "LOCAL" if is_local else "CLOUD"
        display_text = f"{tag} · {self._model}"

        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        painter.setPen(QColor(230, 230, 245, 200))
        painter.drawText(QRectF(20.0, 0.0, 240.0, 18.0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, display_text)

        painter.end()


# ------------------------------------------------------------------ #
#  Draggable Title Bar with Quick Toggles                             #
# ------------------------------------------------------------------ #

class _TitleBar(QWidget):
    """Hosts dragging, title, backend toggle (Local/Cloud), mode toggle (Rikka/AI Mode), and win controls."""

    mode_toggle_requested = pyqtSignal()
    backend_toggle_requested = pyqtSignal()

    def __init__(self, window: QWidget, initial_mode: str, initial_backend: str) -> None:
        super().__init__(window)
        self.setObjectName("TitleBar")
        self._window = window
        self._drag_pos: Optional[QPoint] = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(6)

        grip = QLabel("⠿")
        grip.setStyleSheet("color: rgba(255, 255, 255, 0.35); font-size: 15px;")
        grip.setToolTip("Drag to move assistant")
        layout.addWidget(grip)

        self._title = QLabel("✦  Rikka Assistant")
        self._title.setObjectName("TitleLabel")
        layout.addWidget(self._title)

        layout.addStretch()

        # Backend Toggle Button (Local ⟷ Cloud)
        self._backend_btn = QPushButton()
        self._backend_btn.setObjectName("BackendToggleBtn")
        self._backend_btn.clicked.connect(self.backend_toggle_requested)
        layout.addWidget(self._backend_btn)

        # Mode Toggle Button (Rikka ⟷ AI Assistant Mode)
        self._mode_btn = QPushButton()
        self._mode_btn.setObjectName("ModeToggleBtn")
        self._mode_btn.clicked.connect(self.mode_toggle_requested)
        layout.addWidget(self._mode_btn)

        min_btn = self._win_btn("—", "WinBtn", "Minimise")
        min_btn.clicked.connect(self._window.showMinimized)
        layout.addWidget(min_btn)

        close_btn = self._win_btn("✕", "CloseBtn", "Close")
        close_btn.clicked.connect(self._window.close)
        layout.addWidget(close_btn)

        self.update_buttons(initial_mode, initial_backend)

    def mode_btn_global_center(self) -> QPoint:
        """Return the center point of the mode button relative to the top window."""
        btn_center = self._mode_btn.rect().center()
        return self._mode_btn.mapTo(self._window, btn_center)

    def update_buttons(self, mode: str, backend: str) -> None:
        if mode == "normal":
            self._title.setText("AI Assistant")
            self._mode_btn.setText("✦  Rikka Mode")
            self._mode_btn.setToolTip("Active: AI Assistant Mode. Click for wave transition to Rikka Mode.")
        else:
            self._title.setText("✦  Rikka Assistant")
            self._mode_btn.setText("🫧  AI Mode")
            self._mode_btn.setToolTip("Active: Chunibyo Magic. Click for wave transition to AI Assistant Mode.")

        is_cloud = (backend == "gemini")
        self._backend_btn.setProperty("cloud", "true" if is_cloud else "false")
        self._backend_btn.style().unpolish(self._backend_btn)
        self._backend_btn.style().polish(self._backend_btn)

        if is_cloud:
            self._backend_btn.setText("☁  Cloud")
            self._backend_btn.setIcon(get_vector_icon("cloud", "#38BDF8", 16))
            self._backend_btn.setIconSize(QSize(14, 14))
            self._backend_btn.setToolTip("Running on Cloud via Gemini API. Click to switch to Local (Ollama).")
        else:
            self._backend_btn.setText("⚡  Local")
            self._backend_btn.setIcon(get_vector_icon("local", "#4ADE80", 16))
            self._backend_btn.setIconSize(QSize(14, 14))
            self._backend_btn.setToolTip("Running locally via Ollama. Click to switch to Cloud (Gemini).")

    # ── Drag events ─────────────────────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self._window.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_pos:
            self._window.move(event.globalPosition().toPoint() - self._drag_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    @staticmethod
    def _win_btn(text: str, obj_name: str, tip: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName(obj_name)
        btn.setToolTip(tip)
        btn.setFixedSize(28, 28)
        return btn


# ------------------------------------------------------------------ #
#  Avatar Row with Animated Badge                                     #
# ------------------------------------------------------------------ #

class _AvatarRow(QWidget):
    def __init__(self, avatar_size: int, mode: str, backend: str, model: str) -> None:
        super().__init__()
        self.setObjectName("AvatarRow")
        self._mode = mode

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(14)

        self.avatar = AvatarWidget(avatar_size, mode=mode)
        layout.addWidget(self.avatar)

        text_col = QVBoxLayout()
        text_col.setSpacing(3)

        self._name_lbl = QLabel("Rikka Takanashi" if mode == "rikka" else "AI Assistant")
        self._name_lbl.setObjectName("NameLabel")

        self._badge = EngineBadge(backend, model)

        self._status_lbl = QLabel(self.avatar.status_text())
        self._status_lbl.setObjectName("StatusLabel")

        text_col.addWidget(self._name_lbl)
        text_col.addWidget(self._badge)
        text_col.addWidget(self._status_lbl)
        layout.addLayout(text_col)
        layout.addStretch()

    def set_mode(self, mode: str) -> None:
        self._mode = mode
        self.avatar.set_mode(mode)
        self._name_lbl.setText("Rikka Takanashi" if mode == "rikka" else "AI Assistant")
        self._status_lbl.setText(self.avatar.status_text())

    def set_engine_info(self, backend: str, model: str) -> None:
        self._badge.set_engine_info(backend, model)

    def set_state(self, state: AssistantState) -> None:
        self.avatar.set_state(state)
        self._status_lbl.setText(self.avatar.status_text())


# ------------------------------------------------------------------ #
#  Main Window                                                         #
# ------------------------------------------------------------------ #

class AssistantWindow(QWidget):
    """
    Frameless, transparent, always-on-top desktop assistant.
    Features:
      • Google Pixel-inspired fluid wave transition when changing themes
      • Real-time animated avatar (rotating magic circle / Siri perimeter glow)
      • Privacy-controlled Screen Context & System/Browser tool execution
      • 1-Click Local (Ollama) vs Cloud (Gemini) toggle with animated LED badge
      • 1-Click Rikka Chunibyo vs AI Assistant Mode switch
    """

    def __init__(self, config: Config) -> None:
        super().__init__()
        self._config = config
        self._engine = LLMEngine(config)

        self._setup_window()
        self._build_ui()
        self._apply_theme(self._config.mode, notify=False)

        active_model = self._config.ollama_model if self._config.backend == "ollama" else self._config.gemini_model
        engine_type = "Local (Ollama)" if self._config.backend == "ollama" else "Cloud (Google Gemini)"

        if self._config.mode == "normal":
            self._chat.add_system_message(
                f"✦  AI Assistant is online.\n"
                f"Connected to {engine_type} · {active_model}."
            )
        else:
            self._chat.add_system_message(
                f"👁  The Tyrant's Eye is unsealed! The dark contract is active.\n"
                f"Invoking {engine_type} · {active_model}."
            )

    # ------------------------------------------------------------------ #
    #  Window setup                                                        #
    # ------------------------------------------------------------------ #

    def _setup_window(self) -> None:
        self.setWindowTitle("Rikka Assistant")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(self._config.window_width, self._config.window_height)
        self.move(self._config.window_x, self._config.window_y)

    # ------------------------------------------------------------------ #
    #  UI Construction                                                     #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 14)

        self._frame = QFrame()
        self._frame.setObjectName("MainFrame")
        outer.addWidget(self._frame)

        self._shadow = QGraphicsDropShadowEffect(self)
        self._frame.setGraphicsEffect(self._shadow)

        frame_layout = QVBoxLayout(self._frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        # Title bar
        self._title_bar = _TitleBar(self, self._config.mode, self._config.backend)
        frame_layout.addWidget(self._title_bar)

        # Avatar row with engine badge
        active_model = self._config.ollama_model if self._config.backend == "ollama" else self._config.gemini_model
        self._avatar_row = _AvatarRow(self._config.avatar_size, self._config.mode, self._config.backend, active_model)
        frame_layout.addWidget(self._avatar_row)

        # Chat area
        self._chat = ChatWidget()
        self._chat.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        frame_layout.addWidget(self._chat, stretch=1)

        # Input bar with privacy toggles and vector buttons
        self._input_bar = InputBar()
        self._input_bar.set_privacy_states(
            self._config.screen_context_enabled,
            self._config.system_tools_enabled,
        )
        frame_layout.addWidget(self._input_bar)

        # ── Signal Wiring ────────────────────────────────────────────
        self._title_bar.mode_toggle_requested.connect(self._on_toggle_mode)
        self._title_bar.backend_toggle_requested.connect(self._on_toggle_backend)
        self._input_bar.send_requested.connect(self._on_user_message)
        self._input_bar.stats_requested.connect(self._on_stats)
        self._input_bar.clear_requested.connect(self._on_clear)
        self._input_bar.settings_requested.connect(self._on_settings)
        self._input_bar.screen_context_toggled.connect(self._on_screen_context_toggled)
        self._input_bar.system_tools_toggled.connect(self._on_system_tools_toggled)

    # ------------------------------------------------------------------ #
    #  Theme & Fluid Wave Transition                                      #
    # ------------------------------------------------------------------ #

    def _apply_theme(self, mode: str, notify: bool = False) -> None:
        qss = get_theme_qss(mode)
        self.setStyleSheet(qss)
        self._title_bar.update_buttons(mode, self._config.backend)
        self._avatar_row.set_mode(mode)
        self._input_bar.set_mode(mode)

        if mode == "normal":
            self.setWindowTitle("AI Assistant")
            self._shadow.setBlurRadius(38)
            self._shadow.setOffset(0, 8)
            self._shadow.setColor(QColor(0, 0, 0, 160))
            if notify:
                self._chat.add_system_message(
                    "🫧  AI Assistant Mode activated. High-clarity frosted core online."
                )
        else:
            self.setWindowTitle("Rikka Assistant (Tyrant's Eye)")
            self._shadow.setBlurRadius(36)
            self._shadow.setOffset(0, 6)
            self._shadow.setColor(QColor(35, 10, 60, 200))
            if notify:
                self._chat.add_system_message(
                    "👁  The Tyrant's Eye awakens! Chunibyo Magic mode restored."
                )

    @pyqtSlot()
    def _on_toggle_mode(self) -> None:
        """Trigger a Google Pixel-inspired fluid wave transition between themes."""
        # 1. Capture snapshot before transition
        old_snapshot = self.grab()

        # 2. Determine wave origin (the toggle button center)
        origin = self._title_bar.mode_btn_global_center()

        # 3. Switch mode & config
        new_mode = "normal" if self._config.mode == "rikka" else "rikka"
        self._config.mode = new_mode
        self._config.save()

        # 4. Apply new theme to underlying window
        self._apply_theme(new_mode, notify=True)

        # 5. Spawn fluid wave overlay on top
        WaveTransitionOverlay(self, old_snapshot, origin, to_mode=new_mode)

    @pyqtSlot()
    def _on_toggle_backend(self) -> None:
        """Toggle between Local (Ollama) and Cloud (Gemini) engines."""
        new_backend = "gemini" if self._config.backend == "ollama" else "ollama"
        self._config.backend = new_backend
        self._config.save()

        self._engine = LLMEngine(self._config)

        active_model = self._config.ollama_model if new_backend == "ollama" else self._config.gemini_model
        self._title_bar.update_buttons(self._config.mode, new_backend)
        self._avatar_row.set_engine_info(new_backend, active_model)

        if new_backend == "gemini":
            if not self._config.gemini_api_key.strip():
                self._chat.add_system_message(
                    "⚠️  Switched to Cloud (Gemini), but no API key is configured!\n"
                    "Tap ⚙ Settings to paste your Gemini API key."
                )
            else:
                self._chat.add_system_message(
                    f"☁  Switched to Cloud Engine: Google Gemini ({active_model})."
                )
        else:
            self._chat.add_system_message(
                f"⚡  Switched to Local Engine: Ollama ({active_model}) at {self._config.ollama_base_url}."
            )

    # ------------------------------------------------------------------ #
    #  Privacy Toggles                                                     #
    # ------------------------------------------------------------------ #

    @pyqtSlot(bool)
    def _on_screen_context_toggled(self, enabled: bool) -> None:
        self._config.screen_context_enabled = enabled
        self._config.save()
        if enabled:
            self._chat.add_system_message(
                "👁️  Screen Context: ENABLED. The assistant will capture your screen to assist with queries."
            )
        else:
            self._chat.add_system_message(
                "🔒  Screen Context: DISABLED for privacy. No screen data will be accessed."
            )

    @pyqtSlot(bool)
    def _on_system_tools_toggled(self, enabled: bool) -> None:
        self._config.system_tools_enabled = enabled
        self._config.save()
        if enabled:
            self._chat.add_system_message(
                "🌐  System & Web Tools: ENABLED. Quick web search and app launching active."
            )
        else:
            self._chat.add_system_message(
                "🔒  System & Web Tools: DISABLED."
            )

    # ------------------------------------------------------------------ #
    #  Chat & LLM Slots                                                    #
    # ------------------------------------------------------------------ #

    @pyqtSlot(str)
    def _on_user_message(self, text: str) -> None:
        self._chat.add_user_message(text)

        # 1. Check quick system intent if system tools are enabled
        if self._config.system_tools_enabled:
            intent_result = tools.try_execute_system_intent(text)
            if intent_result:
                self._chat.add_system_message(f"⚡  {intent_result}")
                self._input_bar.focus_input()
                return

        # 2. Capture screen context if enabled
        image_b64: Optional[str] = None
        active_win = ""
        if self._config.screen_context_enabled:
            image_b64, active_win = tools.capture_screen_context()
            tag = f'Active: "{active_win}"' if active_win else "Display captured"
            self._chat.add_system_message(f"📸  Screen context attached ({tag})")

        self._set_state(AssistantState.THINKING)
        self._input_bar.set_busy(True)
        self._chat.start_thinking()

        self._engine.send(
            text,
            on_token=self._on_token,
            on_complete=self._on_complete,
            on_error=self._on_error,
            image_base64=image_b64,
            active_window=active_win,
        )

    @pyqtSlot(str)
    def _on_token(self, token: str) -> None:
        self._set_state(AssistantState.SPEAKING)
        self._chat.on_token(token)

    @pyqtSlot(str)
    def _on_complete(self, _full: str) -> None:
        self._chat.on_complete(_full)
        self._set_state(AssistantState.IDLE)
        self._input_bar.set_busy(False)
        self._input_bar.focus_input()

    @pyqtSlot(str)
    def _on_error(self, message: str) -> None:
        self._chat.on_complete("")
        self._chat.add_error_message(message)
        self._set_state(AssistantState.IDLE)
        self._input_bar.set_busy(False)
        self._input_bar.focus_input()

    @pyqtSlot()
    def _on_stats(self) -> None:
        class _StatsWorker(QThread):
            def __init__(self) -> None:
                super().__init__()
                self.result = ""

            def run(self) -> None:
                stats = tools.get_system_stats()
                self.result = tools.format_stats(stats)

        worker = _StatsWorker()
        worker.finished.connect(
            lambda: self._chat.add_system_message(worker.result)
        )
        worker.start()
        scan_msg = (
            "📡  Scanning system metrics…"
            if self._config.mode == "normal"
            else "📡  Scanning the ether for hardware vitals…"
        )
        self._chat.add_system_message(scan_msg)

    @pyqtSlot()
    def _on_clear(self) -> None:
        self._engine.clear_history()
        self._chat.clear()
        clear_msg = (
            "🧹  Conversation cleared."
            if self._config.mode == "normal"
            else "🌀  History erased. The slate is void."
        )
        self._chat.add_system_message(clear_msg)

    @pyqtSlot()
    def _on_settings(self) -> None:
        dlg = SettingsDialog(self._config, self)
        dlg.setStyleSheet(self.styleSheet())
        dlg.adjustSize()

        gx = self.x() + max(0, (self.width() - dlg.width()) // 2)
        gy = self.y() + max(0, (self.height() - dlg.height()) // 2)
        dlg.move(gx, gy)

        dlg.config_saved.connect(self._apply_config)
        dlg.raise_()
        dlg.activateWindow()
        dlg.exec()

    @pyqtSlot(object)
    def _apply_config(self, new_config: Config) -> None:
        self._config = new_config
        self._engine = LLMEngine(new_config)
        self._apply_theme(new_config.mode, notify=False)

        active_model = new_config.ollama_model if new_config.backend == "ollama" else new_config.gemini_model
        self._avatar_row.set_engine_info(new_config.backend, active_model)
        self._title_bar.update_buttons(new_config.mode, new_config.backend)
        self._input_bar.set_privacy_states(new_config.screen_context_enabled, new_config.system_tools_enabled)

        self._chat.add_system_message(
            "✔  Settings saved. New configuration active."
        )

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _set_state(self, state: AssistantState) -> None:
        self._avatar_row.set_state(state)

    def closeEvent(self, event) -> None:
        pos = self.pos()
        self._config.window_x = pos.x()
        self._config.window_y = pos.y()
        self._config.window_width = self.width()
        self._config.window_height = self.height()
        self._config.save()
        self._engine.cancel_current()
        super().closeEvent(event)
