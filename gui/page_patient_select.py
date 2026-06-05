from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QAbstractItemView, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

import config.config as C
from gui.widgets import (
    make_card, make_primary_button, make_secondary_button,
    section_title_label, h_bold, h_muted, APP_STYLESHEET
)
from data.data_model import PatientData
from data.db import DatabaseHandler


class PatientSelectPage(QWidget):
    """
    Presents two panels:
      • Left  – search + table of existing patients (load)
      • Right – form to register a brand-new patient
    Emits ``patient_ready(PatientData)`` when the user has made a choice.
    """

    patient_ready = pyqtSignal(object)  # PatientData

    def __init__(self, db: DatabaseHandler, parent=None) -> None:
        super().__init__(parent)
        self._db = db
        self._selected_mrn: str | None = None
        self._build_ui()

    # build ui
    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        root.addWidget(self._build_left_panel(), stretch=3)
        root.addWidget(self._build_right_panel(), stretch=2)

    # left panel: existing patients
    def _build_left_panel(self) -> QFrame:
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(section_title_label("REGISTERED PATIENTS"))

        # search
        search_row = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(C.PATIENT_SEARCH_PLACEHOLDER)
        self._search_input.textChanged.connect(self._filter_table)
        search_row.addWidget(self._search_input)
        layout.addLayout(search_row)

        # table
        self._table = QTableWidget()
        self._table.setColumnCount(len(C.PATIENT_TABLE_HEADERS))
        self._table.setHorizontalHeaderLabels(C.PATIENT_TABLE_HEADERS)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.itemSelectionChanged.connect(self._on_row_selected)
        self._table.doubleClicked.connect(self._on_load_patient)
        layout.addWidget(self._table)

        # load + history buttons
        btn_row = QHBoxLayout()

        self._load_btn = make_primary_button(C.BTN_LOAD_PATIENT)
        self._load_btn.setEnabled(False)
        self._load_btn.clicked.connect(self._on_load_patient)
        btn_row.addWidget(self._load_btn)

        self._history_btn = make_secondary_button("View Patient History")
        self._history_btn.setEnabled(False)
        self._history_btn.clicked.connect(self._on_view_history)
        btn_row.addWidget(self._history_btn)

        layout.addLayout(btn_row)

        hint = h_muted("Double-click a row to load a patient, or use the buttons above.")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        return card

    # right panel: new patients
    def _build_right_panel(self) -> QFrame:
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(section_title_label("REGISTER NEW PATIENT"))

        def row(label_text: str, widget: QWidget) -> None:
            lbl = QLabel(label_text)
            lbl.setFixedWidth(110)
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            r = QHBoxLayout()
            r.addWidget(lbl)
            r.addWidget(widget)
            layout.addLayout(r)

        self._mrn_input = QLineEdit()
        self._mrn_input.setPlaceholderText("e.g. 12345678")
        row("MRN *", self._mrn_input)

        self._fn_input = QLineEdit()
        self._fn_input.setPlaceholderText("First name")
        row("First Name *", self._fn_input)

        self._ln_input = QLineEdit()
        self._ln_input.setPlaceholderText("Last name")
        row("Last Name *", self._ln_input)

        from PyQt6.QtWidgets import QSpinBox, QComboBox
        self._age_input = QSpinBox()
        self._age_input.setRange(0, 130)
        self._age_input.setSuffix(" y")
        row("Age", self._age_input)

        self._sex_combo = QComboBox()
        self._sex_combo.addItems(C.SEX_OPTIONS)
        row("Sex", self._sex_combo)

        self._triage_combo = QComboBox()
        self._triage_combo.addItems(C.TRIAGE_OPTIONS)
        row("Triage", self._triage_combo)

        layout.addStretch()

        self._register_btn = make_primary_button(C.BTN_CONFIRM_PATIENT)
        self._register_btn.clicked.connect(self._on_register_new)
        layout.addWidget(self._register_btn)

        req_note = h_muted("* Required fields")
        layout.addWidget(req_note)

        return card

    # data loading

    def refresh(self) -> None:
        """(Re)populate the table from the database."""
        self._all_patients = self._db.list_patients()
        self._populate_table(self._all_patients)

    def _populate_table(self, patients: list[dict]) -> None:
        self._table.setRowCount(0)
        for row_data in patients:
            r = self._table.rowCount()
            self._table.insertRow(r)
            values = [
                row_data.get("mrn", ""),
                row_data.get("full_name", "").strip() or "—",
                row_data.get("age", ""),
                row_data.get("sex", ""),
                row_data.get("last_assessment", ""),
                row_data.get("wells_risk", ""),
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # colour-code risk column
                if col == 5:
                    if "HIGH" in val:
                        item.setForeground(
                            __import__("PyQt6.QtGui", fromlist=["QColor"]).QColor(C.COLOR_HIGH_RISK)
                        )
                    elif "MODERATE" in val:
                        item.setForeground(
                            __import__("PyQt6.QtGui", fromlist=["QColor"]).QColor(C.COLOR_MODERATE)
                        )
                    elif "LOW" in val:
                        item.setForeground(
                            __import__("PyQt6.QtGui", fromlist=["QColor"]).QColor(C.COLOR_LOW_RISK)
                        )
                self._table.setItem(r, col, item)

    def _filter_table(self, text: str) -> None:
        q = text.lower()
        filtered = [
            p for p in self._all_patients
            if q in p.get("mrn", "").lower() or q in p.get("full_name", "").lower()
        ]
        self._populate_table(filtered)

    # ------------ handlers ------------
    def _on_row_selected(self) -> None:
        rows = self._table.selectedItems()
        has_selection = bool(rows)
        self._load_btn.setEnabled(has_selection)
        self._history_btn.setEnabled(has_selection)
        if rows:
            self._selected_mrn = self._table.item(self._table.currentRow(), 0).text()

    def _on_load_patient(self) -> None:
        if not self._selected_mrn:
            return
        patient = self._db.load_patient(self._selected_mrn)
        if patient:
            self.patient_ready.emit(patient)
        else:
            QMessageBox.warning(
                self, "Not Found",
                f"Could not load patient MRN {self._selected_mrn}."
            )

    def _on_register_new(self) -> None:
        mrn = self._mrn_input.text().strip()
        fname = self._fn_input.text().strip()
        lname = self._ln_input.text().strip()

        if not mrn:
            self._show_error("MRN is required.")
            return
        if not fname or not lname:
            self._show_error("First and last name are required.")
            return
        if self._db.patient_exists(mrn):
            reply = QMessageBox.question(
                self, "Patient Exists",
                f"MRN {mrn} is already registered.\n"
                "Load the existing record instead?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                patient = self._db.load_patient(mrn)
                if patient:
                    self.patient_ready.emit(patient)
            return

        patient = PatientData(
            mrn=mrn,
            first_name=fname,
            last_name=lname,
            age=str(self._age_input.value()),
            sex=self._sex_combo.currentText(),
            triage=self._triage_combo.currentText(),
        )
        self.patient_ready.emit(patient)

    def _on_view_history(self) -> None:
        if not self._selected_mrn:
            return
        patient_name = "—"
        for p in self._all_patients:
            if p.get("mrn") == self._selected_mrn:
                patient_name = p.get("full_name", "—").strip()
                break
        from gui.patient_history_dialog import PatientHistoryDialog
        dlg = PatientHistoryDialog(
            mrn=self._selected_mrn,
            patient_name=patient_name,
            db=self._db,
            parent=self,
        )
        dlg.exec()

    def _show_error(self, msg: str) -> None:
        QMessageBox.critical(self, "Input Error", msg)
