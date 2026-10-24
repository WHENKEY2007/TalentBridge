"""
Preprocessing and NLP Feature Extraction Pipeline for Resume Analysis.
Assigned to Member 10.
"""

import io
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from .config import (
    ACTION_VERBS,
    ALL_ACTION_VERBS,
    CAREER_LEVEL_BENCHMARKS,
    INDUSTRY_TAXONOMY,
    SECTION_PATTERNS,
    WEAK_PATTERNS,
)


def clean_text(text: Optional[str]) -> str:
    """Standardizes whitespace, normalizes bullet points, and cleans input text."""
    if not text:
        return ""
    # Normalize unicode bullets and dashes
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25AB]", "\n- ", cleaned)
    cleaned = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2015]", "-", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    return cleaned.strip()


def parse_document(file_bytes_or_str: Any, filename: Optional[str] = None) -> str:
    """
    Parses plain text, bytes, or PDF streams into clean resume text.
    Uses pypdfium2 if PDF bytes are provided, with robust error fallback.
    """
    if isinstance(file_bytes_or_str, str):
        return clean_text(file_bytes_or_str)

    if isinstance(file_bytes_or_str, (bytes, bytearray)):
        name = (filename or "").lower()
        if name.endswith(".pdf") or file_bytes_or_str.startswith(b"%PDF"):
            try:
                import pypdfium2 as pdfium
                pdf = pdfium.PdfDocument(file_bytes_or_str)
                extracted_pages: List[str] = []
                for page_idx in range(len(pdf)):
                    page = pdf[page_idx]
                    textpage = page.get_textpage()
                    extracted_pages.append(textpage.get_text_range())
                return clean_text("\n\n".join(extracted_pages))
            except Exception as e:
                # Fallback to UTF-8 / latin-1 decoding
                return clean_text(file_bytes_or_str.decode("utf-8", errors="ignore"))
        try:
            return clean_text(file_bytes_or_str.decode("utf-8"))
        except UnicodeDecodeError:
            return clean_text(file_bytes_or_str.decode("latin-1", errors="ignore"))

    if hasattr(file_bytes_or_str, "read"):
        content = file_bytes_or_str.read()
        return parse_document(content, filename=getattr(file_bytes_or_str, "name", filename))

    return ""


def extract_contact_info(text: str) -> Dict[str, Any]:
    """Extracts email, phone, LinkedIn, GitHub, and portfolio URLs."""
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    phone_match = re.search(
        r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text
    )
    linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+", text, re.IGNORECASE)
    github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[\w-]+", text, re.IGNORECASE)

    # General portfolio / website detection (excluding linkedin & github)
    url_matches = re.findall(
        r"https?://(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?", text
    )
    portfolio = None
    for url in url_matches:
        if "linkedin.com" not in url and "github.com" not in url:
            portfolio = url
            break

    # Location heuristic (e.g. "City, ST" or "City, Country")
    loc_match = re.search(
        r"\b([A-Z][a-zA-Z\s]+,\s*(?:[A-Z]{2}|[A-Z][a-zA-Z\s]+))\b", text[:400]
    )

    detected = {
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "linkedin": linkedin_match.group(0) if linkedin_match else None,
        "github": github_match.group(0) if github_match else None,
        "portfolio": portfolio,
        "location": loc_match.group(1).strip() if loc_match else None,
    }

    # Count how many critical contact elements are present
    completeness_score = sum(
        1 for k, v in detected.items() if v and k in ("email", "phone", "linkedin")
    ) / 3.0

    return {
        "fields": detected,
        "completeness_score": round(completeness_score * 100.0, 1),
        "has_email": detected["email"] is not None,
        "has_phone": detected["phone"] is not None,
        "has_linkedin": detected["linkedin"] is not None,
        "has_github": detected["github"] is not None,
    }


