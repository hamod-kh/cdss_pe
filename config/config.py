### app ###
APP_TITLE = "CDS PE v1.0 – Pulmonary Embolism CDSS"
APP_VERSION = "1.0"
SOURCE_LABEL = "Source: CDS PE v1.0"

### Window geometry ###
WINDOW_MIN_WIDTH = 1100
WINDOW_MIN_HEIGHT = 720

### Colour palette (hex) ###
COLOR_PRIMARY = "#0D7377"  # teal headers / active buttons
COLOR_PRIMARY_DARK = "#085C60"
COLOR_ACCENT = "#14BDAC"
COLOR_HIGH_RISK = "#C0392B"
COLOR_MODERATE = "#E67E22"
COLOR_LOW_RISK = "#27AE60"
COLOR_WARNING_BG = "#FFF3CD"
COLOR_WARNING_BORDER = "#FFC107"
COLOR_HINT_BG = "#EAF6FB"
COLOR_MISSING_BG = "#FFF8E1"
COLOR_PANEL_BG = "#F8F9FA"
COLOR_BORDER = "#DEE2E6"
COLOR_TEXT_MUTED = "#6C757D"
COLOR_WHITE = "#FFFFFF"
COLOR_LIGHT_TEAL = "#E8F4F5"

### Step titles ###
STEP_TITLES = {
    0: "Patient Selection",
    1: "Patient Overview & Data Entry",
    2: "Wells Score & PE Risk",
    3: "Recommendations",
}

# ### Step-indicator labels ###
STEP_LABELS = ["Patient", "Data Entry", "Wells Score", "Recommendations"]

### navigation buttons ###
BTN_BACK = "← Back"
BTN_NEXT = "Next →"
BTN_PROCEED = "Proceed to Recommendations →"
BTN_SAVE_CONTINUE = "Save & Continue to Orders →"
BTN_ACCEPT_REC = "✓  Accept Recommendation"
BTN_OVERRIDE_REC = "↺  Override / Choose Alternative"
BTN_NEW_PATIENT = "+ New Patient"
BTN_LOAD_PATIENT = "Load Selected Patient"
BTN_CONFIRM_PATIENT = "Confirm & Start Assessment"

### page 0 - patient selection ###
PATIENT_SELECT_TITLE = "Select or Register a Patient"
PATIENT_SELECT_INSTRUCTIONS = (
    "Select an existing patient from the list below, or register a new patient "
    "to begin a PE assessment."
)
PATIENT_TABLE_HEADERS = ["MRN", "Name", "Age", "Sex", "Last Assessment", "PE Risk"]
PATIENT_SEARCH_PLACEHOLDER = "Search by name or MRN…"
NO_PATIENTS_MSG = "No patients found in the database."

### page 1 data entry ###
SECTION_VITAL_SIGNS = "VITAL SIGNS"
SECTION_LABS_IMAGING = "LABS / IMAGING"
SECTION_SYMPTOMS = "SYMPTOMS & RISK FACTORS"
SECTION_MISSING_DATA = "MISSING / INCOMPLETE DATA"
SECTION_PE_HINTS = "PE PATTERN HINTS"

VITAL_LAST_UPDATED = "Last updated:"
LAB_ADD_RESULT = "+ Add result"
MISSING_REVIEW_LINK = "Review and complete"

VITAL_FIELDS = [
    ("hr", "HR", "bpm"),
    ("bp", "BP", "mmHg"),
    ("rr", "RR", "/min"),
    ("spo2", "SpO₂", "%"),
    ("temp", "Temp", "°C"),
]

LAB_FIELDS = [
    ("ddimer", "D-dimer", "ng/mL"),
    ("troponin", "Troponin", "ng/L"),
    ("bnp", "BNP", "pg/mL"),
    ("creatinine", "Creatinine", "µmol/L"),
]

SYMPTOM_FIELDS = [
    ("dyspnea", "Dyspnea"),
    ("pleuritic_pain", "Pleuritic chest pain"),
    ("hemoptysis", "Hemoptysis"),
    ("leg_swelling", "Leg swelling"),
    ("recent_surgery", "Recent surgery / immobilization (≤ 4 wks)"),
    ("prior_dvt_pe", "Prior DVT / PE"),
    ("hormone_therapy", "Hormone therapy / Pregnancy"),
    ("malignancy", "Malignancy (active)"),
]

TRIAGE_OPTIONS = [
    "CTAS 1 – Resuscitation",
    "CTAS 2 – Emergent",
    "CTAS 3 – Urgent",
    "CTAS 4 – Less Urgent",
    "CTAS 5 – Non-Urgent",
]
SEX_OPTIONS = ["Female", "Male", "Other / Not specified"]

BTN_YES = "Yes"
BTN_NO = "No"
BTN_UNKNOWN = "Unknown"

PE_RISK_LABEL = "PE Risk"
PATTERN_SUFFIX = "\nPattern suggests: "

### page 2 wells score ###
WELLS_TITLE = "WELLS CRITERIA"
WELLS_COL_NO = "NO"
WELLS_COL_YES = "YES"
WELLS_COL_UNKNOWN = "UNKNOWN"

WELLS_CRITERIA = [
    ("dvt_signs", "Clinical signs and symptoms of DVT", 3.0),
    ("pe_likely", "PE is #1 diagnosis OR equally likely", 3.0),
    ("hr_over_100", "Heart rate > 100 bpm", 1.5),
    ("immobilization", "Immobilization or surgery in previous 4 weeks", 1.5),
    ("prev_dvt_pe", "Previous DVT / PE", 1.5),
    ("hemoptysis_w", "Hemoptysis", 1.0),
    ("malignancy_w", "Malignancy (active)", 1.0),
]

