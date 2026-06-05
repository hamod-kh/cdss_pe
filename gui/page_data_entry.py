from __future__ import annotations
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QScrollArea, QComboBox, QGridLayout,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

import config.config as C
from gui.widgets import (
    make_card, make_warning_card, make_hint_card,
    make_primary_button, make_secondary_button, make_risk_badge,
    section_title_label, h_bold, h_muted, numeric_line_edit,
    TriStateButtonGroup
)
from data.data_model import InputHandler, PatientData


class DataEntryPage(QWidget):
    """
    Page 1 – vital signs, labs/imaging, symptoms, and risk-factor entry.
    Emits ``go_next()`` / ``go_back()`` when navigation is requested.
    """

    go_next = pyqtSignal()
    go_back = pyqtSignal()

    def __init__(self, handler: InputHandler, parent=None) -> None:
        super().__init__(parent)
        self._h = handler
        self._vital_inputs: dict[str, QLineEdit] = {}
        self._lab_inputs: dict[str, QLineEdit] = {}
        self._symptom_groups: dict[str, TriStateButtonGroup] = {}
        self._triage_combo: QComboBox | None = None
        self._build_ui()

    # build ui

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ──
        header = self._build_patient_header()
        root.addWidget(header)

        # ── Scrollable content ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(14)

        content_layout.addWidget(self._build_left_column(), stretch=2)
        content_layout.addWidget(self._build_middle_column(), stretch=3)
        content_layout.addWidget(self._build_right_column(), stretch=2)

        scroll.setWidget(content)
        root.addWidget(scroll, stretch=1)

        # footer
        root.addWidget(self._build_footer())

    # patient header

    def _build_patient_header(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        frame.setStyleSheet(
            f"background: white; border-bottom: 2px solid {C.COLOR_BORDER}; border-radius: 0px;"
        )
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 12, 20, 12)

        # avatar
        avatar = QLabel("👤")
        avatar.setFixedSize(44, 44)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(
            "font-size: 22px; border: 2px solid #DEE2E6; border-radius: 22px;"
        )
        layout.addWidget(avatar)

        self._name_lbl = QLabel("—")
        self._mrn_lbl = QLabel("MRN —")
        self._age_lbl = QLabel("Age —")
        self._sex_lbl = QLabel("Sex —")

        for lbl in (self._name_lbl,):
            f = QFont()
            f.setBold(True)
            f.setPointSize(14)
            lbl.setFont(f)

        layout.addWidget(self._name_lbl)
        layout.addSpacing(20)

        for lbl in (self._mrn_lbl, self._age_lbl, self._sex_lbl):
            layout.addWidget(lbl)
            layout.addSpacing(12)

        # triage
        triage_lbl = QLabel("Triage")
        triage_lbl.setStyleSheet(f"color: {C.COLOR_TEXT_MUTED}; font-size: 11px;")
        self._triage_combo = QComboBox()
        self._triage_combo.addItems(C.TRIAGE_OPTIONS)
        self._triage_combo.currentTextChanged.connect(
            lambda t: self._h.stage_update("triage", t)
        )
        layout.addWidget(triage_lbl)
        layout.addWidget(self._triage_combo)

        layout.addStretch()

        pe_lbl = QLabel(C.PE_RISK_LABEL)
        pe_lbl.setStyleSheet(f"color: {C.COLOR_TEXT_MUTED}; font-size: 11px;")
        layout.addWidget(pe_lbl)

        self._risk_badge = make_risk_badge("—")
        layout.addWidget(self._risk_badge)

        return frame

    # left: vitals and labs
    def _build_left_column(self) -> QWidget:
        col = QWidget()
        layout = QVBoxLayout(col)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(self._build_vitals_card())
        layout.addWidget(self._build_labs_card())
        return col

    def _build_vitals_card(self) -> QFrame:
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        header_row = QHBoxLayout()
        header_row.addWidget(section_title_label(C.SECTION_VITAL_SIGNS))
        self._vitals_time_lbl = h_muted("")
        header_row.addStretch()
        header_row.addWidget(self._vitals_time_lbl)
        layout.addLayout(header_row)

        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)

        for row_i, (key, label, unit) in enumerate(C.VITAL_FIELDS):
            lbl = QLabel(label)
            lbl.setFixedWidth(50)
            le = numeric_line_edit(placeholder="—", decimals=(key == "temp"))
            le.textChanged.connect(lambda v, k=key: self._h.stage_update(k, v))
            unit_lbl = QLabel(unit)
            unit_lbl.setStyleSheet(f"color: {C.COLOR_TEXT_MUTED};")
            self._vital_inputs[key] = le
            grid.addWidget(lbl, row_i, 0)
            grid.addWidget(le, row_i, 1)
            grid.addWidget(unit_lbl, row_i, 2)

        layout.addLayout(grid)

        # update time
        self._update_vitals_time()

        return card

    def _update_vitals_time(self) -> None:
        now = datetime.now().strftime("%H:%M")
        self._vitals_time_lbl.setText(f"{C.VITAL_LAST_UPDATED} {now}")
        self._h.stage_update("vitals_time", now)

    def _build_labs_card(self) -> QFrame:
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)
        layout.addWidget(section_title_label(C.SECTION_LABS_IMAGING))

        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)

        for row_i, (key, label, unit) in enumerate(C.LAB_FIELDS):
            lbl = QLabel(label)
            le = numeric_line_edit(placeholder="—", decimals=True)
            le.setFixedWidth(100)
            le.textChanged.connect(lambda v, k=key: self._h.stage_update(k, v))
            unit_lbl = QLabel(unit)
            unit_lbl.setStyleSheet(f"color: {C.COLOR_TEXT_MUTED};")
            self._lab_inputs[key] = le
            grid.addWidget(lbl, row_i, 0)
            grid.addWidget(le, row_i, 1)
            grid.addWidget(unit_lbl, row_i, 2)

        layout.addLayout(grid)

        add_lbl = QLabel(C.LAB_ADD_RESULT)
        add_lbl.setStyleSheet(f"color: {C.COLOR_PRIMARY}; font-size: 12px;")
        layout.addWidget(add_lbl)

        return card

    # middle panel: symptoms
    def _build_middle_column(self) -> QFrame:
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        # Header row with column labels
        header = QHBoxLayout()
        header.addWidget(section_title_label(C.SECTION_SYMPTOMS))
        header.addStretch()
        for col_lbl in (C.BTN_YES, C.BTN_NO, C.BTN_UNKNOWN):
            lbl = h_muted(col_lbl)
            lbl.setFixedWidth(80)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.addWidget(lbl)
        layout.addLayout(header)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"color: {C.COLOR_BORDER};")
        layout.addWidget(separator)

        for key, label in C.SYMPTOM_FIELDS:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setWordWrap(True)
            lbl.setMinimumWidth(180)
            row.addWidget(lbl, stretch=1)

            grp = TriStateButtonGroup(default="Unknown")
            grp.value_changed.connect(lambda v, k=key: self._h.stage_update(k, v))
            self._symptom_groups[key] = grp
            row.addWidget(grp)
            layout.addLayout(row)

        layout.addStretch()
        return card

    # right panel: missing data and hints

    def _build_right_column(self) -> QWidget:
        col = QWidget()
        layout = QVBoxLayout(col)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Missing / incomplete
        self._missing_card = make_warning_card()
        m_layout = QVBoxLayout(self._missing_card)
        m_layout.setContentsMargins(12, 10, 12, 10)
        m_layout.setSpacing(6)

        miss_title_row = QHBoxLayout()
        miss_title_row.addWidget(QLabel("⚠"))
        miss_title_row.addWidget(section_title_label(C.SECTION_MISSING_DATA))
        miss_title_row.addStretch()
        m_layout.addLayout(miss_title_row)

        self._missing_labels: list[QLabel] = []
        for _ in range(5):
            lbl = QLabel("")
            lbl.setWordWrap(True)
            lbl.setStyleSheet("font-size: 12px;")
            self._missing_labels.append(lbl)
            m_layout.addWidget(lbl)

        review_lbl = QLabel(C.MISSING_REVIEW_LINK)
        review_lbl.setStyleSheet(f"color: {C.COLOR_PRIMARY}; font-size: 12px;")
        m_layout.addWidget(review_lbl)

        layout.addWidget(self._missing_card)

        # Hints
        self._hints_card = make_hint_card()
        h_layout = QVBoxLayout(self._hints_card)
        h_layout.setContentsMargins(12, 10, 12, 10)
        h_layout.setSpacing(6)

        hint_title_row = QHBoxLayout()
        hint_title_row.addWidget(QLabel("💡"))
        hint_title_row.addWidget(section_title_label(C.SECTION_PE_HINTS))
        hint_title_row.addStretch()
        h_layout.addLayout(hint_title_row)

        self._hint_labels: list[QLabel] = []
        for _ in range(5):
            lbl = QLabel("")
            lbl.setWordWrap(True)
            lbl.setStyleSheet("font-size: 12px;")
            self._hint_labels.append(lbl)
            h_layout.addWidget(lbl)

        self._pattern_suggestion = QLabel("")
        self._pattern_suggestion.setWordWrap(True)
        self._pattern_suggestion.setStyleSheet("font-size: 12px; font-weight: 600;")
        h_layout.addWidget(self._pattern_suggestion)

        layout.addWidget(self._hints_card)
        layout.addStretch()

        return col

    # footer

    def _build_footer(self) -> QFrame:
        bar = QFrame()
        bar.setStyleSheet(
            f"background: {C.COLOR_PANEL_BG}; border-top: 1px solid {C.COLOR_BORDER};"
        )
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 10, 20, 10)

        layout.addWidget(h_muted("All times local"))
        layout.addStretch()
        layout.addWidget(h_muted(C.SOURCE_LABEL))

        layout.addSpacing(20)
        back_btn = make_secondary_button(C.BTN_BACK)
        back_btn.clicked.connect(self._on_back)
        layout.addWidget(back_btn)

        next_btn = make_primary_button(C.BTN_NEXT)
        next_btn.clicked.connect(self._on_next)
        layout.addWidget(next_btn)

        return bar

    # Populate (called when page is loaded/revisited)

    def populate(self) -> None:
        """Refresh all widgets from the committed PatientData."""
        d = self._h.current

        # header
        self._name_lbl.setText(d.full_name or "—")
        self._mrn_lbl.setText(f"MRN  {d.mrn}")
        self._age_lbl.setText(f"Age  {d.age} y" if d.age else "Age —")
        self._sex_lbl.setText(f"Sex  {d.sex}" if d.sex else "Sex —")

        if d.triage and self._triage_combo:
            idx = self._triage_combo.findText(d.triage)
            if idx >= 0:
                self._triage_combo.setCurrentIndex(idx)

        # vitals
        for key, le in self._vital_inputs.items():
            le.blockSignals(True)
            le.setText(getattr(d, key, ""))
            le.blockSignals(False)

        # labs
        for key, le in self._lab_inputs.items():
            le.blockSignals(True)
            le.setText(getattr(d, key, ""))
            le.blockSignals(False)

        # symptoms
        for key, grp in self._symptom_groups.items():
            grp.set_value(getattr(d, key, "Unknown"))

        self._update_missing_panel()
        self._update_hints_panel()
        self._update_risk_badge()

    # Dynamic panel updates

    def _update_missing_panel(self) -> None:
        missing = self._h.current.missing_critical_fields()
        for i, lbl in enumerate(self._missing_labels):
            if i < len(missing):
                lbl.setText(f"• {missing[i]}")
                lbl.setVisible(True)
            else:
                lbl.setText("")
                lbl.setVisible(False)

    def _update_hints_panel(self) -> None:
        hints = self._h.build_pe_pattern_hints()
        for i, lbl in enumerate(self._hint_labels):
            if i < len(hints):
                lbl.setText(f"• {hints[i]}")
                lbl.setVisible(True)
            else:
                lbl.setText("")
                lbl.setVisible(False)

        if hints:
            self._pattern_suggestion.setText(
                "Pattern suggests: Increased likelihood of PE"
            )
        else:
            self._pattern_suggestion.setText("")

    def _update_risk_badge(self) -> None:
        risk = self._h.current.wells_risk
        self._risk_badge.setText(risk if risk else "—")
        if "HIGH" in risk:
            self._risk_badge.setObjectName("badge_high")
        elif "MODERATE" in risk:
            self._risk_badge.setObjectName("badge_moderate")
        elif "LOW" in risk:
            self._risk_badge.setObjectName("badge_low")
        else:
            self._risk_badge.setObjectName("badge_unknown")
        # Force style re-evaluation
        self._risk_badge.style().unpolish(self._risk_badge)
        self._risk_badge.style().polish(self._risk_badge)

    # bavigation

    def _on_next(self) -> None:
        self._h.commit()
        self._update_missing_panel()
        self._update_hints_panel()
        self.go_next.emit()

    def _on_back(self) -> None:
        self._h.discard()
        self.go_back.emit()
