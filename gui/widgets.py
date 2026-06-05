from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QLabel, QFrame, QPushButton, QButtonGroup,
    QLineEdit, QHBoxLayout, QVBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QDoubleValidator, QIntValidator

import config.config as C


# Global stylesheet
APP_STYLESHEET = f"""
/* ── Global ── */
QWidget {{
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
    color: #212529;
    background-color: {C.COLOR_WHITE};
}}

QScrollArea {{ border: none; background-color: {C.COLOR_WHITE}; }}
QScrollBar:vertical  {{ width: 8px;  background: #F1F3F5; }}
QScrollBar::handle:vertical {{ background: #ADB5BD; border-radius: 4px; }}

/* ── Buttons ── */
QPushButton {{
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton#primary {{
    background-color: {C.COLOR_PRIMARY};
    color: white;
    border: none;
}}
QPushButton#primary:hover  {{ background-color: {C.COLOR_PRIMARY_DARK}; }}
QPushButton#primary:pressed{{ background-color: #064a4d; }}

QPushButton#secondary {{
    background-color: white;
    color: {C.COLOR_PRIMARY};
    border: 2px solid {C.COLOR_PRIMARY};
}}
QPushButton#secondary:hover  {{ background-color: {C.COLOR_LIGHT_TEAL}; }}

QPushButton#danger {{
    background-color: white;
    color: {C.COLOR_HIGH_RISK};
    border: 2px solid {C.COLOR_HIGH_RISK};
}}
QPushButton#danger:hover {{ background-color: #FDECEA; }}

QPushButton#tristate {{
    background-color: white;
    color: #495057;
    border: 1.5px solid #CED4DA;
    padding: 5px 12px;
    font-weight: 500;
}}
QPushButton#tristate:checked {{
    background-color: {C.COLOR_PRIMARY};
    color: white;
    border: 2px solid {C.COLOR_PRIMARY};
}}
QPushButton#tristate:hover:!checked {{ background-color: {C.COLOR_LIGHT_TEAL}; }}

/* ── Inputs ── */
QLineEdit {{
    border: 1.5px solid #CED4DA;
    border-radius: 5px;
    padding: 5px 8px;
    font-size: 13px;
    background-color: white;
}}
QLineEdit:focus {{ border-color: {C.COLOR_PRIMARY}; }}
QLineEdit:disabled {{ background-color: #F8F9FA; color: #ADB5BD; }}

QComboBox {{
    border: 1.5px solid #CED4DA;
    border-radius: 5px;
    padding: 5px 8px;
    font-size: 13px;
    background-color: white;
}}
QComboBox:focus {{ border-color: {C.COLOR_PRIMARY}; }}
QComboBox::drop-down {{ border: none; }}

/* ── Cards / panels ── */
QFrame#card {{
    background-color: white;
    border: 1.5px solid {C.COLOR_BORDER};
    border-radius: 8px;
}}
QFrame#warning_card {{
    background-color: {C.COLOR_MISSING_BG};
    border: 1.5px solid {C.COLOR_WARNING_BORDER};
    border-radius: 8px;
}}
QFrame#hint_card {{
    background-color: {C.COLOR_HINT_BG};
    border: 1.5px solid #B2DFF0;
    border-radius: 8px;
}}
QFrame#section_header {{
    background-color: {C.COLOR_PANEL_BG};
    border-bottom: 1.5px solid {C.COLOR_BORDER};
    border-radius: 0px;
}}

/* ── Tables ── */
QTableWidget {{
    border: 1.5px solid {C.COLOR_BORDER};
    border-radius: 6px;
    gridline-color: {C.COLOR_BORDER};
    alternate-background-color: #F8F9FA;
}}
QTableWidget::item:selected {{
    background-color: {C.COLOR_LIGHT_TEAL};
    color: #212529;
}}
QHeaderView::section {{
    background-color: {C.COLOR_PANEL_BG};
    padding: 6px 10px;
    font-weight: 600;
    border: none;
    border-bottom: 1.5px solid {C.COLOR_BORDER};
}}

/* ── Risk badges ── */
QLabel#badge_high {{
    background-color: {C.COLOR_HIGH_RISK};
    color: white;
    border-radius: 6px;
    padding: 4px 12px;
    font-weight: 700;
    font-size: 13px;
}}
QLabel#badge_moderate {{
    background-color: {C.COLOR_MODERATE};
    color: white;
    border-radius: 6px;
    padding: 4px 12px;
    font-weight: 700;
    font-size: 13px;
}}
QLabel#badge_low {{
    background-color: {C.COLOR_LOW_RISK};
    color: white;
    border-radius: 6px;
    padding: 4px 12px;
    font-weight: 700;
    font-size: 13px;
}}
QLabel#badge_unknown {{
    background-color: #6C757D;
    color: white;
    border-radius: 6px;
    padding: 4px 12px;
    font-weight: 700;
    font-size: 13px;
}}

QProgressBar {{
    border: 1.5px solid {C.COLOR_BORDER};
    border-radius: 6px;
    text-align: center;
    background: #E9ECEF;
    height: 14px;
}}
QProgressBar::chunk {{
    background-color: {C.COLOR_PRIMARY};
    border-radius: 6px;
}}
"""


# help functions

def h_bold(text: str, size: int = 13) -> QLabel:
    lbl = QLabel(text)
    f = QFont()
    f.setBold(True)
    f.setPointSize(size)
    lbl.setFont(f)
    return lbl


def h_muted(text: str, size: int = 11) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color: {C.COLOR_TEXT_MUTED}; font-size: {size}px;")
    return lbl


