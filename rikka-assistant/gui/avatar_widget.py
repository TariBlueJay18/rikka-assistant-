"""
Avatar widget that reflects the current AssistantState and Mode.
Features:
  1. Rikka Mode: Authentic circular portrait of Rikka Takanashi (from user reference),
     with live animated rotating Arcane Magic Circle / Tyrant's Eye rune aura during generation.
  2. AI Assistant Mode: Frosted Iridescent Orb with Siri-inspired rotating aura ring during generation.
Uses hardware-accelerated QPainter animations driven by an internal 35 FPS timer.
"""
from __future__ import annotations

import enum
import math
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QPointF, QRectF, QSize, Qt, QTimer
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QFont,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import QWidget

ASSETS_DIR = Path(__file__).parent.parent / "assets"
RIKKA_PORTRAIT_PATH = ASSETS_DIR / "rikka_portrait.png"


class AssistantState(enum.Enum):
    IDLE = "idle"
    THINKING = "thinking"
    SPEAKING = "speaking"


_STATUS_TEXTS: dict[str, dict[AssistantState, str]] = {
    "rikka": {
        AssistantState.IDLE:     "○  Idle",
        AssistantState.THINKING: "⟳  Unsealing spell…",
        AssistantState.SPEAKING: "◉  Tyrant's Eye active",
    },
    "normal": {
        AssistantState.IDLE:     "○  Ready",
        AssistantState.THINKING: "⟳  Processing…",
        AssistantState.SPEAKING: "◉  Responding",
    },
}


