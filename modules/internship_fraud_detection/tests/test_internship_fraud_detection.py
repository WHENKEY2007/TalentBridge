import pytest
from modules.internship_fraud_detection.model import InternshipFraudDetector
from modules.fake_job_detection.analyzer import audit_job_posting_security


def test_internship_detector_initialization():
    detector = InternshipFraudDetector()
    assert detector.is_trained is False
    assert detector.pipeline is None


def test_internship_detector_load_and_predict():
    detector = InternshipFraudDetector()
    detector.load()
    assert detector.is_trained is True

    # Test legitimate internship posting
    legit_job = {
        "title": "Software Engineering Summer Intern",
        "company_profile": "CloudScale Systems",
        "description": "We are seeking a summer software engineering intern with Python and SQL knowledge. Competitive stipend provided.",
        "requirements": "Currently enrolled in Computer Science degree.",
        "benefits": "$35/hour stipend, mentorship, and full health insurance.",
    }
    result = detector.predict(legit_job)
    assert result["status"] == "success"
    assert "fraud_probability" in result
    assert "trust_score" in result


def test_internship_certificate_fee_threat_detection():
    # Test fraudulent internship asking for upfront fee
    scam_text = (
        "Congratulations on being selected for the machine learning internship! "
        "To confirm your seat and receive your certificate and offer letter, "
        "all students must pay a mandatory internship registration fee of $120."
    )
    audit = audit_job_posting_security(
        text=scam_text,
        title="ML Intern",
        company="EduSkills Tech",
        model_fraud_prob=0.8,
    )
    assert len(audit["red_flags"]) > 0
    flag_titles = [f["title"] for f in audit["red_flags"]]
    assert any("Internship" in t or "Fee" in t for t in flag_titles)
    assert audit["threat_level"] in ("Critical / High Risk", "Elevated Risk / Suspicious")
