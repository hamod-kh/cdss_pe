from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QPushButton, QComboBox, QTextEdit,
    QCheckBox, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

import config.config as C
from gui.widgets import (
    make_card, make_primary_button, make_secondary_button,
    make_danger_button, section_title_label, h_bold, h_muted
)
from data.data_model import InputHandler
from logger.logger import (
    log_recommendation, log_physician_decision, log_missing_data
)


class RecommendationsPage(QWidget):
    """
    Page 3 – shows the clinical recommendation derived from the Wells score,
    allows the physician to accept or override, and collects comments.
    Emits ``go_back()`` and ``assessment_done()``.
    """

    go_back = pyqtSignal()
    assessment_done = pyqtSignal()

    def __init__(self, handler: InputHandler, parent=None) -> None:
        super().__init__(parent)
        self._h = handler
        self._action_checks: list[QCheckBox] = []
        self._build_ui()

    # buil ui

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

        content_layout.addWidget(self._build_left_panel(), stretch=3)
        content_layout.addWidget(self._build_right_panel(), stretch=2)

        scroll.setWidget(content)
        root.addWidget(scroll, stretch=1)
        root.addWidget(self._build_footer())

    # left panel

    def _build_left_panel(self) -> QFrame:
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Recommended next step
        rec_row = QHBoxLayout()
        icon = QLabel("📋")
        icon.setFixedSize(44, 44)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            f"font-size: 22px; border: 2px solid {C.COLOR_PRIMARY}; "
            "border-radius: 22px;"
        )
        rec_row.addWidget(icon)

        rec_text_col = QVBoxLayout()
        rec_label = h_muted(C.SECTION_RECOMMENDED_STEP)
        rec_text_col.addWidget(rec_label)

        self._rec_title_lbl = QLabel("—")
        f = QFont()
        f.setBold(True)
        f.setPointSize(14)
        self._rec_title_lbl.setFont(f)
        self._rec_title_lbl.setStyleSheet(f"color: {C.COLOR_PRIMARY};")
        rec_text_col.addWidget(self._rec_title_lbl)

        self._strength_lbl = QLabel("")
        self._strength_lbl.setStyleSheet(
            f"border: 1.5px solid {C.COLOR_PRIMARY}; color: {C.COLOR_PRIMARY}; "
            "border-radius: 4px; padding: 2px 8px; font-weight: 700; font-size: 11px;"
        )
        self._strength_lbl.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        rec_text_col.addWidget(self._strength_lbl)
        rec_row.addLayout(rec_text_col)
        rec_row.addStretch()
        layout.addLayout(rec_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C.COLOR_BORDER};")
        layout.addWidget(sep)

        # rationale
        layout.addWidget(section_title_label(C.SECTION_RATIONALE))
        self._rationale_lbl = QLabel("—")
        self._rationale_lbl.setWordWrap(True)
        self._rationale_lbl.setStyleSheet("font-size: 13px; line-height: 1.5;")
        layout.addWidget(self._rationale_lbl)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"color: {C.COLOR_BORDER};")
        layout.addWidget(sep2)

        # suggested actions
        layout.addWidget(section_title_label(C.SECTION_SUGGESTED_ACTIONS))
        self._actions_widget = QWidget()
        self._actions_layout = QVBoxLayout(self._actions_widget)
        self._actions_layout.setContentsMargins(0, 0, 0, 0)
        self._actions_layout.setSpacing(6)
        layout.addWidget(self._actions_widget)

        layout.addStretch()
        return card

    # right panel

    def _build_right_panel(self) -> QFrame:
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(section_title_label(C.SECTION_PLAN_DECISION))

        # accept button
        self._accept_btn = make_primary_button(C.BTN_ACCEPT_REC)
        self._accept_btn.setMinimumHeight(48)
        self._accept_btn.clicked.connect(self._on_accept)
        layout.addWidget(self._accept_btn)

        # override button
        self._override_btn = make_secondary_button(C.BTN_OVERRIDE_REC)
        self._override_btn.setMinimumHeight(48)
        self._override_btn.clicked.connect(self._on_override_toggle)
        layout.addWidget(self._override_btn)

        # override details (hidden by default)
        self._override_details = QWidget()
        od_layout = QVBoxLayout(self._override_details)
        od_layout.setContentsMargins(0, 0, 0, 0)
        od_layout.setSpacing(6)

        od_layout.addWidget(h_muted("If overriding, please provide a reason"))
        self._override_reason_combo = QComboBox()
        self._override_reason_combo.addItem(C.OVERRIDE_REASON_PLACEHOLDER)
        self._override_reason_combo.addItems(C.OVERRIDE_REASONS)
        od_layout.addWidget(self._override_reason_combo)
        self._override_details.setVisible(False)
        layout.addWidget(self._override_details)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C.COLOR_BORDER};")
        layout.addWidget(sep)

        # physician comments
        layout.addWidget(section_title_label(C.PHYSICIAN_COMMENT_LABEL))
        self._comments_edit = QTextEdit()
        self._comments_edit.setPlaceholderText(C.PHYSICIAN_COMMENT_PLACEHOLDER)
        self._comments_edit.setFixedHeight(130)
        layout.addWidget(self._comments_edit)

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

        self._save_btn = make_primary_button(C.BTN_SAVE_CONTINUE)
        self._save_btn.clicked.connect(self._on_save)
        layout.addWidget(self._save_btn)

        return bar

    # pipulate

    def populate(self) -> None:
        """Load recommendation based on committed Wells risk."""
        risk = self._h.current.wells_risk
        rec = C.RECOMMENDATIONS.get(risk, C.RECOMMENDATIONS["HIGH RISK"])

        self._rec_title_lbl.setText(rec["title"])
        self._strength_lbl.setText(rec["strength"])
        self._rationale_lbl.setText(rec["rationale"])

        # rebuild action checkboxes
        for cb in self._action_checks:
            cb.deleteLater()
        self._action_checks.clear()

        for action_text in rec["actions"]:
            cb = QCheckBox()
            cb.setStyleSheet("font-size: 13px;")
            lbl_action = QLabel(action_text)
            lbl_action.setWordWrap(True)
            lbl_action.setStyleSheet("font-size: 13px;")
            row_w = QWidget()
            row_l = QHBoxLayout(row_w)
            row_l.setContentsMargins(0, 0, 0, 0)
            row_l.setSpacing(6)
            row_l.addWidget(cb)
            row_l.addWidget(lbl_action, stretch=1)
            self._action_checks.append(cb)
            self._actions_layout.addWidget(row_w)

        # restore previously saved decision if revisiting
        d = self._h.current
        if d.physician_comments:
            self._comments_edit.setPlainText(d.physician_comments)
        if d.physician_decision == "Override":
            self._override_details.setVisible(True)
            idx = self._override_reason_combo.findText(d.override_reason)
            if idx >= 0:
                self._override_reason_combo.setCurrentIndex(idx)

        log_recommendation(d.mrn, rec["title"], rec["strength"])

        # log missing data
        missing = d.missing_critical_fields()
        if missing:
            log_missing_data(d.mrn, missing)

    # handlers

    def _on_accept(self) -> None:
        self._h.stage_update("physician_decision", "Accept")
        self._h.stage_update("override_reason", "")
        self._h.stage_update("recommendation_title", self._rec_title_lbl.text())
        self._h.stage_update("recommendation_strength", self._strength_lbl.text())
        self._h.stage_update("physician_comments",
                             self._comments_edit.toPlainText().strip())
        self._h.commit()
        d = self._h.current
        log_physician_decision(d.mrn, "Accept",
                               comments=d.physician_comments)
        self._accept_btn.setStyleSheet(
            f"background:{C.COLOR_LOW_RISK}; color:white; border-radius:6px; "
            "padding:8px 18px; font-weight:700;"
        )
        self._override_btn.setEnabled(False)

    def _on_override_toggle(self) -> None:
        visible = not self._override_details.isVisible()
        self._override_details.setVisible(visible)

    def _on_back(self) -> None:
        self._h.discard()
        self.go_back.emit()

    def _on_save(self) -> None:
        """Validate, commit, and signal that the assessment is complete."""
        decision = self._h.current.physician_decision
        if not decision:
            QMessageBox.warning(
                self, "Decision Required",
                "Please accept or override the recommendation before saving."
            )
            return

        if decision == "Override":
            reason_idx = self._override_reason_combo.currentIndex()
            if reason_idx == 0:  # still on placeholder
                QMessageBox.warning(
                    self, "Override Reason Required",
                    "Please select a reason for overriding the recommendation."
                )
                return
            override_reason = self._override_reason_combo.currentText()
            self._h.stage_update("override_reason", override_reason)

        self._h.stage_update("physician_comments",
                             self._comments_edit.toPlainText().strip())
        self._h.commit()

        d = self._h.current
        if decision == "Override":
            log_physician_decision(
                d.mrn, "Override",
                override_reason=d.override_reason,
                comments=d.physician_comments,
            )

        self.assessment_done.emit()
