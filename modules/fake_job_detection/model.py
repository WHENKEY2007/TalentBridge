
"""
TalentBridge AI - Fake Job Posting Detection Model
Automatically screens historical job postings using ML.
"""

from pathlib import Path
from typing import Any, Dict

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report


MODULE_DIR = Path(__file__).resolve().parent
DATA_PATH = MODULE_DIR / "data" / "fake_job_postings.csv"
MODEL_PATH = MODULE_DIR / "artifacts" / "fake_job_model.joblib"

TEXT_COLUMNS = [
    "title",
    "company_profile",
    "description",
    "requirements",
    "benefits",
]


class FakeJobDetector:
    """Train a fraud classifier and screen job listings automatically."""

    def __init__(self) -> None:
        self.is_trained = False
        self.pipeline = None

    @staticmethod
    def _combine_text(data: pd.DataFrame) -> pd.Series:
        """Combine job text fields into one NLP input."""
        available = [column for column in TEXT_COLUMNS if column in data.columns]

        if not available:
            raise ValueError("No supported job text columns were found.")

        combined = data[available[0]].fillna("").astype(str)

        for column in available[1:]:
            combined = combined + " " + data[column].fillna("").astype(str)

        return combined.str.strip()

    def train(self, data: Any = None) -> Dict[str, Any]:
        """Train and evaluate the model, then save the trained pipeline."""
        if data is None:
            if not DATA_PATH.exists():
                raise FileNotFoundError(
                    f"Dataset not found: {DATA_PATH}. "
                    "Place fake_job_postings.csv in the module data folder."
                )

            columns = TEXT_COLUMNS + ["fraudulent"]
            data = pd.read_csv(
                DATA_PATH,
                usecols=lambda column: column in columns,
            )

        if not isinstance(data, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame or None.")

        if "fraudulent" not in data.columns:
            raise ValueError("Dataset must contain the 'fraudulent' column.")

        data = data.dropna(subset=["fraudulent"]).copy()
        data["fraudulent"] = pd.to_numeric(
            data["fraudulent"], errors="coerce"
        )
        data = data.dropna(subset=["fraudulent"])
        data = data[data["fraudulent"].isin([0, 1])]

        if data["fraudulent"].nunique() != 2:
            raise ValueError("Training data must contain both fraud labels.")

        X = self._combine_text(data)
        y = data["fraudulent"].astype(int)

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )

        self.pipeline = Pipeline([
            (
                "tfidf",
                TfidfVectorizer(
                    stop_words="english",
                    max_features=50000,
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ])

        self.pipeline.fit(X_train, y_train)
        predictions = self.pipeline.predict(X_test)

        report = classification_report(
            y_test,
            predictions,
            labels=[0, 1],
            target_names=["Legitimate", "Fraudulent"],
            zero_division=0,
            output_dict=True,
        )

        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, MODEL_PATH)
        self.is_trained = True

        return {
            "train_rows": len(X_train),
            "test_rows": len(X_test),
            "model_path": str(MODEL_PATH),
            "classification_report": report,
        }

    def load(self) -> None:
        """Load a previously trained model from the artifact folder."""
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "Trained model not found. Train the model first."
            )

        self.pipeline = joblib.load(MODEL_PATH)
        self.is_trained = True

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict whether one posting is likely fraudulent."""
        if not self.is_trained or self.pipeline is None:
            raise RuntimeError("Train or load the model before prediction.")

        row = pd.DataFrame([features])
        text = self._combine_text(row)
        probabilities = self.pipeline.predict_proba(text)[0]

        classes = list(self.pipeline.named_steps["classifier"].classes_)
        fraud_probability = float(probabilities[classes.index(1)])

        return {
            "status": "success",
            "label": (
                "Fraudulent" if fraud_probability >= 0.5 else "Legitimate"
            ),
            "fraud_probability": round(fraud_probability, 4),
            "trust_score": round((1 - fraud_probability) * 100, 1),
            "disclaimer": (
                "This is a model prediction, not proof of authenticity."
            ),
        }

    def screen_jobs(self, jobs: pd.DataFrame) -> pd.DataFrame:
        """Return only jobs predicted as legitimate by the trained model."""
        if not self.is_trained or self.pipeline is None:
            raise RuntimeError("Train or load the model before screening.")

        if jobs.empty:
            return jobs.copy()

        result = jobs.copy()
        text = self._combine_text(result)
        probabilities = self.pipeline.predict_proba(text)

        classes = list(self.pipeline.named_steps["classifier"].classes_)
        fraud_index = classes.index(1)

        result["fraud_probability"] = probabilities[:, fraud_index]

        # Trust score is the inverse of estimated fraud probability.
        result["trust_score"] = (
            (1 - result["fraud_probability"]) * 100
        ).round(1)

        # Keep only postings classified as legitimate at threshold 0.5.
        screened = result[result["fraud_probability"] < 0.5].copy()
        screened["listing_type"] = "Historical demo listing"

        return screened.reset_index(drop=True)