def segment_sections(text: str) -> Dict[str, Dict[str, Any]]:
    """
    Identifies resume sections and extracts their segmented text.
    Returns status, content, and character count for each section.
    """
    lines = text.split("\n")
    found_headers: List[Tuple[str, int, str]] = []  # (section_key, line_idx, matched_title)

    for idx, line in enumerate(lines):
        clean_line = line.strip().lower()
        if not clean_line or len(clean_line) > 55:
            continue

        for section_key, patterns in SECTION_PATTERNS.items():
            for pat in patterns:
                # Match line that looks like a header (e.g. standalone, capitalized, or with colon)
                if re.fullmatch(pat, clean_line) or re.match(rf"^{pat}\s*[:\-]?$", clean_line):
                    found_headers.append((section_key, idx, line.strip()))
                    break

    # Deduplicate keeping earliest line per section
    sections_result: Dict[str, Dict[str, Any]] = {
        sec: {"found": False, "title": None, "content": "", "word_count": 0}
        for sec in SECTION_PATTERNS.keys()
    }

    # Sort found headers by line index
    found_headers.sort(key=lambda x: x[1])

    for i, (sec_key, line_idx, title) in enumerate(found_headers):
        if sections_result[sec_key]["found"]:
            continue  # Already captured primary instance
        start_line = line_idx + 1
        end_line = found_headers[i + 1][1] if i + 1 < len(found_headers) else len(lines)
        sec_content = "\n".join(lines[start_line:end_line]).strip()

        sections_result[sec_key] = {
            "found": True,
            "title": title,
            "content": sec_content,
            "word_count": len(sec_content.split()),
        }

    return sections_result


