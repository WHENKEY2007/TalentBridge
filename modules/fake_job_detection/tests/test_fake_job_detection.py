
import pandas as pd
import pytest
import numpy as np

from modules.fake_job_detection.model import FakeJobDetector


def test_detector_starts_untrained():
    detector = FakeJobDetector()

    assert detector.is_trained is False
    assert detector.pipeline is None


def test_predict_requires_trained_model():
    detector = FakeJobDetector()

    with pytest.raises(RuntimeError):
        detector.predict({"title": "Software Engineer"})


def test_screen_jobs_requires_trained_model():
    detector = FakeJobDetector()
    jobs = pd.DataFrame({"title": ["Software Engineer"]})

    with pytest.raises(RuntimeError):
        detector.screen_jobs(jobs)


def test_screen_jobs_returns_only_legitimate_predictions():
    detector = FakeJobDetector()
    detector.is_trained = True

    class DummyPipeline:
        def predict_proba(self, text):
            return np.array([
                [0.90, 0.10],
                [0.20, 0.80],
                [0.65, 0.35],
            ])

        named_steps = {
            "classifier": type(
                "DummyClassifier",
                (),
                {"classes_": [0, 1]},
            )()
        }

    detector.pipeline = DummyPipeline()

    jobs = pd.DataFrame({
        "title": [
            "Software Engineer",
            "Suspicious Job",
            "Data Analyst",
        ]
    })

    screened = detector.screen_jobs(jobs)

    assert len(screened) == 2
    assert screened["title"].tolist() == [
        "Software Engineer",
        "Data Analyst",
    ]
    assert (screened["fraud_probability"] < 0.5).all()
    assert (screened["listing_type"] == "Historical demo listing").all()
