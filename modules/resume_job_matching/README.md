# Module 1: Resume–Job Matching Engine

**Assigned Lead:** Member 1 (Lead Architect)  
**Status:** ✅ Production Hybrid Engine Implemented & Verified  
**Package:** `modules.resume_job_matching`  
**Test Suite:** 17/17 Unit Tests Passing (36/36 Platform Tests Passing)

---

## 1. Overview & Objective

The **Resume–Job Matching Engine** provides multi-dimensional candidate-to-job compatibility analysis. It accepts multi-format resume documents (**PDF, DOCX, TXT**), evaluates domain skills taxonomy coverage across 6 technical disciplines with canonical synonym normalization, computes vocabulary overlap using TF-IDF and Cosine distance, assesses quantitative experience/seniority alignment, and delivers an Applicant Tracking System (ATS) structural audit with real-time what-if simulations and downloadable reports.

---

## 2. Machine Learning & NLP Architecture

### A. Document Parsing Pipeline (`preprocessing.py`)
- **PDF Extraction:** Uses `PyMuPDF` (`fitz`) to extract text streams across all document pages.
- **DOCX Extraction:** Parses paragraph runs and table cell matrices using `python-docx`.
- **Text Normalization:** Lowercasing, URL/email stripping, punctuation normalization while preserving domain tokens (`c++`, `c#`, `ci/cd`, `rest api`).

### B. Curated Skills Taxonomy & Synonym Canonicalization
Scans resumes and job descriptions against categorized technical competencies:
1. **Programming Languages:** Python, Java, C++, C#, JavaScript, TypeScript, Go, Rust, SQL, Bash, HTML, CSS, etc.
2. **Frameworks & Web:** FastAPI, Django, Flask, React, Next.js, Node.js, Spring Boot, GraphQL, REST API, Tailwind, etc.
3. **Cloud & DevOps:** AWS, Azure, GCP, Docker, Kubernetes, Terraform, CI/CD, GitHub Actions, Helm, Linux, Ansible, etc.
4. **Databases & Storage:** PostgreSQL, MySQL, MongoDB, Redis, Cassandra, Elasticsearch, DynamoDB, Snowflake, BigQuery, etc.
5. **Data & AI/ML:** PyTorch, TensorFlow, Scikit-learn, Pandas, NumPy, NLP, LLMs, Computer Vision, Spark, Airflow, etc.
6. **Architecture & Methods:** Microservices, System Design, Distributed Systems, Agile, Scrum, JIRA, TDD, OOP, Kafka, etc.

**Synonym Aliases:** Automatically resolves variations such as `k8s` ➔ `kubernetes`, `postgres` / `psql` ➔ `postgresql`, `golang` ➔ `go`, `react.js` ➔ `react`, `ci cd` ➔ `ci/cd`, `sklearn` ➔ `scikit-learn`, and `aws` ➔ `amazon web services`.

### C. Quantitative Experience & Seniority Fit
- **Experience Extraction:** Parses tenure numbers (e.g., `5+ years`, `3-5 years`, `2020 - Present`).
- **Seniority Classification:** Identifies candidate and role seniority (`Intern / Entry-Level`, `Junior`, `Mid-Level`, `Senior`, `Lead / Staff / Principal`).
- **Fit Evaluation:** Determines alignment status (`Well Matched`, `Seniority Premium`, `Close Match`, or `Experience Gap`).

### D. Hybrid Composite Scoring Formulation (`model.py`)
Rather than relying purely on bag-of-words or uncalibrated word frequencies, the engine uses a balanced composite metric:

$$\text{Composite Match Score} = (0.50 \times S_{\text{skills}}) + (0.35 \times S_{\text{textual}}) + (0.15 \times S_{\text{experience}})$$

Where:
- **$S_{\text{skills}}$ (Skills Coverage Ratio):**
  $$S_{\text{skills}} = \frac{|\text{Skills}_{\text{Job}} \cap \text{Skills}_{\text{Resume}}|}{|\text{Skills}_{\text{Job}}|}$$
