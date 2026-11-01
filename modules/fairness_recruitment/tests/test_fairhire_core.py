def test_fairhire_core_imports():
    from modules.fairness_recruitment import fairhire_core
    assert fairhire_core is not None


def test_find_skills():
    from modules.fairness_recruitment.fairhire_core import find_skills

    result = find_skills("Python, SQL and Machine Learning")

    assert "python" in result
    assert "sql" in result
    assert "machine learning" in result


def test_find_skills_alias():
    from modules.fairness_recruitment.fairhire_core import find_skills

    result = find_skills("I know ML and sklearn")

    assert "machine learning" in result
    assert "scikit-learn" in result


def test_parse_resume():
    from modules.fairness_recruitment.fairhire_core import parse_resume

    resume = """
    Alex Morgan
    Age: 25
    Education: Regional Engineering College
    Skills: Python, SQL
    Experience: 2 years
    """

    result = parse_resume(resume, "alex.txt")

    assert result["age"] == 25
    assert "python" in result["skills"]


def test_auditor_detects_simulated_bias():
    from modules.fairness_recruitment import FairnessAuditor

    resumes = [
        ("a.txt", "Rahul Sharma\nAge: 26\nIIT Madras\nSkills: Python, SQL"),
        ("b.txt", "Priya Nair\nAge: 46\nRegional Engineering College\nSkills: Python, SQL, Machine Learning"),
        ("c.txt", "Kavya Rao\nAge: 30\nRegional Engineering College\nSkills: Python"),
    ]
    result = FairnessAuditor(kind="biased", top_n=1).predict(
        {"job_description": "Required: Python, SQL, Machine Learning", "resumes": resumes}
    )

    assert "Gender" in result["flagged"]
    assert "College" in result["flagged"]
    assert len(result["rows"]) == 3
