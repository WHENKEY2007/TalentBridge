"""
Unit tests for AI Resume Analysis Module (Member 10).
Tests text preprocessing, contact parsing, section segmentation, action verbs,
quantification diagnostics, readability metrics, and ML inference contracts.
"""

from pathlib import Path
import sys
import warnings
import pytest

# Filter numpy 2.5 shape setting deprecation in scikit-learn/joblib
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Ensure TalentBridge root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules.resume_analyzer.config import SAMPLE_RESUMES
from modules.resume_analyzer.interface import render
from modules.resume_analyzer.model import ResumeAnalyzer
from modules.resume_analyzer.preprocessing import (
    analyze_action_verbs,
    analyze_industry_alignment,
    analyze_quantification,
    analyze_readability,
    clean_text,
    extract_bullet_points,
    extract_contact_info,
    extract_feature_vector,
    parse_document,
    segment_sections,
)


def test_clean_text():
    sample = "• Developed API endpoints.\r\n- Built microservices."
    cleaned = clean_text(sample)
    assert "- " in cleaned
    assert "\r" not in cleaned


def test_parse_document_string_and_bytes():
    assert parse_document("Plain text resume") == "Plain text resume"
    assert parse_document(b"Byte encoded resume text") == "Byte encoded resume text"
    assert parse_document(None) == ""


def test_extract_contact_info():
    text = """
    Jane Developer | San Francisco, CA | (555) 123-4567 | jane.dev@company.com
    linkedin.com/in/janedev | github.com/janedev | https://janedev.io
    """
    contact = extract_contact_info(text)
    assert contact["has_email"] is True
    assert contact["fields"]["email"] == "jane.dev@company.com"
    assert contact["has_phone"] is True
    assert contact["has_linkedin"] is True
    assert contact["has_github"] is True
    assert contact["completeness_score"] >= 90.0


def test_segment_sections():
    text = SAMPLE_RESUMES["Entry-Level CS Graduate (High Quality)"]["text"]
    sections = segment_sections(text)

    assert sections["summary"]["found"] is True
    assert sections["education"]["found"] is True
    assert sections["skills"]["found"] is True
    assert sections["projects"]["found"] is True
    assert sections["experience"]["found"] is True
    assert sections["certifications"]["found"] is True


def test_extract_bullet_points():
    text = """
    EXPERIENCE
    - Architected distributed data processing engine with 99.9% uptime.
    - Reduced latency by 35% through Redis caching.
    • Built 6 reusable React components.
    """
    bullets = extract_bullet_points(text)
    assert len(bullets) >= 3
    assert any("Architected" in b for b in bullets)
    assert any("latency" in b for b in bullets)


def test_analyze_action_verbs_strong_and_weak():
    strong_text = "Architected, engineered, and optimized high-performance systems. Spearheaded team of 8."
    bullets = ["Architected cloud pipeline.", "Engineered backend microservices."]
    res = analyze_action_verbs(strong_text, bullets)
    assert res["total_unique_action_verbs"] >= 4
    assert res["action_verb_density_pct"] == 100.0
    assert res["weak_count"] == 0

    weak_text = "Responsible for fixing bugs and helped with database. Duties included meetings."
    res_weak = analyze_action_verbs(weak_text, ["Responsible for tasks."])
    assert res_weak["weak_count"] >= 3
    assert any(a["weak_phrase"] == "responsible for" for a in res_weak["improvement_advice"])


def test_analyze_quantification():
    bullets = [
        "Reduced cloud costs by 35% saving $1.2M annually.",
        "Scaled architecture to handle 50,000 users with sub-20ms latency.",
        "Worked on general features.",
    ]
    quant = analyze_quantification(bullets)
    assert quant["quantified_bullet_count"] == 2
    assert quant["quantification_pct"] == pytest.approx(66.7, 0.1)
    assert len(quant["extracted_metrics"]) >= 2


def test_analyze_readability():
    text = SAMPLE_RESUMES["Senior Tech Lead / Architect (Elite Benchmark)"]["text"]
    read = analyze_readability(text)
    assert read["word_count"] > 200
    assert read["estimated_pages"] >= 0.5
    assert 0.0 <= read["flesch_reading_ease"] <= 100.0


def test_analyze_industry_alignment():
    text = "Proficient in Python, Docker, Kubernetes, PostgreSQL, Git, Microservices, and REST API."
    align = analyze_industry_alignment(text, "Software & Technology")
    assert "python" in align["matched_skills"]
    assert "docker" in align["matched_skills"]
    assert align["alignment_pct"] > 15.0


def test_extract_feature_vector():
    text = SAMPLE_RESUMES["Entry-Level CS Graduate (High Quality)"]["text"]
    feat = extract_feature_vector(text, "Software & Technology", "Entry-Level / Graduate")
    assert isinstance(feat, dict)
    assert "feat_has_education" in feat
    assert feat["feat_has_education"] == 1.0
    assert "feat_action_verb_density" in feat
    assert "feat_quantification_ratio" in feat
    assert all(0.0 <= v <= 1.0 for v in feat.values())


def test_resume_analyzer_model_elite():
    analyzer = ResumeAnalyzer()
    elite_text = SAMPLE_RESUMES["Senior Tech Lead / Architect (Elite Benchmark)"]["text"]
    res = analyzer.predict({"text": elite_text, "industry": "Software & Technology", "career_level": "Senior / Executive Lead"})

    assert res["status"] == "success"
    assert res["overall_ats_score"] >= 80.0
    assert res["tier"] in ["Elite", "Competitive"]
    assert res["grade"] in ["A+", "A", "B+"]
    assert res["verbs_audit"]["total_unique_action_verbs"] >= 5
    assert len(res["recommendations"]) >= 0


def test_resume_analyzer_model_unoptimized():
    analyzer = ResumeAnalyzer()
    weak_text = SAMPLE_RESUMES["Unoptimized Resume with Passive Language (Needs Work)"]["text"]
    res = analyzer.predict({"text": weak_text, "industry": "Software & Technology", "career_level": "Mid-Level Professional"})

    assert res["status"] == "success"
    assert res["overall_ats_score"] < 75.0
    assert res["verbs_audit"]["weak_count"] >= 3
    # Ensure actionable recommendations were generated
    rec_titles = [r["title"] for r in res["recommendations"]]
    assert any("Passive" in t or "Action Verb" in t for t in rec_titles)


def test_interface_render_contract():
    assert callable(render), "interface.py must expose a callable render() function."
