"""
Resume–Job Matching Hybrid Machine Learning Model.
Combines TF-IDF vectorization with Domain Skills Taxonomy,
Seniority/Experience Fit Analysis, ATS Diagnostics, and What-If Simulation.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import (
    MODEL_PATH,
    SUBLINEAR_TF,
    TFIDF_MAX_FEATURES,
    TFIDF_NGRAM_RANGE,
    THRESHOLD_HIGH,
    THRESHOLD_MODERATE,
    WEIGHT_EXPERIENCE_FIT,
    WEIGHT_SKILLS_OVERLAP,
    WEIGHT_TEXTUAL_SIMILARITY,
)
from .preprocessing import (
    audit_resume_structure,
    clean_text,
    evaluate_seniority_fit,
    find_skill_gap_detailed,
)


class ResumeJobMatcher:
    """
    Enterprise-grade Hybrid Resume–Job Matching engine:
    1. Lexical & Contextual similarity via TF-IDF + Cosine Distance
    2. Explicit Domain Competencies & Skills Taxonomy matching with Synonym Normalization
    3. Experience & Seniority Level Fit Analysis
    4. ATS formatting, impact verbs, and structural audit
    5. Interactive What-If Score Simulator
    """

    def __init__(self, vectorizer: Optional[TfidfVectorizer] = None) -> None:
        self.vectorizer = vectorizer or TfidfVectorizer(
            ngram_range=TFIDF_NGRAM_RANGE,
            max_features=TFIDF_MAX_FEATURES,
            sublinear_tf=SUBLINEAR_TF,
            stop_words="english",
        )
        self.is_fitted = False

    def fit(self, corpus: list[str]) -> "ResumeJobMatcher":
        """Fits the TF-IDF vectorizer on a corpus."""
        cleaned = [clean_text(doc) for doc in corpus if doc]
        if cleaned:
            self.vectorizer.fit(cleaned)
            self.is_fitted = True
        return self

    def save(self, filepath: Optional[Path] = None) -> Path:
        """Serializes the fitted vectorizer."""
        target = Path(filepath or MODEL_PATH)
        target.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.vectorizer, target)
        return target

    @classmethod
    def load(cls, filepath: Optional[Path] = None) -> "ResumeJobMatcher":
        """Loads a pre-fitted vectorizer from disk if present."""
        target = Path(filepath or MODEL_PATH)
        if target.exists():
            vec = joblib.load(target)
            instance = cls(vectorizer=vec)
            instance.is_fitted = True
            return instance
        return cls()

    def compute_similarity(self, resume_text: str, job_text: str) -> float:
        """
        Computes cosine similarity of TF-IDF vectors.
        """
        cleaned_resume = clean_text(resume_text)
        cleaned_job = clean_text(job_text)

        if not cleaned_resume or not cleaned_job:
            return 0.0

        if not self.is_fitted:
            local_vec = TfidfVectorizer(
                ngram_range=TFIDF_NGRAM_RANGE,
                sublinear_tf=SUBLINEAR_TF,
                stop_words="english",
            )
            matrix = local_vec.fit_transform([cleaned_resume, cleaned_job])
            sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        else:
            vectors = self.vectorizer.transform([cleaned_resume, cleaned_job])
            sim = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

        return float(np.clip(sim, 0.0, 1.0))

    def predict(self, resume_text: str, job_text: str) -> Dict[str, Any]:
        """
        Executes complete hybrid analysis:
        - TF-IDF textual similarity
        - Domain skills taxonomy overlap (with synonym canonicalization)
        - Experience & Seniority alignment
        - Weighted composite score
        - ATS structural audit
        - Actionable step-by-step optimization recommendations
        """
        # 1. Textual Similarity
        text_sim = self.compute_similarity(resume_text, job_text)
        text_pct = round(text_sim * 100.0, 1)

        # 2. Detailed Skills Taxonomy Analysis (with alias resolution)
        skill_analysis = find_skill_gap_detailed(resume_text, job_text)
        skills_ratio = skill_analysis["skills_match_ratio"]
        skills_pct = skill_analysis["skills_match_percentage"]

        # 3. Experience & Seniority Fit Evaluation
        seniority_fit = evaluate_seniority_fit(resume_text, job_text)

        # 4. Composite Weighted Score
        if skill_analysis["job_skills"] and seniority_fit.get("required_years") is not None:
            composite_score = (
                (WEIGHT_SKILLS_OVERLAP * skills_ratio)
                + (WEIGHT_TEXTUAL_SIMILARITY * text_sim)
                + (WEIGHT_EXPERIENCE_FIT * seniority_fit["fit_score"])
            )
        elif skill_analysis["job_skills"]:
            composite_score = (0.55 * skills_ratio) + (0.45 * text_sim)
        else:
            composite_score = text_sim

        composite_pct = round(composite_score * 100.0, 1)

        # 5. Classification Tier
        if composite_pct >= THRESHOLD_HIGH:
            level = "High Match"
            level_color = "#22c55e"
            verdict = "Strong candidate alignment! High technical skill coverage and comprehensive experience correspondence."
        elif composite_pct >= THRESHOLD_MODERATE:
            level = "Moderate Match"
            level_color = "#f59e0b"
            verdict = "Solid foundation with moderate overlap. Addressing the identified skill gaps will notably improve suitability."
        else:
            level = "Low Match"
            level_color = "#ef4444"
            verdict = "Limited overlap detected. Crucial job requirements and core technologies are missing from the resume."

        # 6. ATS Structural Audit
        ats_audit = audit_resume_structure(resume_text)

        # 7. Actionable Optimization Strategy
        optimization_plan: List[str] = []
        if skill_analysis["missing_skills"]:
            top_missing = ", ".join(f"'{s}'" for s in skill_analysis["missing_skills"][:5])
            optimization_plan.append(
                f"**Skill Gap Priority:** Add evidence of experience with high-demand job skills: {top_missing}."
            )

        if seniority_fit["badge"] == "Experience Gap":
            optimization_plan.append(
                f"**Seniority Realignment:** Role targets {seniority_fit['required_years']:.1f}+ years. Highlight leadership, end-to-end project ownership, or complex architectural achievements to compensate."
            )

        if ats_audit["sections_missing"]:
            missing_sec = ", ".join(ats_audit["sections_missing"])
            optimization_plan.append(f"**ATS Section Warning:** Add missing standard sections: {missing_sec}.")

        if ats_audit["action_verb_count"] < 6:
            optimization_plan.append(
                "**Action Verb Impact:** Strengthen bullet points with action verbs (e.g., 'Architected', 'Engineered', 'Optimized')."
            )

        if ats_audit["quantification_count"] < 3:
            optimization_plan.append(
                "**Quantify Results:** Add numerical metrics, scale indicators (e.g. 'reduced latency by 40%', 'processed 5M requests')."
            )

        if not optimization_plan:
            optimization_plan.append("Your resume is well-tailored for this role with strong skill coverage, experience alignment, and high ATS readiness.")

        return {
            "similarity_score": composite_score,
            "match_percentage": composite_pct,
            "match_level": level,
            "match_color": level_color,
            "verdict": verdict,
            "textual_similarity_percentage": text_pct,
            "skills_overlap_percentage": skills_pct,
            "matched_keywords": skill_analysis["matched_skills"],
            "missing_keywords": skill_analysis["missing_skills"],
            "bonus_skills": skill_analysis["bonus_skills"],
            "top_job_keywords": skill_analysis["job_skills"],
            "category_breakdown": skill_analysis["category_breakdown"],
            "seniority_fit": seniority_fit,
            "ats_audit": ats_audit,
            "optimization_plan": optimization_plan,
            "resume_word_count": ats_audit["word_count"],
            "job_word_count": len(clean_text(job_text).split()),
        }

    def simulate_skill_additions(
        self,
        resume_text: str,
        job_text: str,
        added_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Simulates the effect of adding candidate skills to the resume.
        Returns baseline score, simulated score, score increase, and new coverage.
        """
        baseline_pred = self.predict(resume_text, job_text)
        if not added_skills:
            return {
                "original_match_percentage": baseline_pred["match_percentage"],
                "simulated_match_percentage": baseline_pred["match_percentage"],
                "score_delta": 0.0,
                "newly_matched_skills": [],
                "remaining_missing": baseline_pred["missing_keywords"],
            }

        simulated_resume = (
            resume_text
            + "\n\nADDITIONAL TECHNICAL PROFICIENCIES:\n"
            + ", ".join(added_skills)
        )
        simulated_pred = self.predict(simulated_resume, job_text)

        newly_matched = [
            s for s in simulated_pred["matched_keywords"]
            if s not in baseline_pred["matched_keywords"]
        ]
        score_delta = round(
            simulated_pred["match_percentage"] - baseline_pred["match_percentage"],
            1
        )

        return {
            "original_match_percentage": baseline_pred["match_percentage"],
            "simulated_match_percentage": simulated_pred["match_percentage"],
            "score_delta": score_delta,
            "newly_matched_skills": newly_matched,
            "remaining_missing": simulated_pred["missing_keywords"],
        }

    def generate_markdown_report(self, results: Dict[str, Any], candidate_title: str = "Candidate") -> str:
        """
        Generates an enterprise-ready Markdown audit and evaluation report.
        """
        ats = results["ats_audit"]
        sen = results.get("seniority_fit", {})

        report_lines = [
            f"# TalentBridge AI — Candidate Matching & ATS Diagnostic Report",
            f"**Evaluation Status:** {results['match_level']} ({results['match_percentage']}%)",
            f"**Suitability Verdict:** {results['verdict']}\n",
            "---",
            "## 1. Key Performance Indicators",
            f"- **Overall Suitability Match:** {results['match_percentage']}%",
            f"- **Technical Skills Overlap:** {results['skills_overlap_percentage']}%",
            f"- **Contextual Textual Similarity:** {results['textual_similarity_percentage']}%",
            f"- **Seniority Alignment:** {sen.get('badge', 'N/A')} ({sen.get('status', 'N/A')})",
            "",
            "## 2. Technical Competencies Breakdown",
            f"- **Matched Required Skills ({len(results['matched_keywords'])}):** "
            + (", ".join(results["matched_keywords"]) if results["matched_keywords"] else "None"),
            f"- **Critical Skill Gaps ({len(results['missing_keywords'])}):** "
            + (", ".join(results["missing_keywords"]) if results["missing_keywords"] else "None (100% Coverage)"),
            f"- **Candidate Bonus Skills ({len(results['bonus_skills'])}):** "
            + (", ".join(results["bonus_skills"][:15]) if results["bonus_skills"] else "None"),
            "",
            "## 3. Applicant Tracking System (ATS) Health",
            f"- **Word Count:** {ats['word_count']} words ({ats['length_status']})",
            f"- **Standard Sections Detected:** {len(ats['sections_present'])}/5 ({', '.join(ats['sections_present'])})",
            f"- **Missing Headers:** {', '.join(ats['sections_missing']) if ats['sections_missing'] else 'None'}",
            f"- **Action Verbs Found:** {ats['action_verb_count']}",
            f"- **Quantified Metrics:** {ats['quantification_count']} metrics",
            "",
            "## 4. Actionable Optimization Strategy",
        ]

        for i, step in enumerate(results["optimization_plan"], 1):
            report_lines.append(f"{i}. {step}")

        report_lines.extend([
            "",
            "---",
            "*Report generated by TalentBridge AI Resume–Job Matching Engine.*",
            "*Notice: Textual similarity scores represent heuristic analytical guides and are not an employment guarantee.*"
        ])

        return "\n".join(report_lines)