- **$S_{\text{textual}}$ (Cosine Distance in TF-IDF Space):**
  $$S_{\text{textual}} = \frac{\mathbf{v}_{\text{resume}} \cdot \mathbf{v}_{\text{job}}}{\|\mathbf{v}_{\text{resume}}\|_2 \|\mathbf{v}_{\text{job}}\|_2}$$
- **$S_{\text{experience}}$ (Seniority Alignment Score):**
  Quantitative ratio comparing candidate's verified tenure against required role experience.

### E. Classification Tiers
- **High Match:** $\ge 75\%$
- **Moderate Match:** $45\% - 74\%$
- **Low Match:** $< 45\%$

### F. ATS Structural & Impact Audit
- **Length Analysis:** Assesses optimal word counts (250–850 words).
- **Section Verification:** Verifies standard headers (*Contact Info, Experience, Education, Skills, Projects*).
- **Action Verb Density:** Identifies power verbs (*Architected, Engineered, Optimized, Automated*).
- **Quantification Metric:** Detects numerical achievements, percentages, and scale indicators.
- **Action Plan:** Automatically generates numbered recommendations for candidates.

### G. Interactive What-If Simulator & Report Export
- **Simulator:** Real-time calculation of projected score jumps when adding missing technical skills.
- **Report Download:** Generates and exports comprehensive diagnostic summaries as `talentbridge_matching_report.md`.

---

## 3. Inputs & Outputs Contract

### Expected Inputs
- **Resume:** Uploaded file (`.pdf`, `.docx`, `.txt`) or pasted plain text.
- **Job Description:** Selected preset (6 engineering roles) or pasted job posting.

### Expected Outputs
- `match_percentage`: Weighted composite alignment percentage.
- `skills_overlap_percentage`: Domain technical skills coverage.
- `textual_similarity_percentage`: TF-IDF vocabulary similarity.
- `seniority_fit`: Candidate years vs. required years and fit tier.
- `category_breakdown`: Category-by-category skill matrix with visual progress meters.
- `matched_keywords` & `missing_keywords`: Specific competencies found and missing.
- `ats_audit`: Structural health metrics and section status.
- `optimization_plan`: Prioritized action items to boost match rate.

---

## 4. Ethical AI & Critical Disclaimer

> ⚠️ **NOTICE: Text-similarity is NOT a hiring guarantee or employment probability.**
> Machine learning similarity scores evaluate textual and competency overlap with a specific job posting. Real-world talent evaluation necessitates holistic human assessment of problem solving, cultural contribution, interpersonal communication, and live code reviews.

---

## 5. File Layout

```
modules/resume_job_matching/
├── __init__.py           # Exports public API and render()
├── config.py             # Hyperparameters, skills taxonomy, aliases, and presets
├── preprocessing.py      # PDF/DOCX parsing, alias resolution, experience extraction, ATS audit
├── model.py              # Hybrid ResumeJobMatcher implementation with simulation & report export
├── train.py              # Vectorizer training on 21 multi-domain technical profiles
├── interface.py          # Interactive Streamlit UI with file upload, simulator, and download button
├── README.md             # This technical document
├── data/
│   └── .gitkeep          # Training data folder
├── artifacts/
│   ├── .gitkeep          # Checkpoints folder
│   └── tfidf_vectorizer.joblib  # Serialized 6,000-feature vectorizer
└── tests/
    └── test_resume_job_matching.py  # Comprehensive unit test suite (17 tests)
```

---

## 6. Testing & Running

### Run Unit Tests
```bash
python -m pytest modules/resume_job_matching/tests/ -v
```

### Run Platform Integration Check
```bash
python -m pytest -v
```

### Launch the Application
```bash
python -m streamlit run app.py
```
*(Select **Resume–Job Matching** from the dashboard cards)*.
