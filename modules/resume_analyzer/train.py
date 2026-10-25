"""
Training Script for AI Resume Analysis Module.
Generates synthetic benchmark datasets, trains regressor & classifier models,
evaluates performance metrics (Accuracy, F1, RMSE), and serializes artifacts.
Assigned to Member 10.
"""

from pathlib import Path
import random
from typing import Any, Dict, List, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from .config import (
    ACTION_VERBS,
    ARTIFACTS_DIR,
    DATA_DIR,
    INDUSTRY_TAXONOMY,
    MODEL_PATH,
    TRAINING_DATA_PATH,
)
from .preprocessing import extract_feature_vector


def generate_synthetic_benchmark_dataset(num_samples: int = 350) -> pd.DataFrame:
    """
    Generates a balanced dataset of resumes with varying quality profiles:
    Elite (85-100), Competitive (66-84), Developing (46-65), and Poor/Scaffold (0-45).
    """
    random.seed(42)
    np.random.seed(42)

    rows: List[Dict[str, Any]] = []

    industries = list(INDUSTRY_TAXONOMY.keys())
    levels = ["Entry-Level / Graduate", "Mid-Level Professional", "Senior / Executive Lead"]

    for i in range(num_samples):
        industry = random.choice(industries)
        level = random.choice(levels)
        quality_tier = random.choices(
            ["elite", "competitive", "developing", "poor"],
            weights=[0.25, 0.35, 0.25, 0.15],
            k=1
        )[0]

        # Generate resume text based on quality tier
        has_contact = quality_tier in ["elite", "competitive", "developing"]
        contact_line = (
            "Alex Smith | (555) 019-2834 | alex.smith@example.com | linkedin.com/in/alexsmith | github.com/alexsmith"
            if quality_tier == "elite"
            else (
                "Alex Smith | alex.smith@example.com | (555) 019-2834"
                if has_contact
                else "Alex Smith"
            )
        )

        has_summary = quality_tier in ["elite", "competitive"]
        summary = ""
        if has_summary:
            summary = (
                "PROFESSIONAL SUMMARY\n"
                "Results-driven technology specialist with proven history of architecting high-scale platforms and driving ROI.\n\n"
            )

        # Experience & Bullets
        bullets = []
        num_bullets = (
            random.randint(6, 12) if quality_tier == "elite"
            else random.randint(4, 8) if quality_tier == "competitive"
            else random.randint(2, 5) if quality_tier == "developing"
            else random.randint(1, 3)
        )

        ind_skills = list(INDUSTRY_TAXONOMY[industry])
        for b_idx in range(num_bullets):
            skill_sample = random.sample(ind_skills, min(2, len(ind_skills)))
            if quality_tier == "elite":
                verb = random.choice(list(ACTION_VERBS["Execution & Engineering"] | ACTION_VERBS["Optimization & Metrics"]))
                metric = random.choice(["35%", "$1.2M", "50,000 users", "99.9% uptime", "3x", "45% reduction"])
                bullets.append(f"- {verb.capitalize()} {skill_sample[0]} pipeline resulting in {metric} performance improvement.")
            elif quality_tier == "competitive":
                verb = random.choice(list(ACTION_VERBS["Execution & Engineering"]))
                bullets.append(f"- {verb.capitalize()} application features utilizing {skill_sample[0]} and {skill_sample[1]}.")
            elif quality_tier == "developing":
                if random.random() > 0.5:
                    bullets.append(f"- Responsible for working on {skill_sample[0]} systems.")
                else:
                    bullets.append(f"- Helped with {skill_sample[0]} and fixing bugs.")
            else:
                bullets.append(f"- Duties included attending meetings and general {skill_sample[0]} tasks.")

        exp_block = "EXPERIENCE\n" + "\n".join(bullets) + "\n\n"

        # Skills section
        skills_sample = random.sample(
            ind_skills,
            min(len(ind_skills), 12 if quality_tier == "elite" else 7 if quality_tier == "competitive" else 3)
        )
        skills_block = "SKILLS\n" + ", ".join(skills_sample) + "\n\n"

        # Education
        edu_block = "EDUCATION\nBachelor of Science in Computer Science | State University | 2022\n\n" if quality_tier != "poor" else ""

        # Projects
        proj_block = (
            "PROJECTS\n"
            f"- Project Alpha ({skills_sample[0]}): Engineered scalable service handling 10k req/sec.\n\n"
            if quality_tier in ["elite", "competitive"]
            else ""
        )

        resume_text = f"{contact_line}\n\n{summary}{edu_block}{skills_block}{exp_block}{proj_block}"

        # Assign ground-truth target score
        if quality_tier == "elite":
            target_score = random.uniform(85.0, 98.0)
            target_class = "Elite"
        elif quality_tier == "competitive":
            target_score = random.uniform(66.0, 84.0)
            target_class = "Competitive"
        elif quality_tier == "developing":
            target_score = random.uniform(46.0, 65.0)
            target_class = "Developing"
        else:
            target_score = random.uniform(20.0, 45.0)
            target_class = "Needs Work"

        # Extract features
        feats = extract_feature_vector(resume_text, industry=industry, career_level=level)
        row = {
            "resume_id": f"res_{i:04d}",
            "industry": industry,
            "career_level": level,
            "quality_tier": target_class,
            "target_score": round(target_score, 2),
            **feats,
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(TRAINING_DATA_PATH, index=False)
    return df


def train_resume_analyzer_model(
    data_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Trains the regressor and classifier pipelines, computes metrics,
    and serializes the model artifact into artifacts/resume_analyzer_model.joblib.
    """
    if data_df is None:
        if TRAINING_DATA_PATH.exists():
            data_df = pd.read_csv(TRAINING_DATA_PATH)
        else:
            data_df = generate_synthetic_benchmark_dataset(350)

    feature_cols = [c for c in data_df.columns if c.startswith("feat_")]
    X = np.asarray(data_df[feature_cols].values, dtype=np.float64)
    y_score = np.asarray(data_df["target_score"].values, dtype=np.float64)
    y_class = np.asarray(data_df["quality_tier"].values, dtype=str)

    X_train, X_test, y_score_train, y_score_test, y_class_train, y_class_test = train_test_split(
        X, y_score, y_class, test_size=0.25, random_state=42, stratify=y_class
    )

    # 1. Regressor for continuous ATS score (0 - 100)
    regressor = GradientBoostingRegressor(
        n_estimators=120,
        learning_rate=0.08,
        max_depth=4,
        random_state=42,
    )
    regressor.fit(X_train, y_score_train)
    y_score_pred = regressor.predict(X_test)

    r2 = float(r2_score(y_score_test, y_score_pred))
    rmse = float(np.sqrt(mean_squared_error(y_score_test, y_score_pred)))

    # 2. Classifier for readiness tier
    classifier = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        random_state=42,
    )
    classifier.fit(X_train, y_class_train)
    y_class_pred = classifier.predict(X_test)

    accuracy = float(accuracy_score(y_class_test, y_class_pred))
    f1 = float(f1_score(y_class_test, y_class_pred, average="macro"))

    # Feature importances
    feature_importances = dict(
        zip(feature_cols, [round(float(v), 4) for v in regressor.feature_importances_])
    )

    artifact_bundle = {
        "regressor": regressor,
        "classifier": classifier,
        "feature_names": feature_cols,
        "metrics": {
            "r2_score": round(r2, 4),
            "rmse": round(rmse, 4),
            "accuracy": round(accuracy, 4),
            "f1_macro": round(f1, 4),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        },
        "feature_importances": feature_importances,
    }

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact_bundle, MODEL_PATH)

    return artifact_bundle["metrics"]


if __name__ == "__main__":
    metrics = train_resume_analyzer_model()
    print("Training Complete! Evaluation Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
