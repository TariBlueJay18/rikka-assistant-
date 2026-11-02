"""
Visual design tokens and Qt stylesheets for Rikka Assistant.
Supports two distinct aesthetics:
  1. Rikka Mode: Chunibyo dark violet, neon runes, magical magenta highlights.
  2. AI Assistant Mode: Frosted Matte Acrylic, diffuse satin luminescence, frosted glass bubbles.
Engineered with unified outer card backgrounds to eliminate all corner clipping and seam glitches.
"""
from __future__ import annotations

# ------------------------------------------------------------------ #
#  Rikka Theme Palette & QSS                                          #
# ------------------------------------------------------------------ #

RIKKA_PALETTE: dict[str, str] = {
    "bg_deep":        "#070514",
    "bg_main":        "#0d0b20",
    "bg_surface":     "rgba(21, 17, 46, 0.60)",
    "bg_hover":       "rgba(124, 77, 255, 0.18)",
    "bg_input":       "rgba(16, 14, 38, 0.85)",
    "accent":         "#7c4dff",
    "accent_light":   "#ae86ff",
    "accent_dark":    "#5532cc",
    "magenta":        "#d050e8",
    "magenta_light":  "#e879f9",
    "text":           "#ede7f6",
    "text_muted":     "#9d8fc2",
    "text_dim":       "#5d5282",
    "bubble_user_0":  "#3a1b6c",
    "bubble_user_1":  "#6b35cc",
    "bubble_bot_0":   "rgba(18, 16, 42, 0.88)",
    "bubble_bot_1":   "rgba(30, 26, 68, 0.88)",
    "border":         "rgba(124, 77, 255, 0.38)",
    "border_focus":   "#ae86ff",
    "error":          "#ff5252",
    "success":        "#4ade80",
    "warning":        "#ffab40",
    "title_bar":      "transparent",
    "scrollbar_fg":   "rgba(124, 77, 255, 0.45)",
}

RP = RIKKA_PALETTE

