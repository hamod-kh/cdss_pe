
# main_window.py  –  Main application window
#
# Orchestrates the multi-page flow:
#   0. PatientSelectPage
#   1. DataEntryPage
#   2. WellsScorePage
#   3. RecommendationsPage
#
# Owns the InputHandler and DatabaseHandler singletons.
# Handles all inter-page navigation and final save.

from __future__ import annotations
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QStackedWidget, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QIcon

import config.config as C
from gui.widgets import (
    APP_STYLESHEET, StepIndicator, h_bold, h_muted,
    make_primary_button, make_secondary_button, section_title_label
)
from data.data_model import InputHandler, PatientData
from data.db import DatabaseHandler
from logger.logger import (
    log_session_start, log_navigation, log_db_event, log_error
)

from gui.page_patient_select import PatientSelectPage
from gui.page_data_entry import DataEntryPage
from gui.page_wells_score import WellsScorePage
from gui.page_recommendations import RecommendationsPage


class MainWindow(QMainWindow):
    """
    Top-level window.  Manages a QStackedWidget with four pages.
    Page indices mirror the STEP_* constants in config.
    """

    # page indices
    PAGE_SELECT = 0
    PAGE_DATA = 1
    PAGE_WELLS = 2
    PAGE_REC = 3

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(C.APP_TITLE)
        self.setMinimumSize(C.WINDOW_MIN_WIDTH, C.WINDOW_MIN_HEIGHT)
        self.setStyleSheet(APP_STYLESHEET)

        # ── Singletons ────────────────────────────────────────────────────────
        self._db = DatabaseHandler()
        self._handler = InputHandler()

        # ── Build central widget ──────────────────────────────────────────────
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_app_header())
        root.addWidget(self._build_step_indicator_bar())
        root.addWidget(self._build_page_title_bar())

        self._stack = QStackedWidget()
        root.addWidget(self._stack, stretch=1)

        # ── Create pages ──────────────────────────────────────────────────────
        self._select_page = PatientSelectPage(self._db)
        self._data_page = DataEntryPage(self._handler)
        self._wells_page = WellsScorePage(self._handler)
        self._rec_page = RecommendationsPage(self._handler)

        self._stack.addWidget(self._select_page)  # index 0
        self._stack.addWidget(self._data_page)  # index 1
        self._stack.addWidget(self._wells_page)  # index 2
        self._stack.addWidget(self._rec_page)  # index 3

        # ── Wire signals ──────────────────────────────────────────────────────
        self._select_page.patient_ready.connect(self._on_patient_selected)

        self._data_page.go_next.connect(lambda: self._navigate_to(self.PAGE_WELLS))
        self._data_page.go_back.connect(lambda: self._navigate_to(self.PAGE_SELECT))

        self._wells_page.go_next.connect(lambda: self._navigate_to(self.PAGE_REC))
        self._wells_page.go_back.connect(lambda: self._navigate_to(self.PAGE_DATA))

        self._rec_page.go_back.connect(lambda: self._navigate_to(self.PAGE_WELLS))
        self._rec_page.assessment_done.connect(self._on_assessment_done)

        # ── Start on selection page ───────────────────────────────────────────
        self._navigate_to(self.PAGE_SELECT, initial=True)

    # ── Header bars ───────────────────────────────────────────────────────────

    def _build_app_header(self) -> QFrame:
        bar = QFrame()
        bar.setStyleSheet(
            f"background: {C.COLOR_PRIMARY}; border-radius: 0px;"
        )
        bar.setFixedHeight(52)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel(C.APP_TITLE)
        title.setStyleSheet(
            "color: white; font-size: 16px; font-weight: 700; background: transparent;"
        )
        layout.addWidget(title)
        layout.addStretch()

        version = QLabel(f"v{C.APP_VERSION}")
        version.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px; background: transparent;")
        layout.addWidget(version)

        return bar

    def _build_step_indicator_bar(self) -> QFrame:
        bar = QFrame()
        bar.setStyleSheet(
            f"background: {C.COLOR_PANEL_BG}; border-bottom: 1px solid {C.COLOR_BORDER};"
        )
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)

        self._step_indicator = StepIndicator(C.STEP_LABELS)
        layout.addWidget(self._step_indicator)

        return bar

    def _build_page_title_bar(self) -> QFrame:
        bar = QFrame()
        bar.setStyleSheet(
            f"background: white; border-bottom: 2px solid {C.COLOR_BORDER};"
        )
        bar.setFixedHeight(48)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)

        self._page_title_lbl = QLabel("—")
        f = QFont()
        f.setBold(True)
        f.setPointSize(13)
        self._page_title_lbl.setFont(f)
        layout.addWidget(self._page_title_lbl)
        layout.addStretch()

        self._patient_context_lbl = QLabel("")
        self._patient_context_lbl.setStyleSheet(
            f"color: {C.COLOR_TEXT_MUTED}; font-size: 12px;"
        )
        layout.addWidget(self._patient_context_lbl)

        return bar

    # ── Navigation ────────────────────────────────────────────────────────────

    def _navigate_to(self, page_idx: int, initial: bool = False) -> None:
        current_idx = self._stack.currentIndex()
        direction = "forward" if page_idx > current_idx else "back"

        if not initial:
            log_navigation(current_idx, page_idx, direction)

        # Refresh target page before showing it
        if page_idx == self.PAGE_SELECT:
            self._select_page.refresh()
            self._step_indicator.set_step(0)

        elif page_idx == self.PAGE_DATA:
            self._data_page.populate()
            self._step_indicator.set_step(1)

        elif page_idx == self.PAGE_WELLS:
            self._wells_page.populate()
            self._step_indicator.set_step(2)

        elif page_idx == self.PAGE_REC:
            self._rec_page.populate()
            self._step_indicator.set_step(3)

        self._stack.setCurrentIndex(page_idx)
        self._update_title_bar(page_idx)

    def _update_title_bar(self, page_idx: int) -> None:
        titles = {
            self.PAGE_SELECT: C.STEP_TITLES[0],
            self.PAGE_DATA: C.STEP_TITLES[1],
            self.PAGE_WELLS: C.STEP_TITLES[2],
            self.PAGE_REC: C.STEP_TITLES[3],
        }
        self._page_title_lbl.setText(
            f"{page_idx}  {titles.get(page_idx, '—')}"
        )

        d = self._handler.current
        if d.mrn:
            self._patient_context_lbl.setText(
                f"Patient: {d.full_name}  |  MRN: {d.mrn}"
            )
        else:
            self._patient_context_lbl.setText("")

    # ── Slots ─────────────────────────────────────────────────────────────────

    @pyqtSlot(object)
    def _on_patient_selected(self, patient: PatientData) -> None:
        """Called when the selection page emits a patient (new or existing)."""
        self._handler.load(patient)
        log_session_start(patient.mrn, patient.full_name)
        self._navigate_to(self.PAGE_DATA)

    @pyqtSlot()
    def _on_assessment_done(self) -> None:
        """Persist the completed assessment and return to the selection page."""
        d = self._handler.current

        # Stamp the assessment timestamp if not yet set
        if not d.assessment_timestamp:
            self._handler.stage_update(
                "assessment_timestamp",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            self._handler.commit()
            d = self._handler.current

        success = self._db.save_assessment(d)

        if success:
            log_db_event("ASSESSMENT_SAVED", f"MRN={d.mrn}")
            QMessageBox.information(
                self, "Assessment Saved",
                f"Assessment for {d.full_name} (MRN {d.mrn}) has been saved.\n"
                f"Wells Score: {d.wells_score}  |  Risk: {d.wells_risk}\n"
                f"Recommendation: {d.recommendation_title}"
            )
        else:
            QMessageBox.critical(
                self, "Save Failed",
                "The assessment could not be saved. Please check the log for details."
            )

        # Reset and return to patient selection
        self._handler.load(PatientData())
        self._navigate_to(self.PAGE_SELECT)
