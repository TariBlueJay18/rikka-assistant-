"""
Google Pixel-inspired fluid wave transition animation.
Creates an expanding fluid wave ripple originating from the mode toggle button,
revealing the destination theme with liquid surface-tension crests.
"""
from __future__ import annotations

import math
from typing import Optional

from PyQt6.QtCore import (
    QEasingCurve,
    QPoint,
    QPointF,
    QRectF,
    Qt,
    QVariantAnimation,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PyQt6.QtWidgets import QWidget


class WaveTransitionOverlay(QWidget):
    """
    Full-window translucent overlay that renders a fluid expanding wave ripple
    transition between Rikka Mode and AI Assistant Mode.
    """

    def __init__(
        self,
        parent: QWidget,
        old_pixmap: QPixmap,
        origin: QPoint,
        to_mode: str,
    ) -> None:
        super().__init__(parent)
        self._old_pixmap = old_pixmap
        self._origin = QPointF(float(origin.x()), float(origin.y()))
        self._to_mode = to_mode
        self._progress = 0.0

        self.setGeometry(parent.rect())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Max radius to cover furthest corner
        w = float(self.width())
        h = float(self.height())
        dx = max(self._origin.x(), w - self._origin.x())
        dy = max(self._origin.y(), h - self._origin.y())
        self._max_radius = math.hypot(dx, dy) * 1.15

        # Fluid wave animation (Google Pixel style OutCubic easing)
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(560)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._on_anim_frame)
        self._anim.finished.connect(self.deleteLater)

        self.show()
        self.raise_()
        self._anim.start()

    def _on_anim_frame(self, val: float) -> None:
        self._progress = float(val)
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w = float(self.width())
        h = float(self.height())
        r = self._progress * self._max_radius

        # 1. Draw old state outside the expanding wave circle
        full_path = QPainterPath()
        full_path.addRect(QRectF(0.0, 0.0, w, h))

        circle_path = QPainterPath()
        circle_path.addEllipse(self._origin, r, r)

        cutout = full_path.subtracted(circle_path)
        painter.save()
        painter.setClipPath(cutout)
        painter.drawPixmap(0, 0, self._old_pixmap)
        painter.restore()

        # Fade ripple at end of transition
        alpha_fade = 1.0
        if self._progress > 0.75:
            alpha_fade = max(0.0, 1.0 - (self._progress - 0.75) / 0.25)

        if alpha_fade > 0.01 and r > 4.0:
            # 2. Fluid Wavefront Ripple Styling
            is_rikka = (self._to_mode == "rikka")
            primary_color = QColor(208, 80, 232) if is_rikka else QColor(56, 189, 248)
            secondary_color = QColor(124, 77, 255) if is_rikka else QColor(255, 255, 255)

            # Outer diffuse liquid halo
            halo_pen = QPen(
                QColor(primary_color.red(), primary_color.green(), primary_color.blue(), int(140 * alpha_fade)),
                7.0,
            )
            painter.setPen(halo_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(self._origin, r, r)

            # Sharp wave crest
            crest_pen = QPen(
                QColor(255, 255, 255, int(220 * alpha_fade)),
                2.0,
            )
            painter.setPen(crest_pen)
            painter.drawEllipse(self._origin, r, r)

            # Secondary trailing echo ripple (fluid surface tension wave)
            if r > 20.0:
                trail_r = r - 16.0
                echo_pen = QPen(
                    QColor(secondary_color.red(), secondary_color.green(), secondary_color.blue(), int(110 * alpha_fade)),
                    2.0,
                )
                painter.setPen(echo_pen)
                painter.drawEllipse(self._origin, trail_r, trail_r)

        painter.end()