def extract_bullet_points(text: str) -> List[str]:
    """Extracts individual experience and project bullet points."""
    lines = text.split("\n")
    bullets: List[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Check standard bullet markers
        match = re.match(r"^[-*•▪–\d+\.]\s*(.+)$", stripped)
        if match:
            item = match.group(1).strip()
            if len(item.split()) >= 3:
                bullets.append(item)
        elif len(stripped.split()) >= 5 and any(
            stripped.lower().startswith(v) for v in ALL_ACTION_VERBS
        ):
            bullets.append(stripped)

    return bullets


def analyze_action_verbs(text: str, bullets: List[str]) -> Dict[str, Any]:
    """
    Evaluates usage of strong high-impact action verbs and flags weak passive phrases.
    """
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    words_set = set(words)

    # Tally strong action verbs by category
    categorized_hits: Dict[str, List[str]] = {}
    total_strong_hits = 0

    for category, verb_set in ACTION_VERBS.items():
        found = sorted(list(verb_set.intersection(words_set)))
        categorized_hits[category] = found
        total_strong_hits += len(found)

    # Bullet starting verb analysis
    bullets_starting_with_action_verb = 0
    for b in bullets:
        first_word = re.findall(r"\b[a-zA-Z]+\b", b.lower())
        if first_word and first_word[0] in ALL_ACTION_VERBS:
            bullets_starting_with_action_verb += 1

    bullet_count = max(len(bullets), 1)
    action_verb_density = round((bullets_starting_with_action_verb / bullet_count) * 100.0, 1)

    # Detect weak/passive phrases
    weak_found: List[str] = []
    text_lower = text.lower()
    for pat in WEAK_PATTERNS:
        matches = re.findall(pat, text_lower)
        if matches:
            weak_found.extend(matches)

    # Recommended replacements for weak verbs
    replacements = {
        "responsible for": ["spearheaded", "orchestrated", "engineered", "governed"],
        "helped with": ["accelerated", "collaborated on", "facilitated", "optimized"],
        "worked on": ["architected", "developed", "deployed", "implemented"],
        "duties included": ["directed", "streamlined", "managed", "executed"],
        "assisted in": ["partnered in", "co-engineered", "amplified", "facilitated"],
        "handled": ["resolved", "coordinated", "administered", "dispatched"],
        "hard-working": ["results-driven", "disciplined", "high-velocity"],
        "team player": ["cross-functional collaborator", "aligned team partner"],
    }

    weak_advice: List[Dict[str, Any]] = []
    for wf in set(weak_found):
        suggestion = replacements.get(wf, ["engineered", "led", "optimized"])
        weak_advice.append({
            "weak_phrase": wf,
            "alternatives": suggestion,
        })

    return {
        "categorized_verbs": categorized_hits,
        "total_unique_action_verbs": total_strong_hits,
        "bullets_starting_with_action": bullets_starting_with_action_verb,
        "total_bullets_analyzed": len(bullets),
        "action_verb_density_pct": action_verb_density,
        "weak_phrases_detected": weak_found,
        "weak_count": len(weak_found),
        "improvement_advice": weak_advice,
    }


def analyze_quantification(bullets: List[str]) -> Dict[str, Any]:
    """
    Detects metrics, percentages, dollar figures, and scale multipliers in bullet points.
    ATS engines and top recruiters heavily favor quantified accomplishments.
    """
    quant_patterns = [
        r"\b\d+%\b",  # Percentages
        r"\$[\d,]+(?:\.\d+)?[kKmMbB]?",  # Dollar amounts
        r"\b\d+x\b",  # Multipliers (e.g. 3x)
        r"\b\d+(?:,\d{3})*(?:\+)?\s*(?:users|clients|customers|records|jobs|requests|events|engineers|teams|members|projects|days|hours|minutes|seconds|ms)\b",  # Scaled units
        r"\b(?:reduced|increased|boosted|saved|grew|cut|scaled)\s+(?:by\s+)?[\$]?\d+[\w%]*\b",  # Action metric phrases
    ]

    quantified_bullets: List[str] = []
    extracted_metrics: List[str] = []

    for b in bullets:
        has_metric = False
        for pat in quant_patterns:
            matches = re.findall(pat, b, re.IGNORECASE)
            if matches:
                has_metric = True
                extracted_metrics.extend(matches)
        if has_metric:
            quantified_bullets.append(b)

    total_bullets = max(len(bullets), 1)
    quant_ratio = round((len(quantified_bullets) / total_bullets) * 100.0, 1)

    return {
        "quantified_bullet_count": len(quantified_bullets),
        "total_bullet_count": len(bullets),
        "quantification_pct": quant_ratio,
        "extracted_metrics": extracted_metrics[:15],
        "quantified_samples": quantified_bullets[:5],
    }


def analyze_readability(text: str) -> Dict[str, Any]:
    """
    Calculates readability statistics: word count, sentence count,
    approximate Flesch Reading Ease score, and estimated pages.
    """
    words = re.findall(r"\b[a-zA-Z0-9-]+\b", text)
    word_count = len(words)
    sentences = re.split(r"[.!?]+(?:\s+|\n)", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
    sentence_count = max(len(sentences), 1)

    avg_sentence_len = round(word_count / sentence_count, 1)

    # Approximate syllable count
    def count_syllables(w: str) -> int:
        w = w.lower()
        count = len(re.findall(r"[aeiouy]+", w))
        if w.endswith("e") and not w.endswith("le") and count > 1:
            count -= 1
        return max(count, 1)

    total_syllables = sum(count_syllables(w) for w in words) if words else 1
    avg_syllables_per_word = total_syllables / max(word_count, 1)

    # Standard Flesch Reading Ease formula
    if word_count > 10:
        flesch_score = round(
            206.835 - (1.015 * avg_sentence_len) - (84.6 * avg_syllables_per_word), 1
        )
        flesch_score = max(0.0, min(100.0, flesch_score))
    else:
        flesch_score = 50.0

    # Page estimate (typical standard resume page is ~380-450 words)
    estimated_pages = round(word_count / 420.0, 1)
    estimated_reading_time_min = round(word_count / 200.0, 1)

    # Bullet length analysis
    bullets = extract_bullet_points(text)
    bullet_lengths = [len(b.split()) for b in bullets]
    avg_bullet_len = round(sum(bullet_lengths) / max(len(bullet_lengths), 1), 1)

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_len": avg_sentence_len,
        "flesch_reading_ease": flesch_score,
        "estimated_pages": estimated_pages,
        "reading_time_minutes": estimated_reading_time_min,
        "avg_bullet_length_words": avg_bullet_len,
    }


def analyze_industry_alignment(text: str, industry: str) -> Dict[str, Any]:
    """Matches industry skill taxonomy terms against resume text."""
    tax = INDUSTRY_TAXONOMY.get(industry, INDUSTRY_TAXONOMY["Software & Technology"])
    text_lower = text.lower()

    matched_skills: List[str] = []
    missing_skills: List[str] = []

    for skill in tax:
        # Match as whole term
        pat = rf"\b{re.escape(skill)}\b"
        if re.search(pat, text_lower):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    match_ratio = round((len(matched_skills) / max(len(tax), 1)) * 100.0, 1)

    return {
        "industry": industry,
        "total_taxonomy_skills": len(tax),
        "matched_skills": sorted(matched_skills),
        "matched_count": len(matched_skills),
        "missing_recommendations": sorted(missing_skills)[:12],
        "alignment_pct": match_ratio,
    }


def extract_feature_vector(
    text: str, industry: str = "Software & Technology", career_level: str = "Mid-Level Professional"
) -> Dict[str, float]:
    """
    Extracts a quantitative numerical feature dictionary (20 dimensions)
    representing resume quality, structure, and ATS readiness.
    Used by the ResumeAnalyzer ML model for training and inference.
    """
    cleaned = clean_text(text)
    sections = segment_sections(cleaned)
    bullets = extract_bullet_points(cleaned)
    contact = extract_contact_info(cleaned)
    verbs = analyze_action_verbs(cleaned, bullets)
    quant = analyze_quantification(bullets)
    readability = analyze_readability(cleaned)
    alignment = analyze_industry_alignment(cleaned, industry)
    benchmarks = CAREER_LEVEL_BENCHMARKS.get(
        career_level, CAREER_LEVEL_BENCHMARKS["Mid-Level Professional"]
    )

    # 1. Section presence flags
    has_contact = 1.0 if (contact["has_email"] and contact["has_phone"]) else 0.0
    has_summary = 1.0 if sections["summary"]["found"] else 0.0
    has_experience = 1.0 if sections["experience"]["found"] else 0.0
    has_education = 1.0 if sections["education"]["found"] else 0.0
    has_skills = 1.0 if sections["skills"]["found"] else 0.0
    has_projects = 1.0 if sections["projects"]["found"] else 0.0
    has_certifications = 1.0 if sections["certifications"]["found"] else 0.0

    # 2. Section completeness score (0-1)
    req_secs = benchmarks["required_sections"]
    found_req = sum(
        1.0 for s in req_secs if (sections[s]["found"] if s in sections else (s == "contact" and has_contact))
    )
    req_ratio = found_req / max(len(req_secs), 1)

    # 3. Action verb density (0-1)
    verb_density = min(verbs["action_verb_density_pct"] / 100.0, 1.0)
    strong_verb_count_norm = min(verbs["total_unique_action_verbs"] / 20.0, 1.0)

    # 4. Weak verb penalty (0-1)
    weak_penalty = min(verbs["weak_count"] / 10.0, 1.0)

    # 5. Quantification ratio (0-1)
    quant_ratio = min(quant["quantification_pct"] / 100.0, 1.0)

    # 6. Word count compliance (0-1)
    w_count = readability["word_count"]
    if benchmarks["min_words"] <= w_count <= benchmarks["max_words"]:
        length_compliance = 1.0
    elif w_count < benchmarks["min_words"]:
        length_compliance = max(0.2, w_count / max(benchmarks["min_words"], 1))
    else:
        excess = w_count - benchmarks["max_words"]
        length_compliance = max(0.3, 1.0 - (excess / 1000.0))

    # 7. Readability / bullet quality (0-1)
    flesch_norm = min(max(readability["flesch_reading_ease"], 0.0), 100.0) / 100.0
    bullet_len = readability["avg_bullet_length_words"]
    bullet_quality = 1.0 if (8 <= bullet_len <= 30) else 0.5

    # 8. Industry keyword density (0-1)
    industry_match_norm = min(alignment["matched_count"] / 15.0, 1.0)

    # 9. Online presence (LinkedIn, GitHub) (0-1)
    online_presence = (
        (1.0 if contact["has_linkedin"] else 0.0) + (1.0 if contact["has_github"] else 0.0)
    ) / 2.0

    return {
        "feat_has_contact": has_contact,
        "feat_has_summary": has_summary,
        "feat_has_experience": has_experience,
        "feat_has_education": has_education,
        "feat_has_skills": has_skills,
        "feat_has_projects": has_projects,
        "feat_has_certifications": has_certifications,
        "feat_required_sections_ratio": req_ratio,
        "feat_action_verb_density": verb_density,
        "feat_strong_verb_count_norm": strong_verb_count_norm,
        "feat_weak_verb_penalty": weak_penalty,
        "feat_quantification_ratio": quant_ratio,
        "feat_length_compliance": length_compliance,
        "feat_flesch_score_norm": flesch_norm,
        "feat_bullet_quality": bullet_quality,
        "feat_industry_match_norm": industry_match_norm,
        "feat_online_presence": online_presence,
        "feat_total_bullets_norm": min(len(bullets) / 20.0, 1.0),
        "feat_contact_completeness": contact["completeness_score"] / 100.0,
    }