class AvatarWidget(QWidget):
    """
    Animated circular avatar widget.
    Smoothly animates magical runes or Siri frosted aura while generating text.
    """

    def __init__(self, size: int = 96, mode: str = "rikka", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._size = size
        self._mode = mode
        self._state = AssistantState.IDLE

        self._rot_angle = 0.0
        self._pulse_phase = 0.0

        # Animation timer (35 FPS)
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(28)
        self._anim_timer.timeout.connect(self._on_anim_tick)

        # Load Rikka portrait image
        self._rikka_img: Optional[QImage] = None
        if RIKKA_PORTRAIT_PATH.exists():
            self._rikka_img = QImage(str(RIKKA_PORTRAIT_PATH))

        self.setFixedSize(size, size)

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def set_mode(self, mode: str) -> None:
        if mode != self._mode:
            self._mode = mode
            self.update()

    def set_state(self, state: AssistantState) -> None:
        if state != self._state:
            self._state = state
            if state in (AssistantState.THINKING, AssistantState.SPEAKING):
                if not self._anim_timer.isActive():
                    self._anim_timer.start()
            else:
                self._anim_timer.stop()
            self.update()

    def state(self) -> AssistantState:
        return self._state

    def status_text(self) -> str:
        texts = _STATUS_TEXTS.get(self._mode, _STATUS_TEXTS["rikka"])
        return texts.get(self._state, "○  Ready")

    def sizeHint(self) -> QSize:
        return QSize(self._size, self._size)

    # ------------------------------------------------------------------ #
    #  Animation Tick                                                      #
    # ------------------------------------------------------------------ #

    def _on_anim_tick(self) -> None:
        step = 5.0 if self._state == AssistantState.SPEAKING else 3.0
        self._rot_angle = (self._rot_angle + step) % 360.0
        self._pulse_phase = (self._pulse_phase + 0.12) % (2.0 * math.pi)
        self.update()

    # ------------------------------------------------------------------ #
    #  Paint Event                                                         #
    # ------------------------------------------------------------------ #

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w = float(self.width())
        h = float(self.height())
        cx = w * 0.5
        cy = h * 0.5
        radius = (min(w, h) * 0.5) - 4.0

        if self._mode == "normal":
            self._paint_frosted_orb(painter, cx, cy, radius)
        else:
            self._paint_rikka(painter, cx, cy, radius)

        painter.end()

    # ------------------------------------------------------------------ #
    #  Rikka Mode Painting                                                 #
    # ------------------------------------------------------------------ #

    def _paint_rikka(self, p: QPainter, cx: float, cy: float, r: float) -> None:
        is_generating = self._state in (AssistantState.THINKING, AssistantState.SPEAKING)
        pulse = 0.5 + 0.5 * math.sin(self._pulse_phase)

        # 1. Outer magical aura glow if generating
        if is_generating:
            aura_rad = r + 3.0 + 3.0 * pulse
            aura = QRadialGradient(cx, cy, aura_rad)
            if self._state == AssistantState.SPEAKING:
                aura.setColorAt(0.7, QColor(208, 80, 232, int(90 * pulse)))
                aura.setColorAt(1.0, QColor(255, 121, 198, 0))
            else:
                aura.setColorAt(0.7, QColor(124, 77, 255, int(90 * pulse)))
                aura.setColorAt(1.0, QColor(174, 134, 255, 0))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(aura))
            p.drawEllipse(QPointF(cx, cy), aura_rad, aura_rad)

        # 2. Base circular portrait
        inner_r = r - (4.0 if is_generating else 2.0)
        circle_rect = QRectF(cx - inner_r, cy - inner_r, inner_r * 2, inner_r * 2)

        p.save()
        clip = QPainterPath()
        clip.addEllipse(circle_rect)
        p.setClipPath(clip)

        if self._rikka_img is not None and not self._rikka_img.isNull():
            p.drawImage(circle_rect, self._rikka_img)
        else:
            bg = QLinearGradient(cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r)
            bg.setColorAt(0.0, QColor("#3a1b6c"))
            bg.setColorAt(1.0, QColor("#15112e"))
            p.fillRect(circle_rect, QBrush(bg))
            font = QFont("Segoe UI", int(inner_r * 0.7), QFont.Weight.Bold)
            p.setFont(font)
            p.setPen(QColor(255, 255, 255, 220))
            p.drawText(circle_rect, Qt.AlignmentFlag.AlignCenter, "✦")

        # Subtle golden Tyrant Eye eye-flare when speaking
        if is_generating:
            flare_x = cx - inner_r * 0.15
            flare_y = cy - inner_r * 0.18
            flare = QRadialGradient(flare_x, flare_y, inner_r * 0.28)
            flare.setColorAt(0.0, QColor(255, 220, 50, int(180 * pulse)))
            flare.setColorAt(0.5, QColor(255, 140, 0, int(90 * pulse)))
            flare.setColorAt(1.0, QColor(255, 140, 0, 0))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(flare))
            p.drawEllipse(QPointF(flare_x, flare_y), inner_r * 0.28, inner_r * 0.28)

        p.restore()

        # 3. Rotating Arcane Rune Ring (when generating)
        if is_generating:
            p.save()
            p.translate(cx, cy)
            p.rotate(self._rot_angle)

            rune_color = QColor(208, 80, 232) if self._state == AssistantState.SPEAKING else QColor(174, 134, 255)
            pen = QPen(rune_color, 1.8)
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setDashPattern([3, 5])
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(0, 0), r, r)

            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(255, 255, 255, 210))
            for i in range(6):
                ang = i * (math.pi / 3.0)
                nx = r * math.cos(ang)
                ny = r * math.sin(ang)
                p.drawEllipse(QPointF(nx, ny), 2.2, 2.2)

            p.restore()
        else:
            p.setPen(QPen(QColor(174, 134, 255, 160), 2.0))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(cx, cy), r, r)

    # ------------------------------------------------------------------ #
    #  AI Assistant Mode: Frosted Iridescent Orb Painting                  #
    # ------------------------------------------------------------------ #

    def _paint_frosted_orb(self, p: QPainter, cx: float, cy: float, r: float) -> None:
        is_generating = self._state in (AssistantState.THINKING, AssistantState.SPEAKING)
        pulse = 0.5 + 0.5 * math.sin(self._pulse_phase)

        # 1. Siri Animated Iridescent Perimeter Ring
        if is_generating:
            p.save()
            p.translate(cx, cy)
            p.rotate(self._rot_angle)

            conical = QConicalGradient(0, 0, 0)
            conical.setColorAt(0.00, QColor("#FF375F"))
            conical.setColorAt(0.25, QColor("#BF5AF2"))
            conical.setColorAt(0.50, QColor("#0A84FF"))
            conical.setColorAt(0.75, QColor("#30D158"))
            conical.setColorAt(1.00, QColor("#FF375F"))

            ring_pen = QPen(QBrush(conical), 2.8 + 1.2 * pulse)
            p.setPen(ring_pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(0, 0), r, r)
            p.restore()
        else:
            p.setPen(QPen(QColor(255, 255, 255, 65), 1.5))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(cx, cy), r, r)

        # 2. Frosted Matte Core (soft velvety diffusion)
        inner_r = r - (3.5 if is_generating else 2.0)
        rad = QRadialGradient(cx - inner_r * 0.20, cy - inner_r * 0.20, inner_r * 1.1)
        if self._state == AssistantState.SPEAKING:
            rad.setColorAt(0.0, QColor("#FF7A95"))
            rad.setColorAt(0.40, QColor("#A855F7"))
            rad.setColorAt(0.80, QColor("#0284C7"))
            rad.setColorAt(1.0, QColor("#0F172A"))
        elif self._state == AssistantState.THINKING:
            rad.setColorAt(0.0, QColor("#FBBF24"))
            rad.setColorAt(0.40, QColor("#F43F5E"))
            rad.setColorAt(0.80, QColor("#9333EA"))
            rad.setColorAt(1.0, QColor("#1E1B4B"))
        else:
            rad.setColorAt(0.0, QColor("#38BDF8"))
            rad.setColorAt(0.35, QColor("#0284C7"))
            rad.setColorAt(0.75, QColor("#4F46E5"))
            rad.setColorAt(1.0, QColor("#0F172A"))

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(rad))
        p.drawEllipse(QPointF(cx, cy), inner_r, inner_r)

        # 3. Soft Satin Matte Diffusion Layer (Frosted effect instead of glossy)
        satin_w = inner_r * 1.4
        satin_h = inner_r * 0.85
        satin_rect = QRectF(cx - satin_w * 0.5, cy - inner_r * 0.90, satin_w, satin_h)

        p.save()
        clip_satin = QPainterPath()
        clip_satin.addEllipse(QPointF(cx, cy), inner_r, inner_r)
        p.setClipPath(clip_satin)

        satin_grad = QLinearGradient(cx, satin_rect.top(), cx, satin_rect.bottom())
        satin_grad.setColorAt(0.0, QColor(255, 255, 255, 120))
        satin_grad.setColorAt(0.5, QColor(255, 255, 255, 30))
        satin_grad.setColorAt(1.0, QColor(255, 255, 255, 0))

        p.setBrush(QBrush(satin_grad))
        p.drawEllipse(satin_rect)
        p.restore()

        # 4. Central Glyph
        symbol = "✦"
        if self._state == AssistantState.THINKING:
            symbol = "◌"
        elif self._state == AssistantState.SPEAKING:
            symbol = "≋"

        font = QFont("Segoe UI", int(inner_r * 0.42), QFont.Weight.Bold)
        p.setFont(font)
        p.setPen(QColor(255, 255, 255, 235))
        center_rect = QRectF(cx - inner_r, cy - inner_r, inner_r * 2, inner_r * 2)
        p.drawText(center_rect, Qt.AlignmentFlag.AlignCenter, symbol)
