# 🌉 TalentBridge AI — Integrated Machine Learning Platform

> A modular, 12-member machine learning and talent intelligence platform unifying predictive analytics, NLP, and career recommendation systems into a single enterprise-ready application.

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![ML Library](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg)](https://scikit-learn.org/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg)](https://github.com/WHENKEY2007/TalentBridge/actions)
[![Test Suite](https://img.shields.io/badge/Tests-36%20Passing-brightgreen.svg)](https://pytest.org/)

---

## 1. Project Overview & Mission

**TalentBridge AI** integrates 12 distinct machine learning applications across the talent acquisition, student career development, and workforce retention lifecycles. 

The platform is designed around **strict modular architecture** allowing 12 developers to build, train, evaluate, and test their machine learning models independently in isolation, without blocking each other or causing git merge conflicts.

---

## 2. Team Member Assignments & Use Case Matrix

| # | Module Directory | Use Case Name | Assigned Lead | Current Status |
|---|------------------|---------------|---------------|----------------|
| 1 | `modules/resume_job_matching/` | **Resume–Job Matching** | **Member 1 (Lead)** | ✅ **Production Hybrid Engine (Completed & Verified)** |
| 2 | `modules/fake_job_detection/` | Fake Job Posting Detection | Member 2 | 🚧 In Development (Scaffold Ready) |
| 3 | `modules/student_performance/` | Student Performance Prediction | Member 3 | 🚧 In Development (Scaffold Ready) |
| 4 | `modules/entrance_exam_prediction/` | Entrance Examination Performance Prediction | Member 4 | 🚧 In Development (Scaffold Ready) |
| 5 | `modules/placement_risk/` | Student Placement Risk Prediction | Member 5 | 🚧 In Development (Scaffold Ready) |
| 6 | `modules/interview_analyzer/` | AI Interview Performance Analysis & Feedback | Member 6 | 🚧 In Development (Scaffold Ready) |
| 7 | `modules/learning_difficulty/` | Personalized Learning Difficulty Detection | Member 7 | 🚧 In Development (Scaffold Ready) |
| 8 | `modules/fairness_recruitment/` | Fairness-Aware Recruitment | Member 8 | 🚧 In Development (Scaffold Ready) |
| 9 | `modules/employee_attrition/` | Employee Attrition Prediction | Member 9 | 🚧 In Development (Scaffold Ready) |
| 10 | `modules/resume_analyzer/` | **AI Resume Analysis** | **Member 10** | ✅ **Production Ready (PR #1 Merged)** |
| 11 | `modules/internship_fraud_detection/` | Fake Internship Detection | Member 11 | 🚧 In Development (Scaffold Ready) |
| 12 | `modules/personalized_learning/` | Personalized Learning Recommendations | Member 12 | 🚧 In Development (Scaffold Ready) |

---

## 3. UI/UX Architecture: Full-Width Portal Layout

The user interface uses a modern **card-based portal architecture** designed for high clarity and zero clutter:
- **No Left Sidebar Clutter:** The default Streamlit sidebar is completely collapsed and hidden, dedicating 100% of the screen width to the active dashboard or module.
- **Interactive Flashcards:** The home page features a clean 3-column grid displaying all 12 modules with category tags, status badges, descriptions, and 1-click launch buttons.
- **Breadcrumb Navigation:** Inside any active module, a top-level `← Back to Dashboard` navigation bar enables seamless return to the portal.

---

## 4. Project Directory Structure

```
TalentBridge-AI/
├── app.py                     # Central Streamlit entry point & lazy module loader
├── requirements.txt           # Core project dependencies
├── README.md                  # Root architectural & team collaboration documentation
├── CONTRIBUTING.md            # Contribution guidelines for all 12 team members
├── .gitignore                 # Excludes models, venv, datasets, caches, IDE files
├── .github/
│   ├── CODEOWNERS             # Enforces code ownership per module
│   ├── pull_request_template.md # PR checklist and guidelines
│   └── workflows/
│       └── ci.yml             # Automated CI workflow running pytest on PRs
├── modules/
│   ├── __init__.py            # Root modules package
│   ├── resume_job_matching/   # [MEMBER 1] Production Hybrid Matching Engine
│   │   ├── __init__.py        # Exports interface and matcher
│   │   ├── interface.py       # Streamlit UI with file upload, simulator, and reports
│   │   ├── model.py           # Hybrid NLP & Taxonomy matching engine
│   │   ├── preprocessing.py   # Multi-format parsing, alias normalization, ATS audit
│   │   ├── train.py           # Multi-domain vectorizer training
│   │   ├── config.py          # Curated taxonomies, aliases, presets, thresholds
│   │   ├── README.md          # Member 1 technical specifications
│   │   ├── data/              # Datasets folder (git-tracked via .gitkeep)
│   │   ├── artifacts/
│   │   │   └── tfidf_vectorizer.joblib  # Serialized 6,000-feature vectorizer
│   │   └── tests/
│   │       └── test_resume_job_matching.py # 17 unit tests
│   │
│   ├── resume_analyzer/       # [MEMBER 10] Production Resume Analyzer
│   │   ├── __init__.py, interface.py, model.py, preprocessing.py, config.py
│   │   ├── artifacts/resume_analyzer_model.joblib
│   │   └── tests/test_resume_analyzer.py # 13 unit tests
│   │
│   ├── fake_job_detection/          # [MEMBER 2]  (Scaffold Ready)
│   ├── student_performance/         # [MEMBER 3]  (Scaffold Ready)
│   ├── entrance_exam_prediction/    # [MEMBER 4]  (Scaffold Ready)
│   ├── placement_risk/              # [MEMBER 5]  (Scaffold Ready)
│   ├── interview_analyzer/          # [MEMBER 6]  (Scaffold Ready)
│   ├── learning_difficulty/         # [MEMBER 7]  (Scaffold Ready)
│   ├── fairness_recruitment/        # [MEMBER 8]  (Scaffold Ready)
│   ├── employee_attrition/          # [MEMBER 9]  (Scaffold Ready)
│   ├── internship_fraud_detection/  # [MEMBER 11] (Scaffold Ready)
│   └── personalized_learning/       # [MEMBER 12] (Scaffold Ready)
│
├── shared/
│   ├── __init__.py            # Shared utility exports
│   └── utils.py               # Design tokens, headers, disclaimers, extension filters
├── tests/
│   └── test_module_integration.py # 6 platform integration tests
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

Run all unit and integration tests across the platform (currently **36 passing tests**):
```bash
python -m pytest -v
```

To run tests for a specific module:
```bash
# Member 1: Resume–Job Matching
python -m pytest modules/resume_job_matching/tests/ -v

# Member 10: Resume Analyzer
python -m pytest modules/resume_analyzer/tests/ -v

# Platform Architecture & Contract Verification
python -m pytest tests/test_module_integration.py -v
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