def make_card(parent=None) -> QFrame:
    f = QFrame(parent)
    f.setObjectName("card")
    return f


def make_warning_card(parent=None) -> QFrame:
    f = QFrame(parent)
    f.setObjectName("warning_card")
    return f


def make_hint_card(parent=None) -> QFrame:
    f = QFrame(parent)
    f.setObjectName("hint_card")
    return f


def make_risk_badge(risk: str) -> QLabel:
    lbl = QLabel(risk)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    if "HIGH" in risk:
        lbl.setObjectName("badge_high")
    elif "MODERATE" in risk:
        lbl.setObjectName("badge_moderate")
    elif "LOW" in risk:
        lbl.setObjectName("badge_low")
    else:
        lbl.setObjectName("badge_unknown")
    lbl.setMinimumWidth(100)
    return lbl


def make_primary_button(text: str) -> QPushButton:
    b = QPushButton(text)
    b.setObjectName("primary")
    b.setMinimumHeight(38)
    return b


def make_secondary_button(text: str) -> QPushButton:
    b = QPushButton(text)
    b.setObjectName("secondary")
    b.setMinimumHeight(38)
    return b


def make_danger_button(text: str) -> QPushButton:
    b = QPushButton(text)
    b.setObjectName("danger")
    b.setMinimumHeight(38)
    return b


def numeric_line_edit(placeholder: str = "", width: int = 110, decimals: bool = False) -> QLineEdit:
    """Line edit that only accepts numeric input."""
    le = QLineEdit()
    le.setPlaceholderText(placeholder)
    le.setFixedWidth(width)
    if decimals:
        le.setValidator(QDoubleValidator(0, 99999, 2))
    else:
        le.setValidator(QIntValidator(0, 99999))
    return le


def section_title_label(text: str) -> QLabel:
    lbl = QLabel(text)
    font = QFont()
    font.setBold(True)
    font.setPointSize(10)
    lbl.setFont(font)
    lbl.setStyleSheet(f"color: {C.COLOR_PRIMARY}; letter-spacing: 1px;")
    return lbl


# TriStateButtonGroup

class TriStateButtonGroup(QWidget):
    """
    A row of three exclusive toggle buttons: Yes / No / Unknown.
    Emits ``value_changed(str)`` whenever the selection changes.
    """

    value_changed = pyqtSignal(str)

    STATES = [C.BTN_YES, C.BTN_NO, C.BTN_UNKNOWN]

    def __init__(self, parent=None, default: str = "Unknown") -> None:
        super().__init__(parent)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._buttons: dict[str, QPushButton] = {}
        for idx, state in enumerate(self.STATES):
            btn = QPushButton(state)
            btn.setObjectName("tristate")
            btn.setCheckable(True)
            btn.setFixedSize(80, 30)
            self._group.addButton(btn, idx)
            layout.addWidget(btn)
            self._buttons[state] = btn

        self._group.idClicked.connect(self._on_clicked)
        self.set_value(default)

    def _on_clicked(self, idx: int) -> None:
        self.value_changed.emit(self.STATES[idx])

    def set_value(self, val: str) -> None:
        for state, btn in self._buttons.items():
            btn.setChecked(state == val)

    def value(self) -> str:
        checked_id = self._group.checkedId()
        if checked_id < 0:
            return "Unknown"
        return self.STATES[checked_id]


# StepIndicator

class StepIndicator(QWidget):
    """Horizontal progress indicator showing numbered steps."""

    def __init__(self, steps: list[str], parent=None) -> None:
        super().__init__(parent)
        self._steps = steps
        self._current = 0

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 8, 0, 8)
        self._layout.setSpacing(0)

        self._circles: list[QLabel] = []
        self._labels:  list[QLabel] = []
        self._connectors: list[QFrame] = []

        for i, step in enumerate(steps):
            # circle
            circle = QLabel(str(i + 1))
            circle.setFixedSize(30, 30)
            circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._circles.append(circle)
            self._layout.addWidget(circle)

            # label
            lbl = QLabel(step)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._labels.append(lbl)
            self._layout.addWidget(lbl)

            if i < len(steps) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setFixedHeight(2)
                line.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
                )
                self._connectors.append(line)
                self._layout.addWidget(line)

        self._refresh()

    def set_step(self, idx: int) -> None:
        self._current = idx
        self._refresh()

    def _refresh(self) -> None:
        for i, (circle, lbl) in enumerate(zip(self._circles, self._labels)):
            if i < self._current:
                circle.setStyleSheet(
                    f"background:{C.COLOR_PRIMARY}; color:white; border-radius:15px; font-weight:700;"
                )
                lbl.setStyleSheet(f"color:{C.COLOR_PRIMARY}; font-weight:600; font-size:12px;")
            elif i == self._current:
                circle.setStyleSheet(
                    f"background:{C.COLOR_PRIMARY}; color:white; border-radius:15px; font-weight:700;"
                    f"border: 3px solid {C.COLOR_PRIMARY_DARK};"
                )
                lbl.setStyleSheet(f"color:{C.COLOR_PRIMARY}; font-weight:700; font-size:12px;")
            else:
                circle.setStyleSheet(
                    "background:#DEE2E6; color:#6C757D; border-radius:15px; font-weight:600;"
                )
                lbl.setStyleSheet("color:#6C757D; font-size:12px;")

        for i, line in enumerate(self._connectors):
            if i < self._current:
                line.setStyleSheet(f"background:{C.COLOR_PRIMARY}; border:none;")
            else:
                line.setStyleSheet("background:#DEE2E6; border:none;")
