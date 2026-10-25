"""
TalentBridge AI - Student Performance Prediction Configuration
Defines feature schemas, threshold boundaries, grade mapping, and sample student profiles.
"""

from pathlib import Path
from typing import Dict, List, Any

MODULE_DIR = Path(__file__).resolve().parent
DATA_DIR = MODULE_DIR / "data"
ARTIFACTS_DIR = MODULE_DIR / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "student_performance_model.joblib"
DATASET_PATH = DATA_DIR / "student_academic_records.csv"

# Input Feature Definitions
NUMERICAL_FEATURES: List[str] = [
    "gpa_sem1",
    "gpa_sem2",
    "gpa_sem3",
    "midterm_score",
    "attendance_rate",
    "lms_hours_per_week",
    "lms_logins_per_week",
    "assignment_punctuality_rate",
    "extracurricular_index",
    "study_hours_per_week",
]

FEATURE_LABELS: Dict[str, str] = {
    "gpa_sem1": "Semester 1 GPA (0.0 - 4.0)",
    "gpa_sem2": "Semester 2 GPA (0.0 - 4.0)",
    "gpa_sem3": "Semester 3 GPA (0.0 - 4.0)",
    "midterm_score": "Midterm Core Exam Score (0 - 100%)",
    "attendance_rate": "Lecture Attendance Rate (0 - 100%)",
    "lms_hours_per_week": "LMS Portal Engagement (Hours/Week)",
    "lms_logins_per_week": "LMS Weekly Logins Count",
    "assignment_punctuality_rate": "Assignment On-Time Punctuality (%)",
    "extracurricular_index": "Extracurricular Participation Index (0.0 - 10.0)",
    "study_hours_per_week": "Independent Study (Hours/Week)",
}

# Feature Defaults & Ranges
FEATURE_BOUNDS: Dict[str, Dict[str, float]] = {
    "gpa_sem1": {"min": 1.0, "max": 4.0, "default": 3.2, "step": 0.05},
    "gpa_sem2": {"min": 1.0, "max": 4.0, "default": 3.3, "step": 0.05},
    "gpa_sem3": {"min": 1.0, "max": 4.0, "default": 3.4, "step": 0.05},
    "midterm_score": {"min": 20.0, "max": 100.0, "default": 78.0, "step": 1.0},
    "attendance_rate": {"min": 30.0, "max": 100.0, "default": 85.0, "step": 1.0},
    "lms_hours_per_week": {"min": 0.0, "max": 35.0, "default": 8.5, "step": 0.5},
    "lms_logins_per_week": {"min": 1.0, "max": 40.0, "default": 12.0, "step": 1.0},
    "assignment_punctuality_rate": {"min": 20.0, "max": 100.0, "default": 90.0, "step": 1.0},
    "extracurricular_index": {"min": 0.0, "max": 10.0, "default": 6.5, "step": 0.5},
    "study_hours_per_week": {"min": 2.0, "max": 45.0, "default": 14.0, "step": 1.0},
}

# Academic Standing & Grade Band Classifications
GRADE_BANDS = [
    {"min_gpa": 3.70, "band": "First Class with Distinction (A / 4.0 Scale)", "color": "#10b981", "badge": "High Distinction"},
    {"min_gpa": 3.30, "band": "First Class / Dean's Honors (B+ to A-)", "color": "#3b82f6", "badge": "Honors"},
    {"min_gpa": 2.70, "band": "Second Class Upper (B / B-)", "color": "#6366f1", "badge": "Good Standing"},
    {"min_gpa": 2.00, "band": "Pass / Academic Warning Zone (C / C-)", "color": "#f59e0b", "badge": "Academic Warning"},
    {"min_gpa": 0.00, "band": "Probation / Critical Graduation Risk (F / D)", "color": "#ef4444", "badge": "Probation Risk"},
]

# Risk Thresholds
RISK_LEVEL_THRESHOLDS = {
    "on_track_gpa": 3.0,
    "moderate_risk_gpa": 2.3,
    "attendance_critical": 65.0,
    "punctuality_critical": 60.0,
}

# Sample Student Profiles for Quick Demonstration & User Exploration
SAMPLE_STUDENTS: Dict[str, Dict[str, Any]] = {
    "High-Achieving Honors Scholar": {
        "description": "Consistently strong academic track record, active in tech clubs and research, stellar attendance.",
        "features": {
            "gpa_sem1": 3.85,
            "gpa_sem2": 3.90,
            "gpa_sem3": 3.92,
            "midterm_score": 94.0,
            "attendance_rate": 96.0,
            "lms_hours_per_week": 16.5,
            "lms_logins_per_week": 22.0,
            "assignment_punctuality_rate": 98.0,
            "extracurricular_index": 8.5,
            "study_hours_per_week": 24.0,
        },
    },
    "Steady Growth Student (On-Track)": {
        "description": "Gradually improving semester trajectory, reliable submission schedule, balanced extracurriculars.",
        "features": {
            "gpa_sem1": 2.95,
            "gpa_sem2": 3.15,
            "gpa_sem3": 3.35,
            "midterm_score": 82.0,
            "attendance_rate": 88.0,
            "lms_hours_per_week": 10.0,
            "lms_logins_per_week": 14.0,
            "assignment_punctuality_rate": 92.0,
            "extracurricular_index": 6.0,
            "study_hours_per_week": 15.0,
        },
    },
    "Disengaged / Moderate Risk Student": {
        "description": "Decent baseline exam performance, but declining attendance, infrequent LMS access, and late homework.",
        "features": {
            "gpa_sem1": 3.10,
            "gpa_sem2": 2.80,
            "gpa_sem3": 2.50,
            "midterm_score": 68.0,
            "attendance_rate": 68.0,
            "lms_hours_per_week": 4.0,
            "lms_logins_per_week": 6.0,
            "assignment_punctuality_rate": 65.0,
            "extracurricular_index": 3.0,
            "study_hours_per_week": 7.0,
        },
    },
    "Critical Intervention Required (At-Risk)": {
        "description": "Severely low attendance (<60%), failing midterms, missing assignments, high risk of course retention failure.",
        "features": {
            "gpa_sem1": 2.40,
            "gpa_sem2": 2.10,
            "gpa_sem3": 1.85,
            "midterm_score": 44.0,
            "attendance_rate": 52.0,
            "lms_hours_per_week": 2.0,
            "lms_logins_per_week": 3.0,
            "assignment_punctuality_rate": 45.0,
            "extracurricular_index": 1.5,
            "study_hours_per_week": 4.0,
        },
    },
}
