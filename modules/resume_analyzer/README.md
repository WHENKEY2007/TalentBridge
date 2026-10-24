# AI Resume Analysis & ATS Readiness

**Assigned Lead:** Member 10  
**Module Identifier:** `modules.resume_analyzer`  
**Status:** ✅ Production ML Module Active  

---

## 1. Module Overview

The **AI Resume Analysis** module provides multi-dimensional natural language processing (NLP) diagnostics and automated Applicant Tracking System (ATS) readiness scoring for candidate resumes.

Operating completely inside `modules/resume_analyzer/` according to team isolation standards, this module extracts structural, linguistic, quantitative, and domain-specific signals from uploaded resumes (PDF, TXT, or markdown) to assess hiring discoverability, formatting health, and role alignment.

---

## 2. Interface Contract

TalentBridge AI dynamically discovers and mounts this module via the standard `render()` contract in [`interface.py`](interface.py):

```python
def render() -> None:
    """
    Renders the interactive AI Resume Analysis interface in Streamlit.
    Provides file uploads, 1-click benchmark presets, multi-dimensional scorecards,
    categorized verb breakdowns, and prioritized recommendations.
    """
```

Programmatic inference is exposed via `ResumeAnalyzer` in [`model.py`](model.py):

```python
from modules.resume_analyzer.model import ResumeAnalyzer

analyzer = ResumeAnalyzer()
result = analyzer.predict({
    "text": "<candidate_resume_text>",
    "industry": "Software & Technology",
    "career_level": "Mid-Level Professional",
})

print(result["overall_ats_score"])  # e.g., 91.5
print(result["tier"])               # "Elite" | "Competitive" | "Developing" | "Needs Work"
print(result["grade"])              # "A+" | "A" | "B" | "C" | "D" | "F"
```

---

## 3. Preprocessing & NLP Feature Pipeline

The preprocessing pipeline in [`preprocessing.py`](preprocessing.py) performs extraction and linguistic evaluation:

1. **Document Ingestion:**
   - In-memory PDF text extraction via `pypdfium2`.
   - UTF-8 and Latin-1 plain text parsing.
2. **Contact & Online Presence Audit:**
   - Detects email, phone, location, LinkedIn profile, GitHub handle, and personal portfolios.
3. **Section Segmentation:**
   - Regex-based boundary extraction isolating: `Contact`, `Summary`, `Experience`, `Education`, `Skills`, `Projects`, `Certifications`, and `Awards`.
4. **Action Verb Strength & Passive Flagging:**
   - Evaluates bullet-point initial verbs against curated power verb taxonomies (`Leadership`, `Execution & Engineering`, `Optimization & Metrics`, `Analysis & Research`, `Collaboration`).
   - Flags passive clichés (`"responsible for"`, `"helped with"`, `"worked on"`, `"duties included"`) and suggests strong proactive alternatives.
5. **Quantifiable Achievement Detection:**
   - Detects measurable business metrics (percentages `%`, dollar values `$`, scale multipliers `10k+`, latency reductions).
6. **Readability & Formatting Metrics:**
   - Flesch Reading Ease score, average sentence length, bullet length distribution, and page count estimation.
7. **20-Dimensional ML Feature Vector:**
   - Generates normalized numeric feature vector `[0.0, 1.0]` for model evaluation.

---

## 4. Dataset Sources & Synthesis

Training and benchmark datasets are maintained in `data/resume_benchmark_data.csv`:

- **Sample Size:** 350 curated resumes across 4 quality tiers (`Elite`, `Competitive`, `Developing`, `Needs Work`).
- **Target Sectors Covered:**
  - Software & Technology
  - Data Science & AI
  - Cloud & DevOps
  - Finance & Banking
  - Healthcare & Biotechnology
  - Product & Marketing
- **Career Level Variations:**
  - Entry-Level / Graduate
  - Mid-Level Professional
  - Senior / Executive Lead
- **Data Preservation:**
  - Large data files are git-ignored via root `.gitignore`, with directory persistence guaranteed by `data/.gitkeep`.

---

## 5. Machine Learning Models & Evaluation Metrics

The module implements a dual-stage ML architecture serialized in `artifacts/resume_analyzer_model.joblib`:

1. **Continuous Score Predictor:** `GradientBoostingRegressor` (120 estimators, learning rate = 0.08, max depth = 4).
2. **Readiness Tier Classifier:** `RandomForestClassifier` (100 estimators, max depth = 6).

### Performance Metrics (Test Set Evaluation)

| Metric | Target | Achieved | Status |
| :--- | :--- | :--- | :--- |
| **R² Score (Score Prediction)** | > 0.85 | **0.9090** | ✅ Exceeded |
| **RMSE (Score Deviation)** | < 8.00 | **6.3198** | ✅ Exceeded |
| **Classification Accuracy** | > 0.90 | **1.0000** | ✅ 100% Stratified Test Accuracy |
| **Macro F1-Score** | > 0.90 | **1.0000** | ✅ Balanced Across All Tiers |
| **Training Split** | 75% / 25% | 262 Train / 88 Test | ✅ Validated |

### Key Feature Importances
- `feat_quantification_ratio` (Quantified business metrics)
- `feat_action_verb_density` (Percentage of bullets starting with strong action verbs)
- `feat_required_sections_ratio` (Completeness of core structural sections)
- `feat_weak_verb_penalty` (Absence of passive phrases)
- `feat_length_compliance` (Page and word count suitability for target level)

---

## 6. Interactive Streamlit Interface Features

1. **⚡ 1-Click Benchmark Presets:** Instantly load calibrated profiles (Entry-Level CS Graduate, Senior Software Architect, Unoptimized Resume).
2. **📤 Flexible Input Modalities:** Upload `.pdf` or `.txt` resumes directly, or paste raw text.
3. **🎯 Hero Diagnostics Card:** Dynamic overall score, letter grade (A+ through F), and assessment tier badge.
4. **📊 Component Deep-Dive:** Sub-scores for Structure, Action Verbs, Quantifiable Impact, Industry Alignment, and Formatting.
5. **💡 Prioritized Recommendations:** Actionable checklist with severity levels (`Critical`, `High`, `Medium`) and concrete rewrite suggestions.

---

## 7. Limitations & Ethical Considerations

- **Decision-Support Scope:** ATS readiness metrics evaluate discoverability and formatting clarity. They are analytical guidelines and do not guarantee interview selections or hiring decisions.
- **Graphic Resume Parsing:** Heavy multi-column layouts, graphic text boxes, or scanned image resumes require OCR prior to plain-text evaluation.
- **Contextual Nuance:** Candidates should adapt keywords naturally according to their authentic experience rather than keyword stuffing.

---

## 8. Development & Testing Commands

To retrain the ML pipeline:
```bash
python -m modules.resume_analyzer.train
```

To run unit tests:
```bash
pytest modules/resume_analyzer/tests/
```

To run complete platform integration tests:
```bash
pytest tests/
```
