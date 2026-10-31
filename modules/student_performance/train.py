"""
TalentBridge AI - Student Performance Model Training Script
Assigned Lead: Member 3

Generates the student academic dataset, trains the regression and classification pipelines,
evaluates validation performance, and persists serialized model artifacts to disk.
"""

from pathlib import Path
import sys

# Ensure repository root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules.student_performance.config import ARTIFACTS_DIR, DATA_DIR, DATASET_PATH, MODEL_PATH
from modules.student_performance.model import (
    StudentPerformancePredictor,
    generate_synthetic_academic_dataset,
)


def run_training() -> None:
    print("=" * 60)
    print("[TalentBridge AI] - Student Performance Training Pipeline")
    print("=" * 60)

    # 1. Ensure directories exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Generate and save synthetic dataset
    print("[*] Generating 1,500 realistic academic student records...")
    df = generate_synthetic_academic_dataset(n_samples=1500, random_state=42)
    df.to_csv(DATASET_PATH, index=False)
    print(f"[OK] Training dataset saved to: {DATASET_PATH} ({len(df)} rows)")

    # 3. Train models
    print("\n[*] Training Dual-Pipeline ML Architecture:")
    print("   - Continuous GPA Regressor: Gradient Boosting Regressor")
    print("   - Academic Risk Classifier: Balanced Random Forest Classifier")
    predictor = StudentPerformancePredictor(auto_train=False)
    metrics = predictor.train(data=df)

    print("\n[Metrics] Model Evaluation Metrics:")
    print(f"   - R2 Score (GPA Fit):       {metrics['r2_score']:.4f}")
    print(f"   - RMSE:                     {metrics['rmse']:.4f}")
    print(f"   - MAE:                      {metrics['mae']:.4f}")
    print(f"   - Risk Classifier Accuracy: {metrics['accuracy'] * 100:.2f}%")
    print(f"   - Macro F1-Score:           {metrics['f1_macro']:.4f}")

    # 4. Save artifacts
    saved_path = predictor.save_artifacts(MODEL_PATH)
    file_size_kb = saved_path.stat().st_size / 1024
    print(f"\n[OK] Model artifact successfully serialized to: {saved_path} ({file_size_kb:.1f} KB)")
    print("[SUCCESS] Training pipeline completed successfully.")


if __name__ == "__main__":
    run_training()
