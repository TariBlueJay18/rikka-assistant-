"""
Vector icon generator for Rikka Assistant.
Renders clean, resolution-independent QIcon objects using QPainter.
Avoids system emoji font issues and guarantees crisp, modern aesthetics.
"""
from __future__ import annotations

import math
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)


def make_stats_pixmap(size: int = 24, color: str = "#AE86FF") -> QPixmap:
    """Three rounded equalizer bars."""
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(color))

    p.drawRoundedRect(QRectF(size * 0.14, size * 0.42, size * 0.18, size * 0.46), 2, 2)
    p.drawRoundedRect(QRectF(size * 0.41, size * 0.16, size * 0.18, size * 0.72), 2, 2)
    p.drawRoundedRect(QRectF(size * 0.68, size * 0.32, size * 0.18, size * 0.56), 2, 2)

    p.end()
    return px


def make_clear_pixmap(size: int = 24, color: str = "#AE86FF") -> QPixmap:
    """Minimalist modern trash can icon."""
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    p.drawLine(QPointF(size * 0.38, size * 0.20), QPointF(size * 0.62, size * 0.20))
    p.drawLine(QPointF(size * 0.20, size * 0.28), QPointF(size * 0.80, size * 0.28))

    body = QPainterPath()
    body.moveTo(size * 0.26, size * 0.32)
    body.lineTo(size * 0.30, size * 0.82)
    body.lineTo(size * 0.70, size * 0.82)
    body.lineTo(size * 0.74, size * 0.32)
    p.drawPath(body)

    p.drawLine(QPointF(size * 0.42, size * 0.42), QPointF(size * 0.42, size * 0.72))
    p.drawLine(QPointF(size * 0.58, size * 0.42), QPointF(size * 0.58, size * 0.72))

    p.end()
    return px


def make_settings_pixmap(size: int = 24, color: str = "#AE86FF") -> QPixmap:
    """Clean modern 6-tooth gear icon."""
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    cx, cy = size * 0.5, size * 0.5
    r_in = size * 0.22
    r_out = size * 0.38

    p.drawEllipse(QPointF(cx, cy), r_in, r_in)

    for i in range(6):
        angle = i * (math.pi / 3.0)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        p1 = QPointF(cx + (r_in + 1) * cos_a, cy + (r_in + 1) * sin_a)
        p2 = QPointF(cx + r_out * cos_a, cy + r_out * sin_a)
        p.drawLine(p1, p2)

    p.end()
    return px


def make_send_pixmap(size: int = 24, color: str = "#FFFFFF") -> QPixmap:
    """Crisp upward arrow."""
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    cx = size * 0.5
    p.drawLine(QPointF(cx, size * 0.74), QPointF(cx, size * 0.26))
    arrow = QPainterPath()
    arrow.moveTo(size * 0.28, size * 0.44)
    arrow.lineTo(cx, size * 0.24)
    arrow.lineTo(size * 0.72, size * 0.44)
    p.drawPath(arrow)

    p.end()
    return px


def make_local_pixmap(size: int = 16, color: str = "#4ADE80") -> QPixmap:
    """Lightning bolt icon for Local Ollama."""
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(color))

    bolt = QPainterPath()
    bolt.moveTo(size * 0.55, size * 0.08)
    bolt.lineTo(size * 0.22, size * 0.52)
    bolt.lineTo(size * 0.48, size * 0.52)
    bolt.lineTo(size * 0.38, size * 0.92)
    bolt.lineTo(size * 0.78, size * 0.44)
    bolt.lineTo(size * 0.52, size * 0.44)
    bolt.closeSubpath()

    p.drawPath(bolt)
    p.end()
    return px


def make_cloud_pixmap(size: int = 16, color: str = "#38BDF8") -> QPixmap:
    """Cloud outline icon for Cloud Gemini."""
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    cloud = QPainterPath()
    cloud.moveTo(size * 0.28, size * 0.70)
    cloud.lineTo(size * 0.76, size * 0.70)
    cloud.arcTo(QRectF(size * 0.64, size * 0.44, size * 0.26, size * 0.26), -90, 180)
    cloud.arcTo(QRectF(size * 0.34, size * 0.24, size * 0.36, size * 0.36), 0, 180)
    cloud.arcTo(QRectF(size * 0.16, size * 0.46, size * 0.24, size * 0.24), 90, 180)
    cloud.closeSubpath()

    p.drawPath(cloud)
    p.end()
    return px


def make_screen_pixmap(size: int = 16, color: str = "#4ADE80") -> QPixmap:
    """Monitor / screen icon for screen context toggle."""
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Screen box
    p.drawRoundedRect(QRectF(size * 0.15, size * 0.15, size * 0.70, size * 0.52), 2, 2)
    # Stand
    p.drawLine(QPointF(size * 0.50, size * 0.67), QPointF(size * 0.50, size * 0.85))
    p.drawLine(QPointF(size * 0.32, size * 0.85), QPointF(size * 0.68, size * 0.85))

    p.end()
    return px


def make_globe_pixmap(size: int = 16, color: str = "#38BDF8") -> QPixmap:
    """Globe / web icon for browser & system actions toggle."""
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    cx, cy = size * 0.5, size * 0.5
    r = size * 0.38
    p.drawEllipse(QPointF(cx, cy), r, r)
    # Horizontal line
    p.drawLine(QPointF(cx - r, cy), QPointF(cx + r, cy))
    # Vertical ellipse
    p.drawEllipse(QPointF(cx, cy), r * 0.45, r)

    p.end()
    return px


def get_vector_icon(name: str, color: str = "#AE86FF", size: int = 24) -> QIcon:
    """Return a QIcon for the requested icon name."""
    if name == "stats":
        return QIcon(make_stats_pixmap(size, color))
    elif name == "clear":
        return QIcon(make_clear_pixmap(size, color))
    elif name == "settings":
        return QIcon(make_settings_pixmap(size, color))
    elif name == "send":
        return QIcon(make_send_pixmap(size, color))
    elif name == "local":
        return QIcon(make_local_pixmap(size, color))
    elif name == "cloud":
        return QIcon(make_cloud_pixmap(size, color))
    elif name == "screen":
        return QIcon(make_screen_pixmap(size, color))
    elif name == "globe":
        return QIcon(make_globe_pixmap(size, color))
    return QIcon()
