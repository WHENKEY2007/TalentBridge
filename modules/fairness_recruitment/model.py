"""
TalentBridge AI - Fairness-Aware Recruitment Model (FairHire)
Assigned Lead: 24B11AI159

Pipeline (implemented in fairhire_core.py):
- Inputs:
    - Candidate resumes (plain text extracted from PDF / DOCX / TXT)
    - A job description (required skills are extracted automatically)
- Outputs:
    - Per-factor bias test (Gender, College, Age, Career gap): average score change and rank-flip rate
    - Fair score and fair rank after removing the effect of every flagged factor
    - Selected / Rejected decision with a plain-language reason for each candidate
- Method:
    - Counterfactual testing: change ONE factor of ONE candidate at a time and re-score
    - Fair re-ranking: subtract each flagged factor's measured effect from the original score
"""

from typing import Any, Dict, List

from .fairhire_core import analyze, find_skills, make_scorer, parse_resume


class FairnessAuditor:
    """Programmatic entry point to the FairHire bias audit."""

    def __init__(self, kind: str = "skills", strength: float = 1.0, top_n: int = 3, threshold: float = 2.0) -> None:
        self.kind = kind
        self.strength = strength
        self.top_n = top_n
        self.threshold = threshold
        self.is_trained = True  # rule-based pipeline, nothing to fit

    def train(self, data: Any = None) -> None:
        """No training step: scoring and bias testing are computed directly from the inputs."""
        self.is_trained = True

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the audit.

        features:
            job_description: str
            resumes: list of resume texts, or list of (filename, text) pairs
        """
        jd = features["job_description"]
        required = find_skills(jd)
        if not required:
            raise ValueError("No known skills found in the job description.")
        resumes: List[Any] = features["resumes"]
        cands = [parse_resume(r[1], r[0]) if isinstance(r, (tuple, list)) else parse_resume(r, f"candidate_{i + 1}")
                 for i, r in enumerate(resumes)]
        scorer = make_scorer(self.kind, jd, required, self.strength)
        result = analyze(cands, scorer, required, self.top_n, self.threshold)
        result["required_skills"] = required
        result["candidates"] = cands
        return result
