# 🌉 TalentBridge AI — Integrated Machine Learning Platform

> A modular, integrated machine learning and talent intelligence platform unifying predictive analytics, NLP, and career recommendation systems into a single enterprise-ready application.

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![ML Library](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg)](https://scikit-learn.org/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg)](https://github.com/WHENKEY2007/TalentBridge/actions)
[![Test Suite](https://img.shields.io/badge/Tests-47%20Passing-brightgreen.svg)](https://pytest.org/)

---

## 1. Project Overview & Mission

**TalentBridge AI** integrates 7 distinct machine learning applications across the talent acquisition, student academic development, and workforce retention lifecycles. 

The platform is designed around **strict modular architecture** allowing 8 student developers to build, train, evaluate, and test their machine learning models independently in isolation, without blocking each other or causing git merge conflicts.

---

## 2. Team Member Assignments & Use Case Matrix

| # | Module Directory | Use Case Name | Assigned Student Lead | Current Status | Notes |
|---|------------------|---------------|-----------------------|----------------|-------|
| 1 | `modules/resume_job_matching/` | **Resume–Job Matching** | **24B11AI304 (Lead)** | ✅ **Production Ready** | Production TF-IDF + Taxonomy matcher, 17 unit tests passing |
| 2 | `modules/fake_job_detection/` | **Fake Job & Internship Posting Detection** | **24B11AI134 & 24P31A42D0** | ✅ **Production Ready** | Single unified module covering job & internship fraud |
| 3 | `modules/student_performance/` | **Student Performance Prediction** | **24B11AI070** | ✅ **Production Ready** | Production dual-pipeline (GPA regressor + risk classifier), 7 unit tests passing |
| 4 | `modules/entrance_exam_prediction/` | Student Performance on Entrance Examination | 24P31A4255 | 🚧 In Development | Scaffold in platform |
| 5 | `modules/fairness_recruitment/` | **Fairness-Aware AI Recruitment** | **24B11AI159** | ✅ **Production Ready** | FairHire counterfactual bias auditor + fair re-ranking, 5 unit tests passing |
| 6 | `modules/employee_attrition/` | Employee Attrition Prediction | 24B11AI446 | 🚧 In Development | Scaffold only (Workplace retention forecasting) |
| 7 | `modules/resume_analyzer/` | **AI Resume Analyzer** | **24B11AI109** | ✅ **Production Ready** | Production GradientBoosting scorer + ATS audit, 13 unit tests passing |

---

## 3. UI/UX Architecture: Full-Width Portal Layout

The user interface uses a modern **card-based portal architecture** designed for high clarity and zero clutter:
- **No Left Sidebar Clutter:** The default Streamlit sidebar is completely collapsed and hidden, dedicating 100% of the screen width to the active dashboard or module.
- **Interactive Flashcards:** The home page features a clean 3-column grid displaying all 7 modules with category tags, status badges, descriptions, and 1-click launch buttons.
- **Breadcrumb Navigation:** Inside any active module, a top-level `← Back to Dashboard` navigation bar enables seamless return to the portal.

---

## 4. Project Directory Structure

```
TalentBridge-AI/
├── app.py                     # Central Streamlit entry point & lazy module loader
├── requirements.txt           # Core project dependencies
├── README.md                  # Root architectural & team collaboration documentation
├── CONTRIBUTING.md            # Contribution guidelines for team members
├── .gitignore                 # Excludes models, venv, datasets, caches, IDE files
├── .github/
│   ├── CODEOWNERS             # Enforces code ownership per module
│   ├── pull_request_template.md # PR checklist and guidelines
│   └── workflows/
│       └── ci.yml             # Automated CI workflow running pytest on PRs
├── modules/
│   ├── __init__.py            # Root modules package
│   ├── resume_job_matching/   # [24B11AI304] Production Hybrid Matching Engine
│   │   ├── __init__.py, interface.py, model.py, preprocessing.py, train.py, config.py, README.md
│   │   ├── artifacts/tfidf_vectorizer.joblib
│   │   └── tests/test_resume_job_matching.py # 17 unit tests
│   │
│   ├── fake_job_detection/    # [24B11AI134 & 24P31A42D0] Production Fraud Scanner (Unified)
│   │   ├── __init__.py, interface.py, model.py, analyzer.py, README.md
│   │   ├── data/fake_job_postings.csv
│   │   ├── artifacts/fake_job_model.joblib
│   │   └── tests/test_fake_job_detection.py # 4 unit tests
│   │
│   ├── student_performance/   # [24B11AI070] Production Dual-Pipeline Engine
│   │   ├── __init__.py, interface.py, model.py, config.py, README.md
│   │   ├── artifacts/student_performance_model.joblib
│   │   └── tests/test_student_performance.py # 7 unit tests
│   │
│   ├── entrance_exam_prediction/ # [24P31A4255] In Development
│   │   ├── __init__.py, interface.py, model.py, README.md
│   │   └── tests/
│   │
│   ├── fairness_recruitment/  # [24B11AI159] Production FairHire Bias Auditor
│   │   ├── __init__.py, interface.py, model.py, fairhire_core.py, fairhire_ui.py, README.md
│   │   ├── data/ananya_iyer.txt, data/sample_jd.txt
│   │   └── tests/test_fairhire_core.py # 5 unit tests
│   │
│   ├── employee_attrition/    # [24B11AI446] In Development
│   │   ├── __init__.py, interface.py, model.py, README.md
│   │   └── tests/
│   │
│   └── resume_analyzer/       # [24B11AI109] Production Resume Analyzer
│       ├── __init__.py, interface.py, model.py, preprocessing.py, config.py, train.py, README.md
│       ├── artifacts/resume_analyzer_model.joblib
│       └── tests/test_resume_analyzer.py # 13 unit tests
│
├── shared/
│   ├── __init__.py            # Shared utility exports
│   └── utils.py               # Design tokens, headers, disclaimers, safe_html helper
├── tests/
│   └── test_module_integration.py # Platform architecture & contract verification
└── data/
    └── .gitkeep               # Root shared data directory (optional)
```

---

## 5. Getting Started & Installation

### Prerequisites
- Python 3.10+ (tested through 3.14)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/WHENKEY2007/TalentBridge.git
cd TalentBridge
```

### 2. Create and Activate a Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 6. Running the Test Suite

Run all unit and integration tests across the platform (currently **47 passing tests**):
```bash
python -m pytest tests modules/resume_job_matching/tests modules/resume_analyzer/tests modules/fake_job_detection/tests modules/student_performance/tests -v
```

---

## 7. Module Interface Contract

Every team member must adhere to the **`render()` contract** in `modules/<your_module>/interface.py`:

```python
"""
File: modules/<your_module_name>/interface.py
"""

def render() -> None:
    """
    Entry point invoked dynamically by app.py when the user clicks this module's card.
    Renders Streamlit controls, processes input, and presents model predictions.
    """
    pass
```

### Lazy Loading Architecture
To maintain fast application startup, `app.py` **does not load model weights into memory at boot**. When a user selects a module, `app.py` dynamically imports `modules.<your_module>.interface` and invokes `render()`.

If an unhandled exception occurs inside a module, `app.py` catches it gracefully and presents diagnostic information without crashing the entire platform.

---

## 8. Git Governance & Team Contribution Rules

- **Branch Naming:** `feature/member-<N>-<module_name>` (e.g. `feature/member-2-fake-job-detection`)
- **Strict Isolation:** Only modify files inside `modules/<your_assigned_module>/`. Do not touch other members' directories.
- **Continuous Integration:** Every PR automatically runs `.github/workflows/ci.yml` via GitHub Actions, validating formatting, contracts, and unit tests.
- **Code Ownership:** Enforced automatically via `.github/CODEOWNERS`.

---

## 9. Ethical AI & Responsible Machine Learning

All predictive components within TalentBridge AI adhere to ethical AI guidelines:
1. **Decision Support:** ML similarity scores and classifications are analytical guidance tools, **not** hiring guarantees.
2. **Explainability:** Always provide interpretable factors (e.g., skill breakdowns, match tiers, actionable recommendations).
3. **Disclaimers:** Every module includes mandatory ethical AI guidance rendered via `shared.utils.render_disclaimer()`.