RIKKA_QSS: str = f"""
/* ── Transparent root ── */
QWidget#AssistantWindow {{
    background: transparent;
}}

/* ── Outer Card Frame (Unified rounded container) ── */
QFrame#MainFrame {{
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #141032,
        stop:0.06 #0e0c24,
        stop:0.92 #09071a,
        stop:1 #060412
    );
    border-radius: 22px;
    border: 1px solid {RP['border']};
}}

/* ── Title bar (Transparent, zero corner leak) ── */
QWidget#TitleBar {{
    background: transparent;
    border: none;
    border-bottom: 1px solid rgba(124, 77, 255, 0.22);
    min-height: 40px;
    max-height: 40px;
}}
QLabel#TitleLabel {{
    color: {RP['accent_light']};
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.8px;
    background: transparent;
}}

/* ── Backend Toggle Button (Local / Cloud) ── */
QPushButton#BackendToggleBtn {{
    background: rgba(74, 222, 128, 0.14);
    border: 1px solid rgba(74, 222, 128, 0.35);
    border-radius: 11px;
    color: #4ade80;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 9px;
    min-height: 22px;
}}
QPushButton#BackendToggleBtn:hover {{
    background: rgba(74, 222, 128, 0.25);
    border-color: #4ade80;
    color: #FFFFFF;
}}
QPushButton#BackendToggleBtn[cloud="true"] {{
    background: rgba(56, 189, 248, 0.14);
    border: 1px solid rgba(56, 189, 248, 0.35);
    color: #38bdf8;
}}
QPushButton#BackendToggleBtn[cloud="true"]:hover {{
    background: rgba(56, 189, 248, 0.25);
    border-color: #38bdf8;
    color: #FFFFFF;
}}

/* ── Mode Toggle Button (Rikka / AI Assistant) ── */
QPushButton#ModeToggleBtn {{
    background: rgba(124, 77, 255, 0.18);
    border: 1px solid rgba(174, 134, 255, 0.38);
    border-radius: 11px;
    color: {RP['magenta_light']};
    font-size: 11px;
    font-weight: 600;
    padding: 2px 9px;
    min-height: 22px;
}}
QPushButton#ModeToggleBtn:hover {{
    background: rgba(208, 80, 232, 0.28);
    border-color: {RP['magenta']};
    color: #FFFFFF;
}}

/* ── Privacy Toggle Pills (Screen Context & System Tools) ── */
QPushButton#PrivacyToggleBtn {{
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 10px;
    color: #9d8fc2;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    min-height: 20px;
}}
QPushButton#PrivacyToggleBtn:hover {{
    background: rgba(255, 255, 255, 0.10);
    color: #ede7f6;
}}
QPushButton#PrivacyToggleBtn[active="true"] {{
    background: rgba(124, 77, 255, 0.22);
    border: 1px solid #ae86ff;
    color: #ede7f6;
}}

/* ── Avatar Section ── */
QWidget#AvatarRow {{
    background: rgba(255, 255, 255, 0.02);
    border: none;
    border-bottom: 1px solid rgba(124, 77, 255, 0.18);
}}
QLabel#NameLabel {{
    color: {RP['text']};
    font-size: 13px;
    font-weight: 600;
    background: transparent;
}}
QLabel#StatusLabel {{
    color: {RP['text_muted']};
    font-size: 11px;
    background: transparent;
}}

/* ── Chat Scroll Area ── */
QScrollArea#ChatArea {{
    background: transparent;
    border: none;
}}
QWidget#ChatContainer {{
    background: transparent;
}}

/* ── Message Bubbles ── */
QFrame#BubbleUser {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {RP['bubble_user_0']}, stop:1 {RP['bubble_user_1']});
    border-radius: 15px 4px 15px 15px;
    border: 1px solid rgba(174, 134, 255, 0.30);
}}
QFrame#BubbleBot {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {RP['bubble_bot_0']}, stop:1 {RP['bubble_bot_1']});
    border-radius: 4px 15px 15px 15px;
    border: 1px solid {RP['border']};
}}
QFrame#BubbleSystem {{
    background: rgba(124, 77, 255, 0.12);
    border-radius: 10px;
    border: 1px solid rgba(174, 134, 255, 0.25);
}}
QFrame#BubbleError {{
    background: rgba(255, 82, 82, 0.12);
    border-radius: 10px;
    border: 1px solid rgba(255, 82, 82, 0.38);
}}

QLabel#BubbleTextUser {{
    color: {RP['text']};
    font-size: 13px;
    background: transparent;
    line-height: 1.45;
}}
QLabel#BubbleTextBot {{
    color: {RP['text']};
    font-size: 13px;
    background: transparent;
    line-height: 1.45;
}}
QLabel#BubbleTextSystem {{
    color: #d8b4fe;
    font-size: 12px;
    background: transparent;
}}
QLabel#BubbleTextError {{
    color: #ff8a80;
    font-size: 12px;
    background: transparent;
}}
QLabel#BubbleTimestamp {{
    color: {RP['text_dim']};
    font-size: 10px;
    background: transparent;
}}

/* ── Typing Indicator ── */
QLabel#TypingDots {{
    color: {RP['accent_light']};
    font-size: 20px;
    background: transparent;
    letter-spacing: 4px;
}}

/* ── Input Bar (Transparent, zero corner leak) ── */
QWidget#InputBar {{
    background: transparent;
    border: none;
    border-top: 1px solid rgba(124, 77, 255, 0.22);
}}
QPlainTextEdit#InputEdit {{
    background: {RP['bg_input']};
    color: {RP['text']};
    border: 1px solid {RP['border']};
    border-radius: 12px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: {RP['accent']};
}}
QPlainTextEdit#InputEdit:focus {{
    border: 1px solid {RP['border_focus']};
}}

/* ── Action Bar Buttons ── */
QPushButton#ActionBtn {{
    background: rgba(124, 77, 255, 0.10);
    border: 1px solid rgba(124, 77, 255, 0.18);
    border-radius: 8px;
    min-width: 30px;
    min-height: 30px;
}}
QPushButton#ActionBtn:hover {{
    background: {RP['bg_hover']};
    border: 1px solid {RP['border_focus']};
}}
QPushButton#ActionBtn:pressed {{
    background: {RP['accent_dark']};
}}

/* ── Send Button ── */
QPushButton#SendBtn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {RP['accent']}, stop:1 {RP['magenta']});
    border: 1px solid rgba(255, 255, 255, 0.20);
    border-radius: 10px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
}}
QPushButton#SendBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {RP['accent_light']}, stop:1 {RP['magenta_light']});
    border-color: rgba(255, 255, 255, 0.40);
}}
QPushButton#SendBtn:disabled {{
    background: rgba(124, 77, 255, 0.12);
    border: none;
}}

/* ── Window Control Buttons ── */
QPushButton#WinBtn {{
    background: transparent;
    border: none;
    color: {RP['text_muted']};
    font-size: 14px;
    border-radius: 6px;
    min-width: 28px;
    min-height: 28px;
}}
QPushButton#WinBtn:hover {{
    background: rgba(255, 255, 255, 0.08);
    color: {RP['text']};
}}
QPushButton#CloseBtn {{
    background: transparent;
    border: none;
    color: {RP['text_muted']};
    font-size: 14px;
    border-radius: 6px;
    min-width: 28px;
    min-height: 28px;
}}
QPushButton#CloseBtn:hover {{
    background: rgba(255, 82, 82, 0.28);
    color: {RP['error']};
}}

/* ── Settings Dialog ── */
QDialog#SettingsDialog {{
    background: transparent;
}}
QFrame#SettingsCardFrame {{
    background-color: #0e0c24;
    border: 1px solid {RP['border']};
    border-radius: 18px;
}}
QLabel#SectionLabel {{
    color: {RP['accent_light']};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    background: transparent;
}}
QLineEdit#SettingsField {{
    background: {RP['bg_input']};
    color: {RP['text']};
    border: 1px solid {RP['border']};
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
    selection-background-color: {RP['accent']};
}}
QLineEdit#SettingsField:focus {{
    border-color: {RP['accent']};
}}
QComboBox#SettingsCombo {{
    background: {RP['bg_input']};
    color: {RP['text']};
    border: 1px solid {RP['border']};
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
}}
QComboBox#SettingsCombo::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox#SettingsCombo QAbstractItemView {{
    background: #15112e;
    color: {RP['text']};
    border: 1px solid {RP['border']};
    selection-background-color: {RP['accent']};
}}
QTextEdit#PromptEdit {{
    background: {RP['bg_input']};
    color: {RP['text']};
    border: 1px solid {RP['border']};
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
    selection-background-color: {RP['accent']};
}}
QTextEdit#PromptEdit:focus {{
    border-color: {RP['accent']};
}}
QPushButton#PrimaryBtn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {RP['accent']}, stop:1 {RP['magenta']});
    color: white;
    border: none;
    border-radius: 8px;
    padding: 7px 20px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton#PrimaryBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {RP['accent_light']}, stop:1 {RP['magenta_light']});
}}
QPushButton#SecondaryBtn {{
    background: rgba(255, 255, 255, 0.06);
    color: {RP['text_muted']};
    border: 1px solid {RP['border']};
    border-radius: 8px;
    padding: 7px 20px;
    font-size: 13px;
}}
QPushButton#SecondaryBtn:hover {{
    color: {RP['text']};
    border-color: {RP['accent']};
}}

/* ── Global scrollbar ── */
QScrollBar:vertical {{
    background: transparent;
    width: 5px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {RP['scrollbar_fg']};
    border-radius: 2px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{ background: none; }}
"""


