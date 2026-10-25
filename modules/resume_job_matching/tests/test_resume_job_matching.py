"""
Unit tests for the upgraded Resume–Job Matching module.
Tests document parsing, skills taxonomy extraction with alias resolution,
experience extraction, seniority fit, ATS diagnostics, what-if simulations, and report generation.
"""

import io
import pytest

from modules.resume_job_matching.config import SAMPLE_JOB_DESCRIPTION, SAMPLE_RESUME
from modules.resume_job_matching.model import ResumeJobMatcher
from modules.resume_job_matching.preprocessing import (
    audit_resume_structure,
    clean_text,
    evaluate_seniority_fit,
    extract_experience_years,
    extract_keywords,
    extract_taxonomy_skills,
    find_skill_gap,
    find_skill_gap_detailed,
    parse_document,
)


def test_clean_text_basic():
    raw = "Senior Software Developer with 5+ years experience! Visit https://example.com or email me@work.com"
    cleaned = clean_text(raw)
    assert "https" not in cleaned
    assert "me@work.com" not in cleaned
    assert "senior software developer" in cleaned
    assert "!" not in cleaned


def test_clean_text_empty_and_none():
    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_extract_keywords():
    text = "Python Docker Kubernetes AWS Python Fastapi Microservices Python"
    keywords = extract_keywords(text, top_n=5)
    assert "python" in keywords
    assert keywords[0] == "python"
    assert len(keywords) <= 5


def test_find_skill_gap():
    job = "Requires Python, Kubernetes, Kafka, and Docker."
    resume = "Jane Doe has extensive experience in Python, Docker, and PostgreSQL."
    result = find_skill_gap(resume, job)

    assert "python" in result["matched_keywords"]
    assert "docker" in result["matched_keywords"]
    assert "kubernetes" in result["missing_keywords"]


def test_extract_taxonomy_skills():
    sample_text = "Proficient in Python, FastAPI, Docker, Kubernetes, PostgreSQL, and REST API."
    categorized = extract_taxonomy_skills(sample_text)

    assert "python" in categorized["Programming Languages"]
    assert "fastapi" in categorized["Frameworks & Libraries"]
    assert "rest api" in categorized["Frameworks & Libraries"]
    assert "docker" in categorized["Cloud & DevOps"]
    assert "kubernetes" in categorized["Cloud & DevOps"]
    assert "postgresql" in categorized["Databases & Storage"]


def test_extract_taxonomy_skills_aliases():
    """Verify abbreviation and alias resolution (e.g. k8s -> kubernetes, postgres -> postgresql)."""
    text = "Engineered microservices using Golang, K8s, Postgres, and AWS (Amazon Web Services)."
    categorized = extract_taxonomy_skills(text)

    # golang -> go
    assert "go" in categorized["Programming Languages"]
    # k8s -> kubernetes
    assert "kubernetes" in categorized["Cloud & DevOps"]
    # postgres -> postgresql
    assert "postgresql" in categorized["Databases & Storage"]
    # aws
    assert "aws" in categorized["Cloud & DevOps"]


def test_extract_experience_years():
    resume_text = "Senior Python Developer with 5+ years of experience in distributed systems."
    years = extract_experience_years(resume_text, is_job_description=False)
    assert years == 5.0

    job_text = "Looking for an engineer with 3-5 years experience."
    req_years = extract_experience_years(job_text, is_job_description=True)
    assert req_years == 3.0


def test_evaluate_seniority_fit():
    resume = "Lead Architect with 8+ years experience building scalable systems."
    job = "Seeking Senior Engineer with 5+ years experience in Python."
    fit = evaluate_seniority_fit(resume, job)

    assert fit["candidate_years"] == 8.0
    assert fit["required_years"] == 5.0
    assert fit["fit_score"] >= 0.90
    assert fit["badge"] in ["Well Matched", "Seniority Premium"]


def test_find_skill_gap_detailed():
    job = "Looking for an engineer skilled in Python, Docker, and Kubernetes."
    resume = "Experienced in Python and Docker."
    gap = find_skill_gap_detailed(resume, job)

    assert "python" in gap["matched_skills"]
    assert "docker" in gap["matched_skills"]
    assert "kubernetes" in gap["missing_skills"]
    assert gap["skills_match_ratio"] == pytest.approx(2 / 3, 0.05)


def test_audit_resume_structure():
    audit = audit_resume_structure(SAMPLE_RESUME)

    assert audit["word_count"] > 100
    assert "Professional Experience" in audit["sections_present"]
    assert "Education" in audit["sections_present"]
    assert len(audit["action_verbs_found"]) >= 3
    assert audit["quantification_count"] >= 1
    assert len(audit["recommendations"]) > 0


def test_parse_document_txt():
    content = "Jane Doe\nSoftware Engineer\nPython, Docker, SQL"
    stream = io.BytesIO(content.encode("utf-8"))
    parsed = parse_document(stream, "resume.txt")
    assert "Jane Doe" in parsed
    assert "Software Engineer" in parsed


def test_similarity_identical_texts():
    matcher = ResumeJobMatcher()
    sample = "Senior Python engineer with AWS, Docker, and FastAPI experience."
    score = matcher.compute_similarity(sample, sample)
    assert score >= 0.99


def test_similarity_disjoint_texts():
    matcher = ResumeJobMatcher()
    t1 = "Pediatric surgeon hospital clinical healthcare patient biology"
    t2 = "Kubernetes Docker terraform microservices backend python devops"
    score = matcher.compute_similarity(t1, t2)
    assert score < 0.20


def test_similarity_empty_inputs():
    matcher = ResumeJobMatcher()
    assert matcher.compute_similarity("", "Python engineer") == 0.0
    assert matcher.compute_similarity("Developer", "") == 0.0
    assert matcher.compute_similarity("", "") == 0.0


def test_predict_structure_and_hybrid_scoring():
    matcher = ResumeJobMatcher()
    results = matcher.predict(SAMPLE_RESUME, SAMPLE_JOB_DESCRIPTION)

    required_keys = [
        "similarity_score",
        "match_percentage",
        "match_level",
        "match_color",
        "verdict",
        "textual_similarity_percentage",
        "skills_overlap_percentage",
        "matched_keywords",
        "missing_keywords",
        "bonus_skills",
        "top_job_keywords",
        "category_breakdown",
        "seniority_fit",
        "ats_audit",
        "optimization_plan",
        "resume_word_count",
        "job_word_count",
    ]
    for key in required_keys:
        assert key in results, f"Missing key in predict results: {key}"

    assert 0.0 <= results["similarity_score"] <= 1.0
    assert 0.0 <= results["match_percentage"] <= 100.0
    assert results["match_level"] in ["High Match", "Moderate Match", "Low Match"]
    assert len(results["matched_keywords"]) > 0
    assert len(results["optimization_plan"]) > 0


def test_simulate_skill_additions():
    matcher = ResumeJobMatcher()
    sim = matcher.simulate_skill_additions(
        SAMPLE_RESUME,
        SAMPLE_JOB_DESCRIPTION,
        ["kubernetes", "kafka", "terraform"]
    )
    assert sim["score_delta"] >= 0.0
    assert "kubernetes" in sim["newly_matched_skills"]


def test_generate_markdown_report():
    matcher = ResumeJobMatcher()
    results = matcher.predict(SAMPLE_RESUME, SAMPLE_JOB_DESCRIPTION)
    report = matcher.generate_markdown_report(results)

    assert "# TalentBridge AI" in report
    assert "Key Performance Indicators" in report
    assert "Technical Competencies Breakdown" in report
    assert "Applicant Tracking System" in report
