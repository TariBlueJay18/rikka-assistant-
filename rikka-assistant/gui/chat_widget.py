"""
Scrollable chat area with message bubbles and streaming support.

Message lifecycle:
  add_user_message()   → user bubble
  start_thinking()     → animated typing indicator
  on_token()           → indicator replaced by streaming assistant bubble
  on_complete()        → streaming bubble finalised
  add_error_message()  → error-styled system bubble
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from PyQt6.QtCore import QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


# ------------------------------------------------------------------ #
#  Message bubble                                                      #
# ------------------------------------------------------------------ #

class MessageBubble(QWidget):
    """
    A single chat bubble. Supports roles: "user" | "bot" | "system" | "error".
    Text can be updated after creation for streaming use.
    """

    MAX_WIDTH = 298  # px — keeps bubbles readable in a 420 px window

    def __init__(
        self,
        role: str,
        text: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._role = role
        self._text = text

        outer = QHBoxLayout(self)
        outer.setContentsMargins(10, 3, 10, 3)
        outer.setSpacing(0)

        frame = QFrame()
        frame.setObjectName(self._frame_name())

        inner = QVBoxLayout(frame)
        inner.setContentsMargins(12, 8, 12, 6)
        inner.setSpacing(2)

        self._label = QLabel(text)
        self._label.setObjectName(self._label_name())
        self._label.setWordWrap(True)
        self._label.setMaximumWidth(self.MAX_WIDTH)
        self._label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        inner.addWidget(self._label)

        ts = QLabel(datetime.now().strftime("%H:%M"))
        ts.setObjectName("BubbleTimestamp")
        ts.setAlignment(
            Qt.AlignmentFlag.AlignRight
            if role == "user"
            else Qt.AlignmentFlag.AlignLeft
        )
        inner.addWidget(ts)

        spacer = QWidget()
        spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        if role == "user":
            outer.addWidget(spacer)
            outer.addWidget(frame)
        elif role in ("system", "error"):
            outer.addWidget(frame)  # full width, no spacer
        else:  # bot
            outer.addWidget(frame)
            outer.addWidget(spacer)

    # ------------------------------------------------------------------ #

    def _frame_name(self) -> str:
        mapping = {
            "user":   "BubbleUser",
            "bot":    "BubbleBot",
            "system": "BubbleSystem",
            "error":  "BubbleError",
        }
        return mapping.get(self._role, "BubbleBot")

    def _label_name(self) -> str:
        mapping = {
            "user":   "BubbleTextUser",
            "bot":    "BubbleTextBot",
            "system": "BubbleTextSystem",
            "error":  "BubbleTextError",
        }
        return mapping.get(self._role, "BubbleTextBot")

    # ------------------------------------------------------------------ #

    def set_text(self, text: str) -> None:
        self._text = text
        self._label.setText(text)

    def append_text(self, chunk: str) -> None:
        self._text += chunk
        self._label.setText(self._text)

    def text(self) -> str:
        return self._text


# ------------------------------------------------------------------ #
#  Typing indicator                                                     #
# ------------------------------------------------------------------ #

class _TypingBubble(QWidget):
    """Animated three-dot indicator while waiting for the first token."""

    _FRAMES = ["●  ○  ○", "○  ●  ○", "○  ○  ●", "○  ●  ○"]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 3, 10, 3)

        frame = QFrame()
        frame.setObjectName("BubbleBot")

        inner = QVBoxLayout(frame)
        inner.setContentsMargins(14, 10, 14, 10)

        self._dot_label = QLabel(self._FRAMES[0])
        self._dot_label.setObjectName("TypingDots")
        self._dot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner.addWidget(self._dot_label)

        layout.addWidget(frame)

        spacer = QWidget()
        spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(spacer)

        self._idx = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(380)

    def _tick(self) -> None:
        self._idx = (self._idx + 1) % len(self._FRAMES)
        self._dot_label.setText(self._FRAMES[self._idx])

    def stop(self) -> None:
        self._timer.stop()


# ------------------------------------------------------------------ #
#  Chat widget                                                         #
# ------------------------------------------------------------------ #

class ChatWidget(QScrollArea):
    """
    Vertically scrolling container for MessageBubble widgets.
    Handles typing indicator lifecycle and auto-scroll behaviour.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("ChatArea")
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self._container = QWidget()
        self._container.setObjectName("ChatContainer")
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(0, 8, 0, 8)
        self._layout.setSpacing(2)
        self._layout.addStretch()  # pushes messages to the bottom initially

        self.setWidget(self._container)

        self._typing_bubble: Optional[_TypingBubble] = None
        self._streaming_bubble: Optional[MessageBubble] = None

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def add_user_message(self, text: str) -> None:
        self._insert_bubble(MessageBubble("user", text))

    def start_thinking(self) -> None:
        """Replace any existing indicator with a fresh typing animation."""
        self._remove_typing_bubble()
        tb = _TypingBubble()
        self._typing_bubble = tb
        self._layout.addWidget(tb)
        self._scroll_to_bottom()

    def on_token(self, token: str) -> None:
        """
        Called for each streamed token.
        On the first token the typing indicator is replaced by a real bubble.
        """
        if self._streaming_bubble is None:
            self._remove_typing_bubble()
            bubble = MessageBubble("bot", "")
            self._streaming_bubble = bubble
            self._layout.addWidget(bubble)

        self._streaming_bubble.append_text(token)

        if self._is_near_bottom():
            QTimer.singleShot(10, self._scroll_to_bottom)

    def on_complete(self, _full_text: str) -> None:
        """Finalise the streaming bubble."""
        self._streaming_bubble = None
        self._remove_typing_bubble()

    def add_system_message(self, text: str) -> None:
        """A neutral informational message (e.g. system stats)."""
        self._insert_bubble(MessageBubble("system", text))

    def add_error_message(self, text: str) -> None:
        self._insert_bubble(MessageBubble("error", f"⚠  {text}"))

    def clear(self) -> None:
        """Remove all message widgets."""
        self._remove_typing_bubble()
        self._streaming_bubble = None
        while self._layout.count() > 1:  # keep the bottom stretch
            item = self._layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    # ------------------------------------------------------------------ #
    #  Internals                                                           #
    # ------------------------------------------------------------------ #

    def _insert_bubble(self, bubble: MessageBubble) -> None:
        # Insert before the trailing stretch (always last)
        self._layout.insertWidget(self._layout.count() - 1, bubble)
        QTimer.singleShot(10, self._scroll_to_bottom)

    def _remove_typing_bubble(self) -> None:
        if self._typing_bubble is not None:
            self._typing_bubble.stop()
            self._layout.removeWidget(self._typing_bubble)
            self._typing_bubble.deleteLater()
            self._typing_bubble = None

    def _is_near_bottom(self) -> bool:
        sb = self.verticalScrollBar()
        return sb.value() >= sb.maximum() - 60

    def _scroll_to_bottom(self) -> None:
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()
        )
