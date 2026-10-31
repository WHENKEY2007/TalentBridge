"""
TalentBridge AI - Threat & Red-Flag Analyzer for Job Postings
Provides heuristic threat auditing, document parsing, and explainable safety checks.
"""

import io
import re
from typing import Any, Dict, List, Optional, Tuple, Union


def parse_job_document(file_data: Union[Any, bytes], filename: str) -> str:
    """
    Extracts text from uploaded PDF, DOCX, or TXT job posting files.
    """
    if not file_data or not filename:
        return ""

    ext = filename.lower().split(".")[-1]
    raw_bytes = file_data.read() if hasattr(file_data, "read") else file_data

    if hasattr(file_data, "seek"):
        file_data.seek(0)

    try:
        if ext == "pdf":
            try:
                import fitz
                doc = fitz.open(stream=raw_bytes, filetype="pdf")
                pages = [page.get_text() for page in doc]
                return "\n".join(pages).strip()
            except Exception:
                # Fallback for plain text decoding if pdf parser fails
                return raw_bytes.decode("utf-8", errors="ignore").strip()

        elif ext in ("docx", "doc"):
            try:
                import docx
                doc = docx.Document(io.BytesIO(raw_bytes))
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                return "\n".join(paragraphs).strip()
            except Exception:
                return raw_bytes.decode("utf-8", errors="ignore").strip()

        else:
            # Assume plain text / markdown
            return raw_bytes.decode("utf-8", errors="ignore").strip()

    except Exception:
        return ""


RED_FLAG_PATTERNS = [
    {
        "category": "Off-Platform Communication",
        "severity": "High",
        "pattern": r"\b(telegram|@\w+_?(recruit|hr|jobs?|hiring)|whatsapp|\+1-\d{3}-fake|signal\s+app|hangouts)\b",
        "title": "Unregulated Messaging App Recruiter",
        "description": "Recruiter instructs candidate to communicate via Telegram, WhatsApp, or private messaging rather than verified corporate email or ATS.",
    },
    {
        "category": "Advance Fee / Equipment Scam",
        "severity": "Critical",
        "pattern": r"\b(cashier'?s?\s+check|deposit.*check|send.*money\s+order|western\s+union|moneygram|registration\s+fee|refundable\s+deposit|equipment\s+vendor|gift\s+cards?|steam\s+cards?|apple\s+gift)\b",
        "title": "Check Cashing or Advance-Fee Scam Indicator",
        "description": "Mentions depositing company checks in personal accounts, wiring funds back, buying equipment from specified vendors, or purchasing gift cards.",
    },
    {
        "category": "Cryptocurrency & Money Mule",
        "severity": "Critical",
        "pattern": r"\b(crypto|bitcoin|usdt|btc\s+wallet|crypto\s+atm|wallet\s+transfer|package\s+forwarding|parcel\s+re-?shipping|package\s+mule)\b",
        "title": "Cryptocurrency or Reshipping Mule Operation",
        "description": "Involves processing crypto payments, handling personal wallet transfers, or reshipping mystery packages from your home.",
    },
    {
        "category": "Premature Identity / Banking Request",
        "severity": "High",
        "pattern": r"\b(ssn|social\s+security\s+number|bank\s+account\s+details|routing\s+number|credit\s+card|send.*driver'?s?\s+license|passport\s+copy)\b",
        "title": "Premature PII / Bank Account Harvesting",
        "description": "Asks for sensitive personal identifiers, bank account numbers, or IDs before any formal contract or verified interview.",
    },
    {
        "category": "Unrealistic Compensation / No-Interview",
        "severity": "Medium",
        "pattern": r"\b(no\s+interview\s+(needed|required)|immediate\s+hire\s+no\s+experience|\$5[0-9]/hr\s+data\s+entry|\$3,?000\s+weekly.*no\s+experience|guaranteed\s+daily\s+pay|work\s+1\s+hour.*earn)\b",
        "title": "Unrealistic Compensation with No Formal Vetting",
        "description": "Promises extremely high compensation for entry-level / data entry work with zero interview or background evaluation.",
    },
    {
        "category": "Free / Suspicious Email Domain",
        "severity": "High",
        "pattern": r"[\w\.-]+@(gmail\.com|yahoo\.com|hotmail\.com|outlook\.com|yopmail\.com|protonmail\.com)",
        "title": "Free Public Webmail for Corporate Recruiting",
        "description": "Corporate HR claims to represent an enterprise organization but uses a free public webmail address (e.g. @gmail.com) instead of a corporate domain.",
    },
]

