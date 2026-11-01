# Fairness-Aware AI Recruitment (FairHire)

**Assigned Lead:** 24B11AI159  
**Module Identifier:** `modules.fairness_recruitment`  
**Status:** ✅ Production Ready  

---

## 1. Module Overview
FairHire reads candidate resumes and a job description, shortlists candidates, and checks whether the
scoring model is biased. It tests **gender, college, age and career gap one at a time**, removes the effect
of any factor that changes scores, re-ranks the candidates fairly, and explains every Selected / Rejected decision.

---

## 2. How It Works
1. **Read resumes** – extracts name, college, age, career gap, years of experience and skills from PDF / DOCX / TXT.
2. **Match to the job** – required skills are taken from the job description; the base score rewards matched skills and experience.
3. **Detect bias** – for each factor, only that one factor of one candidate is changed (e.g. Rahul ↔ Priya, IIT Madras ↔ Regional Engineering College, age 28 ↔ 45, gap 0 ↔ 2 years) and the candidate is re-scored. A factor whose average score change is above the threshold is flagged.
4. **Fair re-rank** – the measured effect of every flagged factor is subtracted from each candidate's score.
5. **Explain** – each candidate gets a reason: skills matched and missing, experience, and any bias that was corrected.

### Scoring models
- **Skills match (no bias)** – baseline; the bias test should find nothing.
- **Simulated biased model (demo)** – adds deliberate bias to show detection and correction.
- **LLM (Gemini / OpenAI)** – audits a real LLM scorer with your own API key.

---

## 3. Interface Contract
The platform loads the module through `render()` in `interface.py`, which runs the Streamlit UI in `fairhire_ui.py`.

Programmatic use:

```python
from modules.fairness_recruitment import FairnessAuditor

result = FairnessAuditor(kind="biased", top_n=2).predict({
    "job_description": "Required: Python, Machine Learning, SQL",
    "resumes": [("a.txt", resume_text_a), ("b.txt", resume_text_b), ("c.txt", resume_text_c)],
})
result["flagged"]   # factors found to be biased
result["rows"]      # fair score, fair rank, decision and reason per candidate
```

---

## 4. Directory Structure
```
modules/fairness_recruitment/
├── __init__.py          # Exports render() and FairnessAuditor
├── interface.py         # Platform render() contract
├── fairhire_ui.py       # Streamlit UI
├── fairhire_core.py     # Resume parsing, scoring, bias testing, fair re-ranking, explanations
├── model.py             # FairnessAuditor wrapper around fairhire_core
├── README.md            # This documentation
├── data/
│   ├── ananya_iyer.txt  # Sample resume
│   └── sample_jd.txt    # Sample job description
├── artifacts/           # No trained artifacts needed (rule-based pipeline)
└── tests/
    └── test_fairhire_core.py   # 5 unit tests
```

---

## 5. Running
From the project root:

```bash
streamlit run app.py
```

Open **Fairness-Aware AI Recruitment** from the dashboard, upload at least 2 resumes, give a job description, and click **Select candidates**.

Tests:

```bash
pytest modules/fairness_recruitment
```
