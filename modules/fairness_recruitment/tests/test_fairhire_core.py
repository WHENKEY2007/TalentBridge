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
