# Fake Job and Internship Posting Detection Using NLP & ML

**Assigned Leads:** Member 11 (`24B11AI134`) & Member 2 (`24P31A42D0`)  
**Module Identifiers:** `modules.internship_fraud_detection` & `modules.fake_job_detection`  
**Status:** ✅ Production Ready (Unified Engine)

---

## 1. Unified Architecture & Overview
This module unifies **Fake Job Posting Detection** and **Fake Internship Detection** into a single, comprehensive fraud screening and security analysis engine. It protects both job seekers and college student applicants against:
- High-risk employment scams (cashier check cashing, advance equipment fees, money mule schemes).
- Predatory student internship scams (mandatory certificate purchase fees, offer letter processing charges, paid training kit scams, campus ambassador MLM schemes).
- Off-platform recruiter phishing operations (unregulated Telegram / WhatsApp interviews, free webmail impersonators).

---

## 2. Key Capabilities
1. **Live Document & Offer Letter Upload:** Accepts `.pdf`, `.docx`, and `.txt` files to extract text and audit security threat vectors in real time.
2. **Dual-Layer Evaluation:**
   - **Machine Learning Classification:** Logistic Regression pipeline with sublinear TF-IDF (50,000 features, unigram + bigram) trained on verified job records.
   - **Heuristic Threat Audit:** Pattern-matches critical red flags (upfront certificate fees, check cashing, disposable email domains, crypto transfers).
3. **Interactive Security Audit Report:**
   - Composite Authenticity Trust Score (0 – 100)
   - Estimated Fraud Probability
   - Matched Red Flag Snippets with Severity Ratings (`Critical`, `High`, `Medium`)
   - Candidate Safety Action Checklist
   - Downloadable Markdown Audit Summary
4. **Verified Screened Job & Internship Browser:** Searchable historical listings filtered at a 0.5 fraud probability threshold.

---

## 3. Interface Contract
Both modules expose the standard TalentBridge AI `render()` contract:
```python
def render() -> None:
    """Renders the unified Fake Job & Internship Detection workspace."""
```

---

## 4. Verification
Run the dedicated test suite:
```bash
python -m pytest modules/internship_fraud_detection/tests/ -v
```
