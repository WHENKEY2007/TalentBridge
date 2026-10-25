"""
Text preprocessing, document parsing (PDF/DOCX/TXT), skills taxonomy extraction,
synonym normalization, experience analysis, and ATS structural diagnostics.
"""

import io
import re
from typing import Any, BinaryIO, Dict, List, Optional, Set, Tuple, Union
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from .config import (
    ADDITIONAL_STOPWORDS,
    ESSENTIAL_RESUME_SECTIONS,
    SENIORITY_LEVELS,
    SKILL_ALIASES,
    SKILLS_TAXONOMY,
    STRONG_ACTION_VERBS,
)


def parse_document(file_data: Union[BinaryIO, bytes], filename: str) -> str:
    """
    Extracts plain text from uploaded files supporting .pdf, .docx, and .txt.
    """
    if not file_data or not filename:
        return ""

    ext = filename.lower().split(".")[-1]
    raw_bytes = file_data.read() if hasattr(file_data, "read") else file_data

    # Reset stream pointer if it was a file object
    if hasattr(file_data, "seek"):
        file_data.seek(0)

    try:
        if ext == "pdf":
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz
            doc = fitz.open(stream=raw_bytes, filetype="pdf")
            text_pages = [page.get_text() for page in doc]
            return "\n".join(text_pages).strip()

        elif ext in ("docx", "doc"):
            import docx
            doc = docx.Document(io.BytesIO(raw_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            paragraphs.append(cell.text.strip())
            return "\n".join(paragraphs).strip()

        elif ext in ("txt", "md"):
            try:
                return raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return raw_bytes.decode("latin-1", errors="ignore")

        else:
            raise ValueError(f"Unsupported file format: '.{ext}'. Supported formats are: PDF, DOCX, TXT.")

    except Exception as exc:
        raise RuntimeError(f"Error parsing document '{filename}': {str(exc)}") from exc


def clean_text(text: str) -> str:
    """
    Cleans raw text for NLP processing:
    - Lowercase
    - Removes URLs and email addresses
    - Normalizes punctuation, bullet points, and redundant whitespace
    - Preserves technology terms with +, #, and hyphens (e.g. c++, c#, ci/cd)
    """
    if not text or not isinstance(text, str):
        return ""

    cleaned = text.lower()
    cleaned = re.sub(r"https?://\S+|www\.\S+", " ", cleaned)
    cleaned = re.sub(r"\S+@\S+", " ", cleaned)
    cleaned = re.sub(r"[\r\n\t•·|/\\_()\[\]{}:;\"*~`]", " ", cleaned)
    cleaned = re.sub(r"[^a-z0-9+#\-\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _canonicalize_skill(skill_term: str) -> str:
    """Returns canonical skill name if term matches an alias."""
    term = skill_term.strip().lower()
    return SKILL_ALIASES.get(term, term)


def extract_taxonomy_skills(text: str) -> Dict[str, List[str]]:
    """
    Scans input text against the curated technical skills taxonomy,
    performing canonical alias resolution (e.g., 'k8s' -> 'kubernetes', 'postgres' -> 'postgresql').
    Matches both single-token and multi-word phrases.
    Returns skills grouped by domain category.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return {cat: [] for cat in SKILLS_TAXONOMY}

    detected_by_category: Dict[str, Set[str]] = {cat: set() for cat in SKILLS_TAXONOMY}

    # 1. Scan for canonical taxonomy skills
    for category, skill_set in SKILLS_TAXONOMY.items():
        for skill in skill_set:
            escaped_skill = re.escape(skill)
            pattern = rf"(?:\b|\s|^){escaped_skill}(?:\b|\s|$)"
            if re.search(pattern, cleaned):
                canonical = _canonicalize_skill(skill)
                # Place canonical in appropriate category if found
                target_cat = category
                for cat_name, cat_skills in SKILLS_TAXONOMY.items():
                    if canonical in cat_skills:
                        target_cat = cat_name
                        break
                detected_by_category[target_cat].add(canonical)

    # 2. Scan for alias triggers
    for alias, canonical in SKILL_ALIASES.items():
        escaped_alias = re.escape(alias)
        pattern = rf"(?:\b|\s|^){escaped_alias}(?:\b|\s|$)"
        if re.search(pattern, cleaned):
            for cat_name, cat_skills in SKILLS_TAXONOMY.items():
                if canonical in cat_skills:
                    detected_by_category[cat_name].add(canonical)
                    break

    return {cat: sorted(list(skills)) for cat, skills in detected_by_category.items()}


def extract_flat_skills(text: str) -> Set[str]:
    """
    Extracts all taxonomy skills found in text as a flat set of canonical strings.
    """
    categorized = extract_taxonomy_skills(text)
    all_skills: Set[str] = set()
    for skills in categorized.values():
        all_skills.update(skills)
    return all_skills


def extract_experience_years(text: str, is_job_description: bool = False) -> Optional[float]:
    """
    Extracts years of experience mentioned in resume or required in job description.
    Handles '5+ years', '3-5 years', 'at least 4 years', 'minimum of 3 years', etc.
    """
    if not text:
        return None

    lower_text = text.lower()

    # Pattern A: range like '3-5 years' or '3 to 5 years'
    range_matches = re.findall(r"\b(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b", lower_text)
    if range_matches:
        vals = []
        for low, high in range_matches:
            val = float(low) if is_job_description else float(high)
            vals.append(val)
        if vals:
            return min(vals) if is_job_description else max(vals)

    # Pattern B: '5+ years', '5 years of experience', '5+ yrs'
    single_matches = re.findall(
        r"(?:(?:minimum|at least|min|over)\s+)?(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)(?:\s+(?:of\s+)?experience)?",
        lower_text
    )
    if single_matches:
        nums = [float(n) for n in single_matches if 0.5 <= float(n) <= 40.0]
        if nums:
            return min(nums) if is_job_description else max(nums)

    # Fallback pattern: date spans like '2019 - Present' or '2018 - 2023'
    if not is_job_description:
        spans = re.findall(r"\b(20\d{2})\s*(?:-|–|to)\s*(20\d{2}|present|current)\b", lower_text)
        current_year = 2026
        total_span = 0.0
        for start_str, end_str in spans:
            start_yr = int(start_str)
            end_yr = current_year if end_str in ("present", "current") else int(end_str)
            if end_yr >= start_yr:
                total_span += (end_yr - start_yr)
        if total_span > 0:
            return min(total_span, 30.0)

    return None


def detect_seniority_level(text: str, years: Optional[float] = None) -> str:
    """
    Infers seniority level from explicit title keywords and experience duration.
    """
    if not text:
        return "Unspecified"

    lower_text = text.lower()

    # Priority check by explicit titles / keywords
    if any(re.search(rf"\b{re.escape(kw)}\b", lower_text) for kw in ["principal", "staff engineer", "architect", "lead engineer", "tech lead"]):
        return "Lead / Staff / Principal"
    if any(re.search(rf"\b{re.escape(kw)}\b", lower_text) for kw in ["senior", "sr."]):
        return "Senior Engineer"
    if any(re.search(rf"\b{re.escape(kw)}\b", lower_text) for kw in ["intern", "internship", "trainee", "associate"]):
        return "Intern / Entry-Level"
    if any(re.search(rf"\b{re.escape(kw)}\b", lower_text) for kw in ["junior", "jr."]):
        return "Junior Engineer"

    # Fallback to experience years
    if years is not None:
        for level, cfg in SENIORITY_LEVELS.items():
            if cfg["min_years"] <= years <= cfg["max_years"]:
                return level

    return "Mid-Level Engineer"


def evaluate_seniority_fit(resume_text: str, job_text: str) -> Dict[str, Any]:
    """
    Evaluates alignment between candidate experience and role seniority demands.
    Returns quantitative fit score, candidate/job years, and qualitative status.
    """
    cand_years = extract_experience_years(resume_text, is_job_description=False)
    req_years = extract_experience_years(job_text, is_job_description=True)

    cand_level = detect_seniority_level(resume_text, cand_years)
    job_level = detect_seniority_level(job_text, req_years)

    if req_years is None:
        # If job doesn't specify numeric years, evaluate level alignment
        fit_score = 0.90
        status = "Role has open experience requirements"
        badge = "Flexible Fit"
        color = "#22c55e"
    elif cand_years is None:
        fit_score = 0.70
        status = f"Candidate experience duration not explicitly stated (Job requires {req_years:.1f}+ yrs)"
        badge = "Experience Unspecified"
        color = "#f59e0b"
    elif cand_years >= req_years:
        excess = cand_years - req_years
        if excess <= 5.0:
            fit_score = 1.0
            status = f"Candidate meets or exceeds required experience ({cand_years:.1f} yrs vs {req_years:.1f}+ yrs required)"
            badge = "Well Matched"
            color = "#22c55e"
        else:
            fit_score = 0.92
            status = f"Candidate is highly experienced for this role ({cand_years:.1f} yrs vs {req_years:.1f}+ yrs required)"
            badge = "Seniority Premium"
            color = "#3b82f6"
    else:
        deficit = req_years - cand_years
        if deficit <= 1.5:
            fit_score = 0.80
            status = f"Candidate is close to required experience ({cand_years:.1f} yrs vs {req_years:.1f}+ yrs required)"
            badge = "Close Match"
            color = "#f59e0b"
        else:
            fit_score = max(0.40, 1.0 - (deficit * 0.15))
            status = f"Candidate experience is below requirement ({cand_years:.1f} yrs vs {req_years:.1f}+ yrs required)"
            badge = "Experience Gap"
            color = "#ef4444"

    return {
        "candidate_years": cand_years,
        "required_years": req_years,
        "candidate_level": cand_level,
        "job_level": job_level,
        "fit_score": round(fit_score, 2),
        "status": status,
        "badge": badge,
        "color": color,
    }


def find_skill_gap_detailed(resume_text: str, job_text: str) -> Dict[str, Any]:
    """
    Performs comprehensive skill gap analysis between resume and job description.
    Utilizes canonical alias resolution.
    Returns categorized matches, missing items, and coverage ratios.
    """
    resume_categorized = extract_taxonomy_skills(resume_text)
    job_categorized = extract_taxonomy_skills(job_text)

    resume_all = extract_flat_skills(resume_text)
    job_all = extract_flat_skills(job_text)

    matched_skills = sorted(list(job_all.intersection(resume_all)))
    missing_skills = sorted(list(job_all.difference(resume_all)))
    bonus_skills = sorted(list(resume_all.difference(job_all)))

    category_breakdown: Dict[str, Dict[str, Any]] = {}
    for cat in SKILLS_TAXONOMY.keys():
        j_skills = set(job_categorized.get(cat, []))
        r_skills = set(resume_categorized.get(cat, []))
        c_matched = sorted(list(j_skills.intersection(r_skills)))
        c_missing = sorted(list(j_skills.difference(r_skills)))
        coverage = round((len(c_matched) / len(j_skills) * 100), 1) if j_skills else 100.0

        category_breakdown[cat] = {
            "required_count": len(j_skills),
            "matched_count": len(c_matched),
            "coverage_percent": coverage,
            "matched": c_matched,
            "missing": c_missing,
        }

    skills_match_ratio = (len(matched_skills) / len(job_all)) if job_all else 1.0

    return {
        "job_skills": sorted(list(job_all)),
        "resume_skills": sorted(list(resume_all)),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "bonus_skills": bonus_skills,
        "category_breakdown": category_breakdown,
        "skills_match_ratio": skills_match_ratio,
        "skills_match_percentage": round(skills_match_ratio * 100.0, 1),
    }


def audit_resume_structure(resume_text: str) -> Dict[str, Any]:
    """
    Performs ATS format diagnostics:
    - Length & word count assessment
    - Essential section presence checks
    - Action verbs density
    - Quantification & metrics check
    - Actionable recommendations list
    """
    if not resume_text:
        return {
            "word_count": 0,
            "length_status": "Empty",
            "length_color": "#94a3b8",
            "sections_present": [],
            "sections_missing": list(ESSENTIAL_RESUME_SECTIONS.keys()),
            "action_verbs_found": [],
            "action_verb_count": 0,
            "quantification_count": 0,
            "recommendations": ["Please upload or paste your resume to receive an ATS audit."],
        }

    cleaned = clean_text(resume_text)
    words = cleaned.split()
    word_count = len(words)

    # Word count evaluation
    if word_count < 250:
        length_status = "Too Short (< 250 words)"
        length_color = "#ef4444"
    elif word_count <= 850:
        length_status = "Optimal (250 - 850 words)"
        length_color = "#22c55e"
    else:
        length_status = "Long (> 850 words)"
        length_color = "#f59e0b"

    # Section Detection
    lower_raw = resume_text.lower()
    sections_present: List[str] = []
    sections_missing: List[str] = []

    for section_name, keywords in ESSENTIAL_RESUME_SECTIONS.items():
        found = any(re.search(rf"\b{re.escape(kw)}\b", lower_raw) for kw in keywords)
        if found:
            sections_present.append(section_name)
        else:
            sections_missing.append(section_name)

    # Action Verbs Count
    action_verbs_found = sorted(list(STRONG_ACTION_VERBS.intersection(set(words))))

    # Quantification detection (e.g. 50%, $10k, 10x, 5 years, 30+)
    metrics_patterns = re.findall(r"\b\d+[%+xXkKmM]?\b|\$\d+", resume_text)
    quantification_count = len(metrics_patterns)

    # Actionable Recommendations
    recommendations: List[str] = []
    if word_count < 250:
        recommendations.append("Expand on your project deliverables and technical responsibilities to reach at least 300 words.")
    if "Professional Experience" in sections_missing:
        recommendations.append("Ensure your work history is clearly marked under an 'Experience' or 'Work History' header.")
    if "Education" in sections_missing:
        recommendations.append("Add an explicit 'Education' or 'Academic Background' section.")
    if len(action_verbs_found) < 5:
        recommendations.append(
            f"Use more impactful action verbs (found {len(action_verbs_found)}). Begin bullets with verbs like 'Architected', 'Engineered', 'Optimized', or 'Automated'."
        )
    if quantification_count < 3:
        recommendations.append("Quantify your impact with measurable metrics (e.g., 'reduced latency by 40%', 'managed $50k budget', 'led 6 engineers').")

    if not recommendations:
        recommendations.append("Resume demonstrates strong ATS structure, clear headers, high action-verb density, and quantifiable impact!")

    return {
        "word_count": word_count,
        "length_status": length_status,
        "length_color": length_color,
        "sections_present": sections_present,
        "sections_missing": sections_missing,
        "action_verbs_found": action_verbs_found,
        "action_verb_count": len(action_verbs_found),
        "quantification_count": quantification_count,
        "recommendations": recommendations,
    }


def extract_keywords(text: str, top_n: int = 35) -> List[str]:
    """Extracts general vocabulary keywords."""
    cleaned = clean_text(text)
    if not cleaned:
        return []
    tokens = cleaned.split()
    all_stopwords = set(ENGLISH_STOP_WORDS).union(ADDITIONAL_STOPWORDS)
    filtered = [t for t in tokens if len(t) >= 3 and t not in all_stopwords and not t.isdigit()]
    freq: Dict[str, int] = {}
    for t in filtered:
        freq[t] = freq.get(t, 0) + 1
    return sorted(freq.keys(), key=lambda k: freq[k], reverse=True)[:top_n]


def find_skill_gap(resume_text: str, job_text: str, top_n_keywords: int = 30) -> Dict[str, List[str]]:
    """Legacy helper maintained for backward compatibility."""
    detailed = find_skill_gap_detailed(resume_text, job_text)
    return {
        "job_keywords": detailed["job_skills"][:top_n_keywords],
        "matched_keywords": detailed["matched_skills"],
        "missing_keywords": detailed["missing_skills"],
    }