# ------------------------------------------------------------------ #
#  AI Assistant Theme (Frosted Matte Acrylic)                         #
# ------------------------------------------------------------------ #

FROSTED_QSS: str = """
/* ── Transparent root ── */
QWidget#AssistantWindow {
    background: transparent;
}

/* ── Frosted Matte Frame (Soft velvety acrylic diffusion) ── */
QFrame#MainFrame {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.14),
        stop:0.03 rgba(255, 255, 255, 0.06),
        stop:0.12 rgba(24, 28, 38, 0.88),
        stop:0.88 rgba(14, 16, 24, 0.92),
        stop:1 rgba(10, 12, 18, 0.96)
    );
    border-radius: 22px;
    border: 1px solid rgba(255, 255, 255, 0.18);
}

/* ── Title bar ── */
QWidget#TitleBar {
    background: transparent;
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    min-height: 40px;
    max-height: 40px;
}
QLabel#TitleLabel {
    color: #FFFFFF;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    background: transparent;
}

/* ── Backend Toggle Button (Local / Cloud) ── */
QPushButton#BackendToggleBtn {
    background: rgba(74, 222, 128, 0.12);
    border: 1px solid rgba(74, 222, 128, 0.30);
    border-radius: 11px;
    color: #4ade80;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 9px;
    min-height: 22px;
}
QPushButton#BackendToggleBtn:hover {
    background: rgba(74, 222, 128, 0.22);
    border-color: #4ade80;
    color: #FFFFFF;
}
QPushButton#BackendToggleBtn[cloud="true"] {
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.30);
    color: #38bdf8;
}
QPushButton#BackendToggleBtn[cloud="true"]:hover {
    background: rgba(56, 189, 248, 0.22);
    border-color: #38bdf8;
    color: #FFFFFF;
}

/* ── Mode Toggle Button (AI Assistant / Rikka) ── */
QPushButton#ModeToggleBtn {
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.20);
    border-radius: 11px;
    color: #38BDF8;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 9px;
    min-height: 22px;
}
QPushButton#ModeToggleBtn:hover {
    background: rgba(56, 189, 248, 0.25);
    border-color: #38BDF8;
    color: #FFFFFF;
}

/* ── Privacy Toggle Pills (Screen Context & System Tools) ── */
QPushButton#PrivacyToggleBtn {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 10px;
    color: #94A3B8;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    min-height: 20px;
}
QPushButton#PrivacyToggleBtn:hover {
    background: rgba(255, 255, 255, 0.12);
    color: #FFFFFF;
}
QPushButton#PrivacyToggleBtn[active="true"] {
    background: rgba(56, 189, 248, 0.20);
    border: 1px solid #38BDF8;
    color: #FFFFFF;
}

/* ── Avatar Section ── */
QWidget#AvatarRow {
    background: rgba(255, 255, 255, 0.02);
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}
QLabel#NameLabel {
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 600;
    background: transparent;
}
QLabel#StatusLabel {
    color: #94A3B8;
    font-size: 11px;
    background: transparent;
}

/* ── Chat Scroll Area ── */
QScrollArea#ChatArea {
    background: transparent;
    border: none;
}
QWidget#ChatContainer {
    background: transparent;
}

/* ── Message Bubbles (Frosted Acrylic Velvet) ── */
QFrame#BubbleUser {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #0071E3,
        stop:1 #0056B3
    );
    border-radius: 15px 4px 15px 15px;
    border: 1px solid rgba(255, 255, 255, 0.22);
}
QFrame#BubbleBot {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.10),
        stop:1 rgba(255, 255, 255, 0.04)
    );
    border-radius: 4px 15px 15px 15px;
    border: 1px solid rgba(255, 255, 255, 0.12);
}
QFrame#BubbleSystem {
    background: rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.12);
}
QFrame#BubbleError {
    background: rgba(255, 69, 58, 0.15);
    border-radius: 10px;
    border: 1px solid rgba(255, 69, 58, 0.32);
}

QLabel#BubbleTextUser {
    color: #FFFFFF;
    font-size: 13px;
    background: transparent;
    line-height: 1.45;
}
QLabel#BubbleTextBot {
    color: #F1F5F9;
    font-size: 13px;
    background: transparent;
    line-height: 1.45;
}
QLabel#BubbleTextSystem {
    color: #CBD5E1;
    font-size: 12px;
    background: transparent;
}
QLabel#BubbleTextError {
    color: #FF8A80;
    font-size: 12px;
    background: transparent;
}
QLabel#BubbleTimestamp {
    color: rgba(255, 255, 255, 0.35);
    font-size: 10px;
    background: transparent;
}

/* ── Typing Indicator ── */
QLabel#TypingDots {
    color: #38BDF8;
    font-size: 20px;
    background: transparent;
    letter-spacing: 4px;
}

/* ── Input Bar ── */
QWidget#InputBar {
    background: transparent;
    border: none;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}
QPlainTextEdit#InputEdit {
    background: rgba(255, 255, 255, 0.07);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 12px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: #0284C7;
}
QPlainTextEdit#InputEdit:focus {
    border: 1px solid #38BDF8;
    background: rgba(255, 255, 255, 0.10);
}

/* ── Action Bar Buttons ── */
QPushButton#ActionBtn {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 8px;
    min-width: 30px;
    min-height: 30px;
}
QPushButton#ActionBtn:hover {
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.22);
}
QPushButton#ActionBtn:pressed {
    background: rgba(2, 132, 199, 0.30);
}

/* ── Send Button ── */
QPushButton#SendBtn {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #0071E3,
        stop:1 #0056B3
    );
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 10px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
}
QPushButton#SendBtn:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #38BDF8,
        stop:1 #0071E3
    );
    border-color: rgba(255, 255, 255, 0.40);
}
QPushButton#SendBtn:disabled {
    background: rgba(255, 255, 255, 0.06);
    border: none;
}

/* ── Window Control Buttons ── */
QPushButton#WinBtn {
    background: transparent;
    border: none;
    color: #CBD5E1;
    font-size: 13px;
    border-radius: 6px;
    min-width: 28px;
    min-height: 28px;
}
QPushButton#WinBtn:hover {
    background: rgba(255, 179, 0, 0.35);
    color: #FFFFFF;
}
QPushButton#CloseBtn {
    background: transparent;
    border: none;
    color: #CBD5E1;
    font-size: 13px;
    border-radius: 6px;
    min-width: 28px;
    min-height: 28px;
}
QPushButton#CloseBtn:hover {
    background: rgba(255, 69, 58, 0.50);
    color: #FFFFFF;
}

/* ── Settings Dialog ── */
QDialog#SettingsDialog {
    background: transparent;
}
QFrame#SettingsCardFrame {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.16),
        stop:0.03 rgba(255, 255, 255, 0.06),
        stop:0.18 rgba(24, 28, 38, 0.94),
        stop:1 rgba(14, 16, 24, 0.98)
    );
    border: 1px solid rgba(255, 255, 255, 0.20);
    border-radius: 20px;
}
QLabel#SectionLabel {
    color: #38BDF8;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    background: transparent;
}
QLineEdit#SettingsField {
    background: rgba(255, 255, 255, 0.07);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
    selection-background-color: #0284C7;
}
QLineEdit#SettingsField:focus {
    border-color: #38BDF8;
    background: rgba(255, 255, 255, 0.10);
}
QComboBox#SettingsCombo {
    background: rgba(255, 255, 255, 0.07);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
}
QComboBox#SettingsCombo::drop-down {
    border: none;
    width: 24px;
}
QComboBox#SettingsCombo QAbstractItemView {
    background: rgba(24, 28, 38, 0.98);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.18);
    selection-background-color: #0284C7;
}
QTextEdit#PromptEdit {
    background: rgba(255, 255, 255, 0.07);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
    selection-background-color: #0284C7;
}
QTextEdit#PromptEdit:focus {
    border-color: #38BDF8;
}
QPushButton#PrimaryBtn {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #0071E3,
        stop:1 #0056B3
    );
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 8px;
    padding: 7px 20px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#PrimaryBtn:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #38BDF8,
        stop:1 #0071E3
    );
}
QPushButton#SecondaryBtn {
    background: rgba(255, 255, 255, 0.07);
    color: #CBD5E1;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 7px 20px;
    font-size: 13px;
}
QPushButton#SecondaryBtn:hover {
    background: rgba(255, 255, 255, 0.12);
    color: #FFFFFF;
}

/* ── Global scrollbar ── */
QScrollBar:vertical {
    background: transparent;
    width: 5px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.20);
    border-radius: 2px;
    min-height: 20px;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical { background: none; }
"""

PALETTE = RIKKA_PALETTE
MAIN_QSS = RIKKA_QSS


def get_theme_qss(mode: str) -> str:
    """Return the corresponding stylesheet for the given mode."""
    if mode.lower() == "normal":
        return FROSTED_QSS
    return RIKKA_QSS
