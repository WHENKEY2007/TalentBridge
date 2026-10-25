"""
TalentBridge AI - Student Performance Prediction Module Tests
Validates feature definitions, data generator, model training, prediction accuracy,
and interface contract compliance.
"""

from pathlib import Path
import pytest
import numpy as np

from modules.student_performance.config import (
    FEATURE_BOUNDS,
    FEATURE_LABELS,
    GRADE_BANDS,
    NUMERICAL_FEATURES,
    SAMPLE_STUDENTS,
)
from modules.student_performance.model import (
    StudentPerformancePredictor,
    generate_synthetic_academic_dataset,
)
from modules.student_performance.interface import render


def test_config_integrity():
    """Verify feature schemas, bounds, and sample student profiles."""
    assert len(NUMERICAL_FEATURES) == 10
    for feat in NUMERICAL_FEATURES:
        assert feat in FEATURE_LABELS
        assert feat in FEATURE_BOUNDS
        bounds = FEATURE_BOUNDS[feat]
        assert bounds["min"] < bounds["max"]
        assert bounds["min"] <= bounds["default"] <= bounds["max"]

    assert len(GRADE_BANDS) >= 4
    assert len(SAMPLE_STUDENTS) >= 3


def test_synthetic_academic_dataset():
    """Verify synthetic dataset generator produces valid, clean dataframe."""
    df = generate_synthetic_academic_dataset(n_samples=200, random_state=123)
    assert len(df) == 200
    for feat in NUMERICAL_FEATURES:
        assert feat in df.columns
    assert "target_gpa" in df.columns
    assert "target_risk" in df.columns

    # Verify no nulls
    assert df.isnull().sum().sum() == 0

    # Verify target GPA bounded between 1.0 and 4.0
    assert df["target_gpa"].min() >= 1.0
    assert df["target_gpa"].max() <= 4.0

    # Verify risk classes exist
    unique_risks = set(df["target_risk"].unique())
    assert "On-Track" in unique_risks
    assert "At-Risk" in unique_risks


def test_model_training_and_metrics():
    """Verify training executes properly and meets performance baselines."""
    predictor = StudentPerformancePredictor(auto_train=False)
    metrics = predictor.train()

    assert predictor.is_trained is True
    assert metrics["r2_score"] >= 0.85
    assert metrics["rmse"] <= 0.25
    assert metrics["accuracy"] >= 0.90
    assert len(predictor.feature_importances_) == len(NUMERICAL_FEATURES)


def test_model_serialization(tmp_path: Path):
    """Verify artifact serialization and reloading."""
    predictor = StudentPerformancePredictor(auto_train=True)
    temp_artifact = tmp_path / "test_model.joblib"

    saved_path = predictor.save_artifacts(temp_artifact)
    assert saved_path.exists()

    new_predictor = StudentPerformancePredictor(auto_train=False)
    success = new_predictor.load_artifacts(temp_artifact)
    assert success is True
    assert new_predictor.is_trained is True


def test_prediction_schema_and_values():
    """Verify end-to-end inference output contract."""
    predictor = StudentPerformancePredictor(auto_train=True)
    sample_input = SAMPLE_STUDENTS["High-Achieving Honors Scholar"]["features"]

    result = predictor.predict(sample_input)
    assert result["status"] == "success"
    assert 3.5 <= result["predicted_gpa"] <= 4.0
    assert result["risk_status"] == "On-Track"
    assert "grade_band" in result
    assert "factor_influences" in result
    assert len(result["factor_influences"]) == len(NUMERICAL_FEATURES)
    assert "interventions" in result
    assert "trend_projection" in result
    assert len(result["trend_projection"]) == 4
    assert 80.0 <= result["retention_probability"] <= 100.0


def test_prediction_at_risk_detection():
    """Verify that a failing student profile is flagged as At-Risk."""
    predictor = StudentPerformancePredictor(auto_train=True)
    critical_input = SAMPLE_STUDENTS["Critical Intervention Required (At-Risk)"]["features"]

    result = predictor.predict(critical_input)
    assert result["risk_status"] == "At-Risk"
    assert result["predicted_gpa"] < 2.5
    # Must have actionable interventions
    assert len(result["interventions"]) > 0


def test_interface_render_callable():
    """Verify that interface exposes callable render function."""
    assert callable(render)
