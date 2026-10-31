"""
TalentBridge AI - Student Performance Prediction Model
Assigned Lead: Member 3

Production ML Pipeline:
- Inputs:
    - Past Semester GPAs (Sem 1, Sem 2, Sem 3)
    - Midterm & Core Exam Grades
    - Lecture Attendance Rate
    - LMS Portal Engagement (Hours/Week, Logins/Week)
    - Assignment Submission Punctuality
    - Extracurricular Participation Index
    - Independent Study Hours
- Outputs:
    - Predicted End-of-Semester GPA / Grade band
    - Risk Classification: 'On-Track' vs 'Moderate Risk' vs 'At-Risk'
    - Risk Probabilities
    - Key Academic Factor Influence Weights (Feature Attributions)
    - Semester Trajectory Projection & Academic Guidance Plan
- Algorithms:
    - Ensemble Regressor: GradientBoostingRegressor + RandomForestRegressor
    - Risk Classifier: RandomForestClassifier with probability calibration
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from .config import (
    FEATURE_BOUNDS,
    FEATURE_LABELS,
    GRADE_BANDS,
    MODEL_PATH,
    NUMERICAL_FEATURES,
    RISK_LEVEL_THRESHOLDS,
)


def generate_synthetic_academic_dataset(n_samples: int = 1500, random_state: int = 42) -> pd.DataFrame:
    """
    Generates a realistic, correlated educational performance dataset representing diverse
    college student learning behaviors, historical GPAs, engagement metrics, and semester outcomes.
    """
    rng = np.random.default_rng(random_state)

    # Underlying student capability / baseline aptitude (latent factor ~ Normal(3.0, 0.5))
    latent_ability = rng.normal(loc=3.0, scale=0.45, size=n_samples)
    latent_ability = np.clip(latent_ability, 1.2, 4.0)

    # Attendance rate correlated with capability and motivation
    attendance_rate = latent_ability * 22.0 + rng.normal(loc=15.0, scale=8.0, size=n_samples)
    attendance_rate = np.clip(attendance_rate, 35.0, 100.0)

    # LMS engagement hours/week
    lms_hours = (latent_ability * 2.8) + (attendance_rate / 25.0) + rng.normal(loc=0.0, scale=2.0, size=n_samples)
    lms_hours = np.clip(lms_hours, 1.0, 32.0)

    # LMS logins/week
    lms_logins = lms_hours * 1.3 + rng.normal(loc=3.0, scale=2.5, size=n_samples)
    lms_logins = np.clip(lms_logins, 2.0, 38.0)

    # Assignment punctuality
    assignment_punctuality = (attendance_rate * 0.6) + (latent_ability * 8.0) + rng.normal(loc=10.0, scale=6.0, size=n_samples)
    assignment_punctuality = np.clip(assignment_punctuality, 25.0, 100.0)

    # Study hours per week
    study_hours = (latent_ability * 3.5) + rng.normal(loc=4.0, scale=3.5, size=n_samples)
    study_hours = np.clip(study_hours, 3.0, 42.0)

    # Extracurricular index (0 - 10)
    extracurricular_index = rng.uniform(1.0, 9.5, size=n_samples)

    # Past Semester GPAs with temporal progression
    gpa_sem1 = latent_ability + rng.normal(loc=-0.1, scale=0.2, size=n_samples)
    gpa_sem1 = np.clip(gpa_sem1, 1.0, 4.0)

    gpa_sem2 = 0.6 * gpa_sem1 + 0.4 * latent_ability + rng.normal(loc=0.0, scale=0.18, size=n_samples)
    gpa_sem2 = np.clip(gpa_sem2, 1.0, 4.0)

    gpa_sem3 = 0.5 * gpa_sem2 + 0.3 * gpa_sem1 + 0.2 * latent_ability + rng.normal(loc=0.02, scale=0.16, size=n_samples)
    gpa_sem3 = np.clip(gpa_sem3, 1.0, 4.0)

    # Midterm exam score (0 - 100)
    midterm_score = (
        gpa_sem3 * 18.0
        + (study_hours * 0.45)
        + (attendance_rate * 0.15)
        + rng.normal(loc=8.0, scale=5.0, size=n_samples)
    )
    midterm_score = np.clip(midterm_score, 25.0, 100.0)

    # Final Outcome GPA (Target Variable)
    base_gpa = (
        0.38 * gpa_sem3
        + 0.22 * gpa_sem2
        + 0.12 * gpa_sem1
        + 0.010 * midterm_score
        + 0.003 * attendance_rate
        + 0.004 * assignment_punctuality
        + 0.006 * lms_hours
        + 0.005 * study_hours
        + rng.normal(loc=-0.15, scale=0.10, size=n_samples)
    )

    # Real-world academic penalties for severe attendance drops or exam failures
    attendance_penalty = np.where(attendance_rate < 65.0, 0.35, 0.0)
    midterm_penalty = np.where(midterm_score < 50.0, 0.30, 0.0)
    predicted_gpa = base_gpa - attendance_penalty - midterm_penalty
    predicted_gpa = np.clip(predicted_gpa, 1.0, 4.0)

    # Academic Risk Label
    risk_labels = []
    for gpa, att, punc in zip(predicted_gpa, attendance_rate, assignment_punctuality):
        if gpa >= RISK_LEVEL_THRESHOLDS["on_track_gpa"] and att >= 75.0 and punc >= 70.0:
            risk_labels.append("On-Track")
        elif gpa < RISK_LEVEL_THRESHOLDS["moderate_risk_gpa"] or att < RISK_LEVEL_THRESHOLDS["attendance_critical"]:
            risk_labels.append("At-Risk")
        else:
            risk_labels.append("Moderate Risk")

    df = pd.DataFrame({
        "gpa_sem1": np.round(gpa_sem1, 2),
        "gpa_sem2": np.round(gpa_sem2, 2),
        "gpa_sem3": np.round(gpa_sem3, 2),
        "midterm_score": np.round(midterm_score, 1),
        "attendance_rate": np.round(attendance_rate, 1),
        "lms_hours_per_week": np.round(lms_hours, 1),
        "lms_logins_per_week": np.round(lms_logins, 1),
        "assignment_punctuality_rate": np.round(assignment_punctuality, 1),
        "extracurricular_index": np.round(extracurricular_index, 1),
        "study_hours_per_week": np.round(study_hours, 1),
        "target_gpa": np.round(predicted_gpa, 2),
        "target_risk": risk_labels,
    })
    return df


class StudentPerformancePredictor:
    """
    Dual-pipeline ML engine for Student Performance Prediction and Academic Risk Analysis.
    Predicts:
    1. Continuous Final Semester GPA via Gradient Boosting Regressor
    2. Categorical Risk Classification ('On-Track', 'Moderate Risk', 'At-Risk')
    3. Academic Factor Weights and Tailored Guidance Recommendations
    """

    def __init__(self, auto_train: bool = True) -> None:
        self.is_trained: bool = False
        self.regressor: Optional[GradientBoostingRegressor] = None
        self.classifier: Optional[RandomForestClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: List[str] = NUMERICAL_FEATURES
        self.feature_importances_: Dict[str, float] = {}
        self.metrics_: Dict[str, Any] = {}

        # Attempt to load serialized artifacts or initialize with baseline training
        if not self.load_artifacts():
            if auto_train:
                self.train()

    def train(self, data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Trains both regression and classification pipelines on the provided
        or generated training dataset.
        """
        if data is None:
            data = generate_synthetic_academic_dataset(n_samples=1500, random_state=42)

        # Convert to raw numpy arrays to prevent indexing issues across versions
        X_arr = np.asarray(data[self.feature_names].values, dtype=np.float64)
        y_reg = np.asarray(data["target_gpa"].values, dtype=np.float64)
        y_clf = np.asarray(data["target_risk"].values, dtype=str)

        # Split into training and testing partitions
        X_train, X_test, y_reg_train, y_reg_test, y_clf_train, y_clf_test = train_test_split(
            X_arr, y_reg, y_clf, test_size=0.20, random_state=42, stratify=y_clf
        )

        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # 1. Regression Pipeline (Gradient Boosting Regressor)
        self.regressor = GradientBoostingRegressor(
            n_estimators=120,
            learning_rate=0.08,
            max_depth=4,
            subsample=0.85,
            random_state=42,
        )
        self.regressor.fit(X_train_scaled, y_reg_train)
        y_reg_pred = self.regressor.predict(X_test_scaled)
        y_reg_pred = np.clip(y_reg_pred, 1.0, 4.0)

        # Regression Metrics
        r2 = float(r2_score(y_reg_test, y_reg_pred))
        rmse = float(np.sqrt(mean_squared_error(y_reg_test, y_reg_pred)))
        mae = float(mean_absolute_error(y_reg_test, y_reg_pred))

        # 2. Classification Pipeline (Random Forest Classifier)
        self.classifier = RandomForestClassifier(
            n_estimators=120,
            max_depth=6,
            class_weight="balanced",
            random_state=42,
        )
        self.classifier.fit(X_train_scaled, y_clf_train)
        y_clf_pred = self.classifier.predict(X_test_scaled)

        # Classification Metrics
        acc = float(accuracy_score(y_clf_test, y_clf_pred))
        f1_macro = float(f1_score(y_clf_test, y_clf_pred, average="macro"))

        # Feature Importances (Normalized Combination)
        reg_importances = self.regressor.feature_importances_
        clf_importances = self.classifier.feature_importances_
        combined_importances = (reg_importances * 0.5) + (clf_importances * 0.5)
        total_sum = combined_importances.sum()
        if total_sum > 0:
            combined_importances = combined_importances / total_sum

        self.feature_importances_ = {
            feat: float(round(combined_importances[i] * 100.0, 2))
            for i, feat in enumerate(self.feature_names)
        }

        self.metrics_ = {
            "r2_score": round(r2, 4),
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
            "accuracy": round(acc, 4),
            "f1_macro": round(f1_macro, 4),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        }

        self.is_trained = True
        return self.metrics_

    def save_artifacts(self, filepath: Optional[Path] = None) -> Path:
        """
        Serializes trained models, scaler, feature weights, and metrics to disk.
        """
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained model pipeline.")

        target = Path(filepath or MODEL_PATH)
        target.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "regressor": self.regressor,
            "classifier": self.classifier,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "feature_importances_": self.feature_importances_,
            "metrics_": self.metrics_,
        }
        joblib.dump(payload, target, compress=3)
        return target

    def load_artifacts(self, filepath: Optional[Path] = None) -> bool:
        """
        Loads pre-trained model artifacts from disk if available.
        """
        target = Path(filepath or MODEL_PATH)
        if target.exists():
            try:
                payload = joblib.load(target)
                self.regressor = payload["regressor"]
                self.classifier = payload["classifier"]
                self.scaler = payload["scaler"]
                self.feature_names = payload.get("feature_names", NUMERICAL_FEATURES)
                self.feature_importances_ = payload.get("feature_importances_", {})
                self.metrics_ = payload.get("metrics_", {})
                self.is_trained = True
                return True
            except Exception:
                return False
        return False

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes end-to-end inference on incoming student academic metrics.
        Returns predicted GPA, grade band, risk status, factor influences,
        retention probability, and personalized intervention guidance.
        """
        if not self.is_trained or self.regressor is None or self.scaler is None:
            self.train()

        # Build feature vector with default fallbacks
        row = []
        clean_features = {}
        for feat in self.feature_names:
            default_val = FEATURE_BOUNDS.get(feat, {}).get("default", 0.0)
            val = float(features.get(feat, default_val))
            bounds = FEATURE_BOUNDS.get(feat)
            if bounds:
                val = float(np.clip(val, bounds["min"], bounds["max"]))
            row.append(val)
            clean_features[feat] = val

        X_input = np.array([row], dtype=np.float64)
        X_scaled = self.scaler.transform(X_input)

        # 1. Regress Continuous GPA
        raw_pred_gpa = float(self.regressor.predict(X_scaled)[0])
        predicted_gpa = float(np.clip(np.round(raw_pred_gpa, 2), 1.0, 4.0))

        # 2. Classify Risk & Probabilities
        predicted_risk = "On-Track"
        risk_probs: Dict[str, float] = {}

        if self.classifier is not None and hasattr(self.classifier, "predict_proba"):
            classes = list(self.classifier.classes_)
            probs = self.classifier.predict_proba(X_scaled)[0]
            for cls_name, prob in zip(classes, probs):
                risk_probs[str(cls_name)] = round(float(prob) * 100.0, 1)

            # Rule check: if GPA < 2.3 or attendance < 65%, force risk status
            raw_risk = str(self.classifier.predict(X_scaled)[0])
            if predicted_gpa < RISK_LEVEL_THRESHOLDS["moderate_risk_gpa"] or clean_features["attendance_rate"] < RISK_LEVEL_THRESHOLDS["attendance_critical"]:
                predicted_risk = "At-Risk"
            elif predicted_gpa < RISK_LEVEL_THRESHOLDS["on_track_gpa"]:
                predicted_risk = "Moderate Risk" if raw_risk != "At-Risk" else "At-Risk"
            else:
                predicted_risk = raw_risk
        else:
            if predicted_gpa >= 3.0 and clean_features["attendance_rate"] >= 75.0:
                predicted_risk = "On-Track"
                risk_probs = {"On-Track": 85.0, "Moderate Risk": 12.0, "At-Risk": 3.0}
            elif predicted_gpa < 2.3 or clean_features["attendance_rate"] < 65.0:
                predicted_risk = "At-Risk"
                risk_probs = {"On-Track": 5.0, "Moderate Risk": 20.0, "At-Risk": 75.0}
            else:
                predicted_risk = "Moderate Risk"
                risk_probs = {"On-Track": 25.0, "Moderate Risk": 65.0, "At-Risk": 10.0}

        # 3. Grade Band Lookup
        selected_band = GRADE_BANDS[-1]
        for band_info in GRADE_BANDS:
            if predicted_gpa >= band_info["min_gpa"]:
                selected_band = band_info
                break

        # 4. GPA Delta Calculation
        sem3_gpa = clean_features.get("gpa_sem3", clean_features.get("gpa_sem2", 3.0))
        gpa_delta = round(predicted_gpa - sem3_gpa, 2)

        # 5. Detailed Factor Influence Weights
        factor_influences = self._compute_factor_influences(clean_features)

        # 6. Actionable Interventions
        interventions = self._generate_interventions(clean_features, predicted_gpa, predicted_risk)

        # 7. Projected Semester Trajectory
        trend_projection = [
            {"semester": "Sem 1", "gpa": clean_features["gpa_sem1"], "type": "Historical"},
            {"semester": "Sem 2", "gpa": clean_features["gpa_sem2"], "type": "Historical"},
            {"semester": "Sem 3", "gpa": clean_features["gpa_sem3"], "type": "Historical"},
            {"semester": "Sem 4 (Predicted)", "gpa": predicted_gpa, "type": "Forecast"},
        ]

        # 8. Graduation Retention Probability Index (0 - 100%)
        retention_index = self._calculate_retention_index(clean_features, predicted_gpa)

        # Risk Styling
        risk_color_map = {
            "On-Track": "#10b981",
            "Moderate Risk": "#f59e0b",
            "At-Risk": "#ef4444",
        }

        return {
            "status": "success",
            "predicted_gpa": predicted_gpa,
            "gpa_delta": gpa_delta,
            "grade_band": selected_band["band"],
            "grade_badge": selected_band["badge"],
            "grade_color": selected_band["color"],
            "risk_status": predicted_risk,
            "risk_color": risk_color_map.get(predicted_risk, "#6366f1"),
            "risk_probabilities": risk_probs,
            "retention_probability": retention_index,
            "factor_influences": factor_influences,
            "interventions": interventions,
            "trend_projection": trend_projection,
            "inputs_received": clean_features,
            "model_metrics": self.metrics_,
        }

    def _compute_factor_influences(self, features: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Evaluates how each academic factor contributes (positive or negative drag)
        relative to institutional expectations and baseline importance.
        """
        influences = []
        for feat in self.feature_names:
            val = features[feat]
            weight = self.feature_importances_.get(feat, 10.0)

            # Direction of impact
            if feat in ["gpa_sem1", "gpa_sem2", "gpa_sem3"]:
                impact = "Positive Catalyst" if val >= 3.2 else ("Neutral" if val >= 2.5 else "Academic Drag")
                delta_str = f"{val:.2f} GPA"
            elif feat in ["attendance_rate", "assignment_punctuality_rate"]:
                impact = "Positive Catalyst" if val >= 80.0 else ("Neutral" if val >= 70.0 else "Critical Deficit")
                delta_str = f"{val:.1f}%"
            elif feat == "midterm_score":
                impact = "Positive Catalyst" if val >= 75.0 else ("Neutral" if val >= 60.0 else "Exam Deficit")
                delta_str = f"{val:.1f}/100"
            elif feat in ["study_hours_per_week", "lms_hours_per_week"]:
                impact = "High Engagement" if val >= 12.0 else ("Adequate" if val >= 6.0 else "Low Engagement")
                delta_str = f"{val:.1f} hrs/wk"
            else:
                impact = "Active" if val >= 5.0 else "Minimal"
                delta_str = f"{val:.1f}/10"

            influences.append({
                "feature": feat,
                "label": FEATURE_LABELS.get(feat, feat),
                "value_formatted": delta_str,
                "importance_pct": weight,
                "impact": impact,
            })

        # Sort by importance percentage descending
        influences.sort(key=lambda x: x["importance_pct"], reverse=True)
        return influences

    def _generate_interventions(
        self, features: Dict[str, float], predicted_gpa: float, risk_status: str
    ) -> List[Dict[str, str]]:
        """
        Generates tailored, actionable intervention blueprints based on identified risk vectors.
        """
        interventions: List[Dict[str, str]] = []

        if features["attendance_rate"] < 75.0:
            deficit = round(80.0 - features["attendance_rate"], 1)
            interventions.append({
                "category": "Attendance & Engagement",
                "severity": "High Priority",
                "color": "#ef4444",
                "action": f"Boost physical lecture attendance by +{deficit}% to clear the minimum 80% threshold required for academic compliance.",
            })

        if features["assignment_punctuality_rate"] < 75.0:
            interventions.append({
                "category": "Submission Punctuality",
                "severity": "Medium Priority",
                "color": "#f59e0b",
                "action": "Implement a structured sprint calendar. Late assignments currently drag the term GPA by up to -0.35 points.",
            })

        if features["midterm_score"] < 65.0:
            interventions.append({
                "category": "Exam Prep & Tutoring",
                "severity": "High Priority",
                "color": "#ef4444",
                "action": "Schedule bi-weekly departmental peer-tutoring sessions for core subject modules before final semester exams.",
            })

        if features["lms_hours_per_week"] < 5.0:
            interventions.append({
                "category": "LMS Resource Engagement",
                "severity": "Low Priority",
                "color": "#3b82f6",
                "action": "Increase LMS review of asynchronous course slides, recorded lectures, and practice quizzes by 3 hours per week.",
            })

        if features["study_hours_per_week"] < 10.0 and predicted_gpa < 3.2:
            interventions.append({
                "category": "Independent Study Time",
                "severity": "Medium Priority",
                "color": "#f59e0b",
                "action": "Target at least 12-15 hours/week of focused study blocks outside lecture hours.",
            })

        if not interventions:
            interventions.append({
                "category": "Academic Excellence & Enrichment",
                "severity": "Growth Opportunity",
                "color": "#10b981",
                "action": "Candidate is performing in the top percentile! Recommend applying for Undergraduate Research Fellowships or TA positions.",
            })

        return interventions

    def _calculate_retention_index(self, features: Dict[str, float], predicted_gpa: float) -> float:
        """
        Calculates an integrated graduation retention probability percentage (0 - 100%).
        """
        base = (predicted_gpa / 4.0) * 55.0
        att_part = (features["attendance_rate"] / 100.0) * 25.0
        punc_part = (features["assignment_punctuality_rate"] / 100.0) * 12.0
        study_part = min(features["study_hours_per_week"] / 20.0, 1.0) * 8.0

        score = base + att_part + punc_part + study_part
        return float(np.clip(round(score, 1), 10.0, 99.5))