WELLS_SCORE_LABEL = "WELLS SCORE"
WELLS_RISK_LABEL = "Risk level"
WELLS_SCORE_BREAKDOWN = "SCORE BREAKDOWN"
WELLS_CRITERIA_TOTAL = "Criteria total"
WELLS_ADJUSTMENT = "Adjustment"
WELLS_SCORE_TOTAL = "Wells score"
WELLS_DATA_COMPLETENESS = "DATA COMPLETENESS"
WELLS_COMPLETE_LABEL = "Complete"
WELLS_ELEMENTS_LABEL = "data elements completed"
WELLS_VIEW_MISSING = "View missing data"
WELLS_SCALE_NOTE = (
    "Total possible score: 0–12.5\n"
    "Risk categories:  Low ≤ 4   |   Moderate 4.5–6   |   High > 6"
)

RISK_LOW = "LOW RISK"
RISK_MODERATE = "MODERATE RISK"
RISK_HIGH = "HIGH RISK"

RISK_THRESHOLDS = {
    "low": (None, 4.0),
    "moderate": (4.5, 6.0),
    "high": (6.0, None),
}

### page 3 recommendation ###
SECTION_RECOMMENDED_STEP = "RECOMMENDED NEXT STEP"
SECTION_RATIONALE = "RATIONALE"
SECTION_SUGGESTED_ACTIONS = "SUGGESTED ACTIONS"
SECTION_PLAN_DECISION = "PLAN DECISION"

LABEL_STRONG_REC = "STRONG RECOMMENDATION"
LABEL_MODERATE_REC = "MODERATE RECOMMENDATION"

OVERRIDE_REASON_PLACEHOLDER = "Select reason (required)"
OVERRIDE_REASONS = [
    "Patient contraindication",
    "Already ordered / in progress",
    "Clinical judgment – alternative pathway",
    "Resource unavailable",
    "Other (see comments)",
]
OVERRIDE_COMMENTS_PLACEHOLDER = "Additional comments (optional)"

PHYSICIAN_COMMENT_LABEL = "Physician Notes / Clinical Context"
PHYSICIAN_COMMENT_PLACEHOLDER = (
    "Enter any additional clinical notes, override justification, "
    "or context for this assessment…"
)

### recommendation logic keyed on risk level ###
RECOMMENDATIONS = {
    "HIGH RISK": {
        "title": "Order D-dimer (quantitative)",
        "strength": LABEL_STRONG_REC,
        "rationale": (
            "Patient is at high pre-test probability for PE (Wells score ≥ 6). "
            "D-dimer testing is recommended to guide further imaging decisions. "
            "If D-dimer is positive or not available, proceed to CT Pulmonary "
            "Angiography (CTPA)."
        ),
        "actions": [
            "Order D-dimer (quantitative)",
            "If D-dimer positive (≥ age-adjusted cutoff) or not available → Order CTPA",
            "If CTPA positive → Start anticoagulation per protocol",
            "Consider bilateral lower limb ultrasound if CTPA contraindicated",
            "Reassess hemodynamics and oxygenation",
        ],
    },
    "MODERATE RISK": {
        "title": "Order D-dimer (quantitative)",
        "strength": LABEL_MODERATE_REC,
        "rationale": (
            "Patient is at moderate pre-test probability for PE (Wells score 4.5–6). "
            "D-dimer testing should be performed. If D-dimer is negative (below "
            "age-adjusted cutoff), PE can be excluded. If positive, proceed to CTPA."
        ),
        "actions": [
            "Order D-dimer (quantitative)",
            "If D-dimer negative (< age-adjusted cutoff) → PE excluded; no imaging needed",
            "If D-dimer positive → Order CTPA",
            "If CTPA positive → Start anticoagulation per protocol",
            "Document clinical reasoning for probability assessment",
        ],
    },
    "LOW RISK": {
        "title": "Order D-dimer (PERC rule or quantitative)",
        "strength": LABEL_MODERATE_REC,
        "rationale": (
            "Patient is at low pre-test probability for PE (Wells score ≤ 4). "
            "Consider applying the PERC rule. If PERC negative, PE can be excluded "
            "without further testing. If PERC positive or not applicable, order "
            "D-dimer; proceed to CTPA only if D-dimer is elevated."
        ),
        "actions": [
            "Apply PERC rule (if all 8 criteria negative → discharge, no further workup)",
            "If PERC positive → Order D-dimer (quantitative)",
            "If D-dimer negative → PE excluded",
            "If D-dimer positive → Order CTPA",
            "Consider alternative diagnoses for symptoms",
        ],
    },
}

### Logger ###
LOG_FILE_NAME = "cdss_pe.log"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = "INFO"

### Database ###
DB_FILE_NAME = "cdss_pe.db"

### Missing-data hints ###
PE_PATTERN_HINTS_RULES = [
    # (condition_fn, hint_text)
    # condition_fn receives the current PatientData dict
    ("hr_tachycardia", "Tachycardia + Tachypnea"),
    ("spo2_low", "Hypoxemia (SpO₂ < 95%)"),
    ("pleuritic_pain", "Pleuritic chest pain present"),
    ("hemoptysis_yes", "Hemoptysis reported"),
    ("leg_swelling_yes", "Unilateral leg swelling"),
]
