from __future__ import annotations
import math

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QProgressBar, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush

import config.config as C
from gui.widgets import (
    make_card, make_primary_button, make_secondary_button,
    section_title_label, h_bold, h_muted, make_risk_badge,
    TriStateButtonGroup
)
from data.data_model import InputHandler
from logger.logger import log_wells_score


# Circular score gauge
class ScoreGauge(QWidget):
    """Draws a circular arc gauge displaying the Wells score."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._score: float = 0.0
        self._risk: str = ""
        self.setFixedSize(200, 200)

    def set_score(self, score: float, risk: str) -> None:
        self._score = score
        self._risk = risk
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        r = min(cx, cy) - 12

        # background arc
        p.setPen(QPen(QColor("#E9ECEF"), 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(int(cx - r), int(cy - r), int(2 * r), int(2 * r), 30 * 16, 300 * 16)

        # coloured progress arc
        colour = (
            C.COLOR_HIGH_RISK if "HIGH" in self._risk else
            C.COLOR_MODERATE if "MODERATE" in self._risk else
            C.COLOR_LOW_RISK if "LOW" in self._risk else
            C.COLOR_PRIMARY
        )
        p.setPen(QPen(QColor(colour), 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        max_score = 12.5
        fraction = min(self._score / max_score, 1.0)
        span = int(fraction * 300 * 16)
        p.drawArc(int(cx - r), int(cy - r), int(2 * r), int(2 * r), 210 * 16, -span)

        # score text
        font = QFont("Segoe UI", 32, QFont.Weight.Bold)
        p.setFont(font)
        p.setPen(QColor(colour))
        score_str = f"{self._score:.1f}"
        fm = p.fontMetrics()
        p.drawText(
            int(cx - fm.horizontalAdvance(score_str) / 2),
            int(cy + fm.ascent() / 2 - 16),
            score_str,
        )

        # risk label
        font2 = QFont("Segoe UI", 9, QFont.Weight.Bold)
        p.setFont(font2)
        p.setPen(QColor(colour))
        risk_lbl = self._risk or "—"
        fm2 = p.fontMetrics()
        p.drawText(
            int(cx - fm2.horizontalAdvance(risk_lbl) / 2),
            int(cy + 22),
            risk_lbl,
        )

        # subtitle
        if self._risk:
            font3 = QFont("Segoe UI", 8)
            p.setFont(font3)
            p.setPen(QColor(C.COLOR_TEXT_MUTED))
            sub = "(> 6)" if "HIGH" in self._risk else "(4.5–6)" if "MODERATE" in self._risk else "(≤ 4)"
            fm3 = p.fontMetrics()
            p.drawText(int(cx - fm3.horizontalAdvance(sub) / 2), int(cy + 38), sub)

        p.end()


# WellsScorePage

class WellsScorePage(QWidget):
    """
    Page 2 – presents the seven Wells criteria as tri-state button groups,
    computes and displays the score in real-time.
    Emits ``go_next()`` / ``go_back()``.
    """

    go_next = pyqtSignal()
    go_back = pyqtSignal()

    def __init__(self, handler: InputHandler, parent=None) -> None:
        super().__init__(parent)
        self._h = handler
        self._criteria_groups: dict[str, TriStateButtonGroup] = {}
        self._build_ui()

    # UI build

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(16)

        content_layout.addWidget(self._build_criteria_card(), stretch=3)
        content_layout.addWidget(self._build_breakdown_card(), stretch=2)

        scroll.setWidget(content)
        root.addWidget(scroll, stretch=1)
        root.addWidget(self._build_footer())

    # Criteria card

    def _build_criteria_card(self) -> QFrame:
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(0)

        # Column headers
        header = QHBoxLayout()
        header.addWidget(section_title_label(C.WELLS_TITLE), stretch=1)
        for col in (C.WELLS_COL_NO, C.WELLS_COL_YES, C.WELLS_COL_UNKNOWN):
            lbl = h_muted(col)
            lbl.setFixedWidth(90)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.addWidget(lbl)
        layout.addLayout(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C.COLOR_BORDER}; margin: 6px 0;")
        layout.addWidget(sep)

        for key, label, points in C.WELLS_CRITERIA:
            row = QHBoxLayout()
            row.setContentsMargins(0, 4, 0, 4)

            criterion_lbl = QLabel(f"{label}  ({points})")
            criterion_lbl.setWordWrap(True)
            criterion_lbl.setMinimumWidth(260)
            row.addWidget(criterion_lbl, stretch=1)

            grp = TriStateButtonGroup(default="Unknown")
            # Each group has buttons ordered NO, YES, UNKNOWN with width 80 each
            grp.value_changed.connect(lambda v, k=key: self._on_criterion_changed(k, v))
            self._criteria_groups[key] = grp
            row.addWidget(grp)

            layout.addLayout(row)

            sep2 = QFrame()
            sep2.setFrameShape(QFrame.Shape.HLine)
            sep2.setStyleSheet(f"color: {C.COLOR_BORDER};")
            layout.addWidget(sep2)

        # Scale note
        note = h_muted(C.WELLS_SCALE_NOTE)
        note.setWordWrap(True)
        note.setStyleSheet(
            f"background: {C.COLOR_PANEL_BG}; border: 1px solid {C.COLOR_BORDER}; "
            "border-radius: 6px; padding: 8px; font-size: 12px;"
        )
        layout.addSpacing(8)
        layout.addWidget(note)

        return card

    # breakdown card

    def _build_breakdown_card(self) -> QFrame:
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Gauge
        self._gauge = ScoreGauge()
        layout.addWidget(self._gauge, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Breakdown table
        layout.addWidget(section_title_label(C.WELLS_SCORE_BREAKDOWN))

        def add_row(label: str, value_lbl: QLabel, bold: bool = False) -> None:
            r = QHBoxLayout()
            lbl = QLabel(label)
            if bold:
                f = QFont()
                f.setBold(True)
                lbl.setFont(f)
                value_lbl.setFont(f)
            r.addWidget(lbl)
            r.addStretch()
            r.addWidget(value_lbl)
            layout.addLayout(r)
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet(f"color: {C.COLOR_BORDER};")
            layout.addWidget(sep)

        self._criteria_total_lbl = QLabel("0.0")
        self._adjustment_lbl = QLabel("0.0")
        self._score_total_lbl = QLabel("0.0")
        self._risk_level_lbl = QLabel("—")

        add_row(C.WELLS_CRITERIA_TOTAL, self._criteria_total_lbl)
        add_row(C.WELLS_ADJUSTMENT, self._adjustment_lbl)
        add_row(C.WELLS_SCORE_TOTAL, self._score_total_lbl, bold=True)
        add_row(C.WELLS_RISK_LABEL, self._risk_level_lbl, bold=True)

        layout.addSpacing(8)

        # Completeness
        layout.addWidget(section_title_label(C.WELLS_DATA_COMPLETENESS))

        self._completeness_bar = QProgressBar()
        self._completeness_bar.setRange(0, 100)
        self._completeness_bar.setValue(0)
        self._completeness_bar.setTextVisible(False)
        self._completeness_bar.setFixedHeight(14)
        layout.addWidget(self._completeness_bar)

        self._completeness_lbl = QLabel("")
        self._completeness_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._completeness_lbl.setStyleSheet("font-size: 20px; font-weight: 700;")
        layout.addWidget(self._completeness_lbl)

        self._elements_lbl = h_muted("")
        self._elements_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._elements_lbl)

        view_missing = QLabel(C.WELLS_VIEW_MISSING)
        view_missing.setStyleSheet(f"color: {C.COLOR_PRIMARY}; font-size: 12px;")
        view_missing.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(view_missing)

        layout.addStretch()
        return card

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

        self._proceed_btn = make_primary_button(C.BTN_PROCEED)
        self._proceed_btn.clicked.connect(self._on_next)
        layout.addWidget(self._proceed_btn)

        return bar

    # populate

    def populate(self) -> None:
        """Sync criteria toggles from committed data and recompute score."""
        d = self._h.current
        for key, grp in self._criteria_groups.items():
            grp.set_value(getattr(d, key, "Unknown"))
        self._recompute()

    # score computation

    def _on_criterion_changed(self, key: str, value: str) -> None:
        self._h.stage_update(key, value)
        # Temporarily commit criteria to allow score preview
        staged_copy = dict(self._h._staged)  # peek at staged
        saved_committed = self._h.current.to_dict()

        # Compute live preview by merging staged into committed
        merged = {**saved_committed, **staged_copy}
        from data_model import PatientData
        preview = PatientData.from_dict(merged)

        score = 0.0
        for k, _label, pts in C.WELLS_CRITERIA:
            if getattr(preview, k, "Unknown") == "Yes":
                score += pts
        score = round(score, 1)

        if score <= 4.0:
            risk = C.RISK_LOW
        elif score <= 6.0:
            risk = C.RISK_MODERATE
        else:
            risk = C.RISK_HIGH

        self._update_display(score, risk)

    def _recompute(self) -> None:
        score, risk = self._h.compute_wells_score()
        self._update_display(score, risk)

    def _update_display(self, score: float, risk: str) -> None:
        self._gauge.set_score(score, risk)
        self._criteria_total_lbl.setText(f"{score:.1f}")
        self._adjustment_lbl.setText("0.0")
        self._score_total_lbl.setText(f"{score:.1f}")
        self._risk_level_lbl.setText(risk or "—")

        colour = (
            C.COLOR_HIGH_RISK if "HIGH" in risk else
            C.COLOR_MODERATE if "MODERATE" in risk else
            C.COLOR_LOW_RISK if "LOW" in risk else
            C.COLOR_TEXT_MUTED
        )
        self._risk_level_lbl.setStyleSheet(f"color: {colour}; font-weight: 700;")
        self._score_total_lbl.setStyleSheet(f"color: {colour};")

        filled, total = self._h.data_completeness()
        pct = int(filled / total * 100) if total else 0
        self._completeness_bar.setValue(pct)
        self._completeness_lbl.setText(f"{pct}%")
        self._elements_lbl.setText(f"{filled} of {total} {C.WELLS_ELEMENTS_LABEL}")

    def _on_next(self) -> None:
        # Commit criteria + score into the handler
        self._h.commit()
        score, risk = self._h.compute_wells_score()
        self._h.stage_update("wells_score", score)
        self._h.stage_update("wells_risk", risk)
        self._h.commit()
        log_wells_score(self._h.current.mrn, score, risk)
        self.go_next.emit()

    def _on_back(self) -> None:
        self._h.discard()
        self.go_back.emit()
