"""
TalentBridge AI - Fake Internship & Job Fraud Classifier
Unified ML architecture for 24B11AI134 & 24P31A42D0.
"""

from modules.fake_job_detection.model import FakeJobDetector


class InternshipFraudDetector(FakeJobDetector):
    """
    Unified fraud classifier for both Job and Internship postings.
    Co-maintained by 24B11AI134 and 24P31A42D0.
    """
    pass


__all__ = ["InternshipFraudDetector"]
