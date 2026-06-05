# db_handler.py
#
# Responsibilities:
# - Create / migrate the database on first run
# - Save a completed assessment (upsert by MRN + timestamp)
# - Load all patients for the selection list
#  - Load a specific patient's most recent (or a specific) assessment

from __future__ import annotations
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional

from data.data_model import PatientData
from logger.logger import log_db_event, log_error
from config.config import DB_FILE_NAME


# database üath
DB_PATH = os.path.join(os.path.dirname(__file__), DB_FILE_NAME)


# sql schema
_DDL = """
CREATE TABLE IF NOT EXISTS patients (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    mrn                  TEXT    NOT NULL,
    first_name           TEXT    DEFAULT '',
    last_name            TEXT    DEFAULT '',
    age                  TEXT    DEFAULT '',
    sex                  TEXT    DEFAULT '',
    triage               TEXT    DEFAULT '',
    wells_score          REAL    DEFAULT 0.0,
    wells_risk           TEXT    DEFAULT '',
    recommendation_title TEXT    DEFAULT '',
    physician_decision   TEXT    DEFAULT '',
    override_reason      TEXT    DEFAULT '',
    physician_comments   TEXT    DEFAULT '',
    assessment_timestamp TEXT    NOT NULL,
    last_updated         TEXT    NOT NULL,
    full_data_json       TEXT    NOT NULL,
    UNIQUE(mrn, assessment_timestamp)
);

CREATE INDEX IF NOT EXISTS idx_patients_mrn ON patients(mrn);
"""


# class for handling the database

class DatabaseHandler:
    """Thread-safe-ish SQLite wrapper (single-writer, multiple reads)."""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self._init_db()


    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self) -> None:
        try:
            with self._connect() as conn:
                conn.executescript(_DDL)
            log_db_event("INIT", f"Database ready at {self.db_path}")
        except Exception as exc:
            log_error("DatabaseHandler._init_db", exc)
            raise

    def save_assessment(self, patient: PatientData) -> bool:
        """
        Insert or replace a patient assessment.
        Uses (mrn, assessment_timestamp) as the natural key.
        Returns True on success.
        """
        if not patient.mrn:
            log_error("save_assessment", ValueError("MRN is empty – cannot save"))
            return False

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not patient.assessment_timestamp:
            patient.assessment_timestamp = now
        patient.last_updated = now

        full_json = json.dumps(patient.to_dict(), ensure_ascii=False)

        sql = """
        INSERT INTO patients
            (mrn, first_name, last_name, age, sex, triage,
             wells_score, wells_risk, recommendation_title,
             physician_decision, override_reason, physician_comments,
             assessment_timestamp, last_updated, full_data_json)
        VALUES
            (:mrn, :first_name, :last_name, :age, :sex, :triage,
             :wells_score, :wells_risk, :recommendation_title,
             :physician_decision, :override_reason, :physician_comments,
             :assessment_timestamp, :last_updated, :full_data_json)
        ON CONFLICT(mrn, assessment_timestamp) DO UPDATE SET
            first_name           = excluded.first_name,
            last_name            = excluded.last_name,
            age                  = excluded.age,
            sex                  = excluded.sex,
            triage               = excluded.triage,
            wells_score          = excluded.wells_score,
            wells_risk           = excluded.wells_risk,
            recommendation_title = excluded.recommendation_title,
            physician_decision   = excluded.physician_decision,
            override_reason      = excluded.override_reason,
            physician_comments   = excluded.physician_comments,
            last_updated         = excluded.last_updated,
            full_data_json       = excluded.full_data_json
        """
        try:
            with self._connect() as conn:
                conn.execute(sql, {
                    "mrn":                  patient.mrn,
                    "first_name":           patient.first_name,
                    "last_name":            patient.last_name,
                    "age":                  patient.age,
                    "sex":                  patient.sex,
                    "triage":               patient.triage,
                    "wells_score":          patient.wells_score,
                    "wells_risk":           patient.wells_risk,
                    "recommendation_title": patient.recommendation_title,
                    "physician_decision":   patient.physician_decision,
                    "override_reason":      patient.override_reason,
                    "physician_comments":   patient.physician_comments,
                    "assessment_timestamp": patient.assessment_timestamp,
                    "last_updated":         patient.last_updated,
                    "full_data_json":       full_json,
                })
            log_db_event("SAVE", f"MRN={patient.mrn} | Risk={patient.wells_risk}")
            return True
        except Exception as exc:
            log_error("save_assessment", exc)
            return False

    def list_patients(self) -> list[dict]:
        """
        Return one summary row per MRN (most recent assessment).
        Keys: mrn, full_name, age, sex, last_assessment, wells_risk
        """
        sql = """
        SELECT
            mrn,
            first_name || ' ' || last_name AS full_name,
            age,
            sex,
            MAX(assessment_timestamp) AS last_assessment,
            wells_risk
        FROM patients
        GROUP BY mrn
        ORDER BY last_assessment DESC
        """
        try:
            with self._connect() as conn:
                rows = conn.execute(sql).fetchall()
            return [dict(r) for r in rows]
        except Exception as exc:
            log_error("list_patients", exc)
            return []

    def load_patient(self, mrn: str, timestamp: Optional[str] = None) -> Optional[PatientData]:
        """
        Load the most recent (or a specific) assessment for an MRN.
        Returns a PatientData or None.
        """
        if timestamp:
            sql = """
            SELECT full_data_json FROM patients
            WHERE mrn = ? AND assessment_timestamp = ?
            ORDER BY last_updated DESC LIMIT 1
            """
            params = (mrn, timestamp)
        else:
            sql = """
            SELECT full_data_json FROM patients
            WHERE mrn = ?
            ORDER BY assessment_timestamp DESC LIMIT 1
            """
            params = (mrn,)

        try:
            with self._connect() as conn:
                row = conn.execute(sql, params).fetchone()
            if row:
                data = json.loads(row["full_data_json"])
                log_db_event("LOAD", f"MRN={mrn}")
                return PatientData.from_dict(data)
            log_db_event("LOAD_MISS", f"MRN={mrn} not found")
            return None
        except Exception as exc:
            log_error("load_patient", exc)
            return None

    def patient_exists(self, mrn: str) -> bool:
        sql = "SELECT 1 FROM patients WHERE mrn = ? LIMIT 1"
        try:
            with self._connect() as conn:
                row = conn.execute(sql, (mrn,)).fetchone()
            return row is not None
        except Exception as exc:
            log_error("patient_exists", exc)
            return False

    def assessment_history(self, mrn: str) -> list[dict]:
        """All assessments for one MRN, newest first."""
        sql = """
        SELECT assessment_timestamp, wells_score, wells_risk,
               recommendation_title, physician_decision
        FROM patients
        WHERE mrn = ?
        ORDER BY assessment_timestamp DESC
        """
        try:
            with self._connect() as conn:
                rows = conn.execute(sql, (mrn,)).fetchall()
            return [dict(r) for r in rows]
        except Exception as exc:
            log_error("assessment_history", exc)
            return []
