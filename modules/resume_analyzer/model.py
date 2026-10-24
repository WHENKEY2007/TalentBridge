"""
TalentBridge AI - AI Resume Analysis Machine Learning Model.
Hybrid multi-dimensional scoring pipeline incorporating:
1. NLP structure segmentation & contact completeness
2. Action verb density and passive phrase audit
3. Quantifiable achievement impact metrics
4. Flesch-Kincaid readability & formatting compliance
5. Supervised GradientBoosting / RandomForest model trained on resume quality benchmarks
Assigned Lead: Member 10
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import numpy as np

from .config import (
    CAREER_LEVEL_BENCHMARKS,
    MODEL_PATH,
)
from .preprocessing import (
    analyze_action_verbs,
    analyze_industry_alignment,
    analyze_quantification,
    analyze_readability,
    clean_text,
    extract_bullet_points,
    extract_contact_info,
    extract_feature_vector,
    segment_sections,
)


class ResumeAnalyzer:
    """
    ML Model implementation for AI Resume Analysis.
    Assigned to Member 10.
    """

    def __init__(self, model_path: Optional[Path] = None) -> None:
        self.model_path = Path(model_path or MODEL_PATH)
        self.bundle: Optional[Dict[str, Any]] = None
        self.regressor = None
        self.classifier = None
        self.feature_names: List[str] = []
        self.is_trained = False

        self._load_if_exists()

    def _load_if_exists(self) -> None:
        """Loads serialized model bundle if available."""
        if self.model_path.exists():
            try:
                self.bundle = joblib.load(self.model_path)
                self.regressor = self.bundle.get("regressor")
                self.classifier = self.bundle.get("classifier")
                self.feature_names = self.bundle.get("feature_names", [])
                self.is_trained = self.regressor is not None
            except Exception:
                self.is_trained = False

    def train(self, data: Any = None) -> Dict[str, Any]:
        """
        Train ML regressor and classifier models on historical / benchmark dataset.
        Serializes checkpoints into artifacts/resume_analyzer_model.joblib.
        """
        from .train import train_resume_analyzer_model

        metrics = train_resume_analyzer_model(data)
        self._load_if_exists()
        return metrics

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute multi-dimensional ATS inference.
        Accepts either raw text input dict or pre-extracted feature dictionary.
        """
        # If passed raw text or resume dictionary
        raw_text = features.get("text") or features.get("resume_text") or features.get("resume", "")
        industry = features.get("industry") or features.get("target_industry", "Software & Technology")
        career_level = features.get("career_level") or features.get("level", "Mid-Level Professional")

        if isinstance(raw_text, str) and raw_text.strip():
            return self.analyze_resume(raw_text, industry=industry, career_level=career_level)

        # Fallback if only numerical features were provided directly
        feat_vector = {k: float(v) for k, v in features.items() if k.startswith("feat_")}
        if not feat_vector:
            return {
                "status": "error",
                "message": "No valid resume text or feature vectors supplied.",
                "overall_ats_score": 0.0,
            }

        score = self._predict_score_from_vector(feat_vector)
        tier = self._predict_tier_from_vector(feat_vector, score)
        return {
            "status": "success",
            "overall_ats_score": score,
            "tier": tier,
            "grade": self._calculate_grade(score),
            "features_used": feat_vector,
        }

    def analyze_resume(
        self,
        resume_text: str,
        industry: str = "Software & Technology",
        career_level: str = "Mid-Level Professional",
    ) -> Dict[str, Any]:
        """
        Deep multi-dimensional diagnostic scan of candidate resume text.
        Returns component scores, structural breakdown, action verbs, and actionable recommendations.
        """
        text = clean_text(resume_text)
        if not text:
            return {
                "status": "empty_input",
                "overall_ats_score": 0.0,
                "tier": "Needs Work",
                "grade": "F",
                "message": "Resume text is empty.",
            }

        # 1. Linguistic and Structural Preprocessing
        sections = segment_sections(text)
        bullets = extract_bullet_points(text)
        contact = extract_contact_info(text)
        verbs_audit = analyze_action_verbs(text, bullets)
        quant_audit = analyze_quantification(bullets)
        readability_audit = analyze_readability(text)
        industry_audit = analyze_industry_alignment(text, industry)
        benchmarks = CAREER_LEVEL_BENCHMARKS.get(
            career_level, CAREER_LEVEL_BENCHMARKS["Mid-Level Professional"]
        )

        # 2. Extract 20-dimensional feature vector
        feat_vector = extract_feature_vector(text, industry=industry, career_level=career_level)

        # 3. Model Scoring (ML inference if model loaded, with calibrated heuristic backup)
        ml_score = None
        predicted_tier = None

        if self.is_trained and self.regressor and self.feature_names:
            try:
                x_vec = np.array([[feat_vector.get(fn, 0.0) for fn in self.feature_names]])
                pred_val = float(self.regressor.predict(x_vec)[0])
                ml_score = max(5.0, min(99.0, round(pred_val, 1)))

                if self.classifier:
                    predicted_tier = str(self.classifier.predict(x_vec)[0])
            except Exception:
                ml_score = None

        # 4. Component Sub-scores (0 - 100)
        # Structure Completeness
        req_found = sum(
            1 for s in benchmarks["required_sections"]
            if (sections[s]["found"] if s in sections else (s == "contact" and contact["completeness_score"] >= 60))
        )
        struct_score = round((req_found / max(len(benchmarks["required_sections"]), 1)) * 100.0, 1)

        # Action Verb Strength
        verb_score = round(
            min(100.0, (verbs_audit["action_verb_density_pct"] * 0.7) + (min(verbs_audit["total_unique_action_verbs"], 15) * 2.0) - (verbs_audit["weak_count"] * 5.0)),
            1
        )
        verb_score = max(10.0, verb_score)

        # Quantifiable Impact
        quant_score = round(
            min(100.0, (quant_audit["quantification_pct"] * 0.85) + (min(len(quant_audit["extracted_metrics"]), 10) * 1.5)),
            1
        )

        # Industry Alignment
        ind_score = round(min(100.0, industry_audit["alignment_pct"] * 2.0), 1)

        # Formatting & Readability
        format_score = round(
            (feat_vector["feat_length_compliance"] * 40.0)
            + (feat_vector["feat_bullet_quality"] * 30.0)
            + (feat_vector["feat_contact_completeness"] * 30.0),
            1
        )

        # Career Level Fit
        word_count = readability_audit["word_count"]
        level_fit = round(feat_vector["feat_length_compliance"] * 100.0, 1)

        # 5. Composite Overall Score
        if ml_score is not None:
            overall_score = ml_score
        else:
            # Calibrated composite heuristic
            overall_score = round(
                (struct_score * 0.25)
                + (verb_score * 0.20)
                + (quant_score * 0.20)
                + (ind_score * 0.15)
                + (format_score * 0.10)
                + (level_fit * 0.10),
                1
            )
            overall_score = max(5.0, min(99.0, overall_score))

        # Determine Tier & Grade
        if predicted_tier is None:
            if overall_score >= 85.0:
                predicted_tier = "Elite"
            elif overall_score >= 68.0:
                predicted_tier = "Competitive"
            elif overall_score >= 48.0:
                predicted_tier = "Developing"
            else:
                predicted_tier = "Needs Work"

        grade = self._calculate_grade(overall_score)

        # 6. Generate Actionable AI Recommendations
        recommendations = self._generate_recommendations(
            sections=sections,
            contact=contact,
            verbs_audit=verbs_audit,
            quant_audit=quant_audit,
            readability_audit=readability_audit,
            industry_audit=industry_audit,
            benchmarks=benchmarks,
            career_level=career_level,
        )

        return {
            "status": "success",
            "overall_ats_score": overall_score,
            "tier": predicted_tier,
            "grade": grade,
            "career_level": career_level,
            "industry": industry,
            "component_scores": {
                "structural_completeness": struct_score,
                "action_verb_strength": verb_score,
                "quantifiable_impact": quant_score,
                "industry_alignment": ind_score,
                "formatting_readability": format_score,
                "career_level_fit": level_fit,
            },
            "contact_audit": contact,
            "sections_audit": sections,
            "verbs_audit": verbs_audit,
            "quantification_audit": quant_audit,
            "readability_audit": readability_audit,
            "industry_audit": industry_audit,
            "recommendations": recommendations,
            "feature_vector": feat_vector,
        }

    def _predict_score_from_vector(self, feat_vec: Dict[str, float]) -> float:
        if self.is_trained and self.regressor and self.feature_names:
            x_vec = np.array([[feat_vec.get(fn, 0.0) for fn in self.feature_names]])
            pred_val = float(self.regressor.predict(x_vec)[0])
            return max(5.0, min(99.0, round(pred_val, 1)))
        # Heuristic fallback
        return 70.0

    def _predict_tier_from_vector(self, feat_vec: Dict[str, float], score: float) -> str:
        if self.is_trained and self.classifier and self.feature_names:
            x_vec = np.array([[feat_vec.get(fn, 0.0) for fn in self.feature_names]])
            return str(self.classifier.predict(x_vec)[0])
        if score >= 85:
            return "Elite"
        elif score >= 68:
            return "Competitive"
        elif score >= 48:
            return "Developing"
        return "Needs Work"

    @staticmethod
    def _calculate_grade(score: float) -> str:
        if score >= 90.0:
            return "A+"
        elif score >= 82.0:
            return "A"
        elif score >= 73.0:
            return "B+"
        elif score >= 65.0:
            return "B"
        elif score >= 55.0:
            return "C"
        elif score >= 45.0:
            return "D"
        return "F"

    @staticmethod
    def _generate_recommendations(
        sections: Dict[str, Any],
        contact: Dict[str, Any],
        verbs_audit: Dict[str, Any],
        quant_audit: Dict[str, Any],
        readability_audit: Dict[str, Any],
        industry_audit: Dict[str, Any],
        benchmarks: Dict[str, Any],
        career_level: str,
    ) -> List[Dict[str, str]]:
        recs: List[Dict[str, str]] = []

        # Contact info recommendations
        if not contact["has_email"]:
            recs.append({
                "category": "Contact Information",
                "priority": "Critical",
                "title": "Missing Candidate Email",
                "detail": "Add a professional email address at the top header for ATS recruiter parsing.",
            })
        if not contact["has_phone"]:
            recs.append({
                "category": "Contact Information",
                "priority": "High",
                "title": "Missing Phone Number",
                "detail": "Include a reachable phone number formatted with standard country/area codes.",
            })
        if not contact["has_linkedin"]:
            recs.append({
                "category": "Contact Information",
                "priority": "Medium",
                "title": "Add LinkedIn Profile URL",
                "detail": "ATS parsers look for verified LinkedIn URLs to match social recruitment records.",
            })

        # Section presence recommendations
        for req in benchmarks["required_sections"]:
            if req in sections and not sections[req]["found"]:
                recs.append({
                    "category": "Structure",
                    "priority": "High",
                    "title": f"Missing Required Section: {req.capitalize()}",
                    "detail": f"For {career_level}, ATS algorithms mandate an explicit '{req.capitalize()}' section heading.",
                })

        # Action verbs recommendations
        if verbs_audit["action_verb_density_pct"] < 60.0:
            recs.append({
                "category": "Action Verbs",
                "priority": "High",
                "title": "Increase Action Verb Bullet Density",
                "detail": f"Currently only {verbs_audit['action_verb_density_pct']}% of bullets start with power verbs. Aim for 75%+.",
            })

        if verbs_audit["weak_count"] > 0:
            examples = ", ".join(f"'{w}'" for w in list(set(verbs_audit["weak_phrases_detected"]))[:3])
            recs.append({
                "category": "Action Verbs",
                "priority": "Medium",
                "title": "Replace Passive & Cliché Phrases",
                "detail": f"Detected {verbs_audit['weak_count']} passive phrases (such as {examples}). Replace with proactive execution verbs like 'engineered', 'spearheaded', or 'orchestrated'.",
            })

        # Quantification recommendations
        if quant_audit["quantification_pct"] < 35.0:
            recs.append({
                "category": "Impact & Metrics",
                "priority": "High",
                "title": "Quantify Achievements with Metrics",
                "detail": f"Only {quant_audit['quantification_pct']}% of bullets contain measurable impact. Add percentages (%), dollar figures ($), or scale multipliers (e.g. 'reduced latency by 35%').",
            })

        # Industry alignment recommendations
        if industry_audit["missing_recommendations"]:
            missing_preview = ", ".join(industry_audit["missing_recommendations"][:4])
            recs.append({
                "category": "Industry Keywords",
                "priority": "Medium",
                "title": f"Expand Core {industry_audit['industry']} Keywords",
                "detail": f"Consider naturally integrating recognized industry tools/terms like: {missing_preview}.",
            })

        # Length / page compliance
        wc = readability_audit["word_count"]
        if wc < benchmarks["min_words"]:
            recs.append({
                "category": "Length & Detail",
                "priority": "Medium",
                "title": "Resume Too Brief",
                "detail": f"Resume contains {wc} words. Recommended minimum for {career_level} is {benchmarks['min_words']} words.",
            })
        elif wc > benchmarks["max_words"]:
            recs.append({
                "category": "Length & Detail",
                "priority": "Medium",
                "title": "Resume Length Exceeds Target",
                "detail": f"Resume contains {wc} words (approx. {readability_audit['estimated_pages']} pages). Tighten bullet descriptions to fit the target range ({benchmarks['min_words']}-{benchmarks['max_words']} words).",
            })

        return recs
