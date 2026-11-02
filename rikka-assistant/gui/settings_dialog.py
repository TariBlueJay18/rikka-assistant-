"""
Settings dialog: backend selection, mode toggle, model names, API keys, system prompt.
Fixed Z-ordering with WindowStaysOnTopHint, draggable header bar, and smooth translucent card framing.
"""
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QKeyEvent, QMouseEvent
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config import Config, DEFAULT_NORMAL_PROMPT, DEFAULT_RIKKA_PROMPT


class SettingsDialog(QDialog):
    """
    Modal settings panel.
    Emits config_saved(Config) when the user clicks Save.
    """

    config_saved = pyqtSignal(object)

    def __init__(self, config: Config, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("SettingsDialog")
        self.setWindowTitle("⚙ Settings")
        self.setModal(True)
        self.setMinimumWidth(440)

        # Essential for staying above the floating assistant window
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._config = config
        self._drag_pos: Optional[QPoint] = None

        self._build_ui()
        self._load_values()

    # ------------------------------------------------------------------ #
    #  UI construction                                                     #
    # ------------------------------------------------------------------ #

    def _build_ui() -> None:
        pass  # overridden below

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(14, 14, 14, 14)

        # Inner card frame
        self._card = QFrame()
        self._card.setObjectName("SettingsCardFrame")
        outer_layout.addWidget(self._card)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 180))
        self._card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(20, 16, 20, 18)
        card_layout.setSpacing(12)

        # ── Header bar (draggable handle + close button) ────────────
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)

        title = QLabel("⚙  Settings")
        title.setObjectName("SectionLabel")
        title.setStyleSheet("font-size: 15px; font-weight: 700;")
        header_row.addWidget(title)
        header_row.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(26, 26)
        close_btn.setToolTip("Close (Esc)")
        close_btn.clicked.connect(self.reject)
        header_row.addWidget(close_btn)
        card_layout.addLayout(header_row)

        # ── Mode Selection ──────────────────────────────────────────
        card_layout.addWidget(self._section("APPEARANCE & PERSONALITY"))
        mode_row = QHBoxLayout()
        mode_lbl = QLabel("Mode:")
        mode_lbl.setStyleSheet("color: #EDE7F6; font-size: 12px;")
        self._combo_mode = QComboBox()
        self._combo_mode.setObjectName("SettingsCombo")
        self._combo_mode.addItem("✦  Rikka (Chunibyo Magic)", "rikka")
        self._combo_mode.addItem("🫧  AI Assistant Mode (Frosted Acrylic)", "normal")
        self._combo_mode.currentIndexChanged.connect(self._on_mode_combo_changed)
        mode_row.addWidget(mode_lbl)
        mode_row.addWidget(self._combo_mode, stretch=1)
        card_layout.addLayout(mode_row)

        # ── Backend ─────────────────────────────────────────────────
        card_layout.addWidget(self._section("BACKEND ENGINE"))
        backend_row = QHBoxLayout()
        backend_lbl = QLabel("Engine:")
        backend_lbl.setStyleSheet("color: #EDE7F6; font-size: 12px;")
        self._combo_backend = QComboBox()
        self._combo_backend.setObjectName("SettingsCombo")
        self._combo_backend.addItems(["ollama", "gemini"])
        self._combo_backend.currentTextChanged.connect(self._on_backend_changed)
        backend_row.addWidget(backend_lbl)
        backend_row.addWidget(self._combo_backend, stretch=1)
        card_layout.addLayout(backend_row)

        # ── Ollama fields ───────────────────────────────────────────
        self._lbl_ollama = self._section("OLLAMA CONFIG")
        card_layout.addWidget(self._lbl_ollama)

        self._ollama_widget = QWidget()
        ollama_layout = QVBoxLayout(self._ollama_widget)
        ollama_layout.setContentsMargins(0, 0, 0, 0)
        ollama_layout.setSpacing(6)

        self._field_ollama_url = self._field("http://localhost:11434")
        self._field_ollama_model = self._field("llama3.2")
        ollama_layout.addLayout(self._form_row("Base URL:", self._field_ollama_url))
        ollama_layout.addLayout(self._form_row("Model:", self._field_ollama_model))
        card_layout.addWidget(self._ollama_widget)

        # ── Gemini fields ───────────────────────────────────────────
        self._lbl_gemini = self._section("GEMINI CONFIG")
        card_layout.addWidget(self._lbl_gemini)

        self._gemini_widget = QWidget()
        gemini_layout = QVBoxLayout(self._gemini_widget)
        gemini_layout.setContentsMargins(0, 0, 0, 0)
        gemini_layout.setSpacing(6)

        self._field_gemini_key = self._field("AIza…", password=True)
        self._field_gemini_model = self._field("gemini-2.0-flash")
        gemini_layout.addLayout(self._form_row("API Key:", self._field_gemini_key))
        gemini_layout.addLayout(self._form_row("Model:", self._field_gemini_model))
        card_layout.addWidget(self._gemini_widget)

        # ── Persona / Prompt ────────────────────────────────────────
        prompt_header = QHBoxLayout()
        prompt_header.addWidget(self._section("ACTIVE SYSTEM PROMPT"))
        prompt_header.addStretch()
        reset_prompt_btn = QPushButton("Reset to Default")
        reset_prompt_btn.setStyleSheet(
            "background: transparent; color: #8C7FB0; font-size: 11px; border: none; text-decoration: underline;"
        )
        reset_prompt_btn.clicked.connect(self._reset_prompt_to_default)
        prompt_header.addWidget(reset_prompt_btn)
        card_layout.addLayout(prompt_header)

        self._prompt_edit = QTextEdit()
        self._prompt_edit.setObjectName("PromptEdit")
        self._prompt_edit.setMinimumHeight(80)
        self._prompt_edit.setMaximumHeight(120)
        card_layout.addWidget(self._prompt_edit)

        # ── Misc (History turns) ────────────────────────────────────
        misc_row = QHBoxLayout()
        turns_lbl = QLabel("Max history turns:")
        turns_lbl.setStyleSheet("color: #EDE7F6; font-size: 12px;")
        self._field_turns = self._field("20")
        self._field_turns.setMaximumWidth(70)
        misc_row.addWidget(turns_lbl)
        misc_row.addWidget(self._field_turns)
        misc_row.addStretch()
        card_layout.addLayout(misc_row)

        # ── Action Buttons ──────────────────────────────────────────
        card_layout.addSpacerItem(QSpacerItem(0, 6, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Save Changes")
        save_btn.setObjectName("PrimaryBtn")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        card_layout.addLayout(btn_row)

    # ------------------------------------------------------------------ #
    #  Window dragging                                                     #
    # ------------------------------------------------------------------ #

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            return
        super().keyPressEvent(event)

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _section(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("SectionLabel")
        return lbl

    @staticmethod
    def _field(placeholder: str = "", password: bool = False) -> QLineEdit:
        f = QLineEdit()
        f.setObjectName("SettingsField")
        if placeholder:
            f.setPlaceholderText(placeholder)
        if password:
            f.setEchoMode(QLineEdit.EchoMode.Password)
        return f

    @staticmethod
    def _form_row(label_text: str, field_widget: QWidget) -> QHBoxLayout:
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #EDE7F6; font-size: 12px;")
        lbl.setMinimumWidth(80)
        row.addWidget(lbl)
        row.addWidget(field_widget, stretch=1)
        return row

    def _on_backend_changed(self, value: str) -> None:
        is_ollama = value == "ollama"
        self._lbl_ollama.setVisible(is_ollama)
        self._ollama_widget.setVisible(is_ollama)
        self._lbl_gemini.setVisible(not is_ollama)
        self._gemini_widget.setVisible(not is_ollama)
        self.adjustSize()

    def _on_mode_combo_changed(self, _idx: int) -> None:
        mode = self._combo_mode.currentData()
        if mode == "normal":
            self._prompt_edit.setPlainText(self._config.system_prompt_normal)
        else:
            self._prompt_edit.setPlainText(self._config.system_prompt_rikka)

    def _reset_prompt_to_default(self) -> None:
        mode = self._combo_mode.currentData()
        if mode == "normal":
            self._prompt_edit.setPlainText(DEFAULT_NORMAL_PROMPT)
        else:
            self._prompt_edit.setPlainText(DEFAULT_RIKKA_PROMPT)

    # ------------------------------------------------------------------ #
    #  Load / Save                                                         #
    # ------------------------------------------------------------------ #

    def _load_values(self) -> None:
        c = self._config
        mode_idx = 0 if c.mode == "rikka" else 1
        self._combo_mode.setCurrentIndex(mode_idx)

        self._combo_backend.setCurrentText(c.backend)
        self._field_ollama_url.setText(c.ollama_base_url)
        self._field_ollama_model.setText(c.ollama_model)
        self._field_gemini_key.setText(c.gemini_api_key)
        self._field_gemini_model.setText(c.gemini_model)
        self._prompt_edit.setPlainText(c.system_prompt)
        self._field_turns.setText(str(c.max_history_turns))
        self._on_backend_changed(c.backend)

    def _save(self) -> None:
        c = self._config
        c.mode = self._combo_mode.currentData()
        c.backend = self._combo_backend.currentText()
        c.ollama_base_url = self._field_ollama_url.text().strip()
        c.ollama_model = self._field_ollama_model.text().strip()
        c.gemini_api_key = self._field_gemini_key.text().strip()
        c.gemini_model = self._field_gemini_model.text().strip()

        edited_prompt = self._prompt_edit.toPlainText().strip()
        if c.mode == "normal":
            c.system_prompt_normal = edited_prompt
        else:
            c.system_prompt_rikka = edited_prompt

        try:
            c.max_history_turns = int(self._field_turns.text())
        except ValueError:
            pass

        c.save()
        self.config_saved.emit(c)
        self.accept()