POSITIVE_INDICATORS = [
    {
        "pattern": r"\b(health\s+insurance|dental|vision|401\(?k\)?|pto|paid\s+time\s+off|parental\s+leave|equity|stock\s+options)\b",
        "title": "Standard Corporate Benefits Package",
    },
    {
        "pattern": r"\b(interview\s+process|technical\s+assessment|portfolio\s+review|peer\s+review|bachelor'?s?\s+degree|master'?s|ph\.?d|years\s+of\s+experience)\b",
        "title": "Structured Evaluation & Experience Criteria",
    },
    {
        "pattern": r"\b(soc\s*2|hipaa|gdpr|equal\s+opportunity\s+employer|eeo|headquarters|founded\s+in)\b",
        "title": "Corporate Compliance & Governance Disclosures",
    },
]


def audit_job_posting_security(
    text: str,
    title: str = "",
    company: str = "",
    model_fraud_prob: float = 0.0,
) -> Dict[str, Any]:
    """
    Performs multi-layered threat analysis combining ML model output with rule-based threat heuristics.
    """
    full_text = f"{title} {company} {text}".strip()
    lowered = full_text.lower()

    detected_red_flags: List[Dict[str, Any]] = []
    detected_positives: List[Dict[str, Any]] = []

    # Check Red Flags
    for flag in RED_FLAG_PATTERNS:
        match = re.search(flag["pattern"], lowered)
        if match:
            # Extract sample snippet
            start = max(0, match.start() - 25)
            end = min(len(lowered), match.end() + 25)
            snippet = lowered[start:end].replace("\n", " ").strip()
            detected_red_flags.append({
                "title": flag["title"],
                "category": flag["category"],
                "severity": flag["severity"],
                "description": flag["description"],
                "matched_snippet": f"...{snippet}...",
            })

    # Check Positive Indicators
    for pos in POSITIVE_INDICATORS:
        if re.search(pos["pattern"], lowered):
            detected_positives.append({
                "title": pos["title"],
            })

    # Severity scoring
    critical_count = sum(1 for f in detected_red_flags if f["severity"] == "Critical")
    high_count = sum(1 for f in detected_red_flags if f["severity"] == "High")
    medium_count = sum(1 for f in detected_red_flags if f["severity"] == "Medium")

    # Composite Threat Calculation
    # Baseline from ML model
    heuristic_penalty = (critical_count * 35.0) + (high_count * 20.0) + (medium_count * 10.0)
    heuristic_bonus = min(len(detected_positives) * 8.0, 25.0)

    # Adjust fraud probability
    adjusted_fraud_prob = min(max(model_fraud_prob + (heuristic_penalty / 100.0) - (heuristic_bonus / 100.0), 0.01), 0.99)
    composite_trust_score = round((1.0 - adjusted_fraud_prob) * 100.0, 1)

    if critical_count > 0 or adjusted_fraud_prob >= 0.70:
        threat_level = "Critical / High Risk"
        verdict = "Fraudulent Scam Detected"
        verdict_color = "#dc2626"  # Red
        badge_icon = "🚨"
    elif high_count > 0 or adjusted_fraud_prob >= 0.40:
        threat_level = "Elevated Risk / Suspicious"
        verdict = "Suspicious Signals Present"
        verdict_color = "#f59e0b"  # Amber
        badge_icon = "⚠️"
    else:
        threat_level = "Low Risk / Clean"
        verdict = "Likely Legitimate Posting"
        verdict_color = "#10b981"  # Green
        badge_icon = "✅"

    # Actionable safety advice
    safety_steps = []
    if critical_count > 0 or high_count > 0:
        safety_steps.append("❌ NEVER deposit checks received by mail or wire funds via Zelle, CashApp, or Western Union.")
        safety_steps.append("❌ NEVER conduct official job interviews solely via Telegram, WhatsApp, or Google Chat.")
        safety_steps.append("❌ NEVER pay upfront equipment deposits, background check fees, or training costs.")
        safety_steps.append("🔍 Look up the company on LinkedIn or official corporate domain to verify recruiters.")
    else:
        safety_steps.append("✅ Verify that recruiter emails originate from official corporate domain (@company.com).")
        safety_steps.append("✅ Cross-reference the role on the company's official 'Careers' portal.")
        safety_steps.append("✅ Do not disclose Social Security Number or banking info until an official offer is signed.")

    return {
        "verdict": verdict,
        "threat_level": threat_level,
        "verdict_color": verdict_color,
        "badge_icon": badge_icon,
        "composite_trust_score": composite_trust_score,
        "model_fraud_probability": round(model_fraud_prob * 100.0, 1),
        "adjusted_fraud_probability": round(adjusted_fraud_prob * 100.0, 1),
        "red_flags": detected_red_flags,
        "positive_signals": detected_positives,
        "safety_steps": safety_steps,
        "character_count": len(full_text),
    }
