# Student Performance Prediction & Academic Risk Engine

**Assigned Lead:** Member 3  
**Module Identifier:** `modules.student_performance`  
**Status:** ✅ Production Ready  

---

## 1. Module Overview
Predicts academic outcomes, GPA trajectories, and graduation/retention risk based on historical learning metrics, lecture attendance, LMS portal engagement, and independent study behaviors.

This module operates independently within the **TalentBridge AI** platform under the Module Sandbox Policy.

---

## 2. Interface Contract
TalentBridge AI dynamically loads this module via the `render()` function in `interface.py`:

```python
def render() -> None:
    """
    Renders Streamlit widgets and invokes StudentPerformancePredictor.
    Takes 0 arguments and returns None.
    """
```

---

## 3. Architecture & Machine Learning Pipelines

### Dual ML Pipeline:
1. **Continuous GPA Regressor:**
   - Model: `GradientBoostingRegressor(n_estimators=120, learning_rate=0.08, max_depth=4, subsample=0.85)`
   - Preprocessing: `StandardScaler`
   - Target: End-of-Semester GPA (1.0 to 4.0)
   - Performance: $R^2 \approx 0.9327$, $\text{RMSE} \approx 0.1094$, $\text{MAE} \approx 0.0770$

2. **Categorical Academic Risk Classifier:**
   - Model: `RandomForestClassifier(n_estimators=120, max_depth=6, class_weight='balanced')`
   - Classes: `On-Track`, `Moderate Risk`, `At-Risk`
   - Accuracy: $\approx 97.67\%$, Macro F1: $\approx 0.9788$

### Key Inputs
- **Past Semester GPAs:** Semester 1, 2, and 3 GPAs (0.0 – 4.0 scale)
- **Midterm Exam Score:** Core subject assessment (0 – 100%)
- **Attendance Rate:** Lecture attendance percentage (0 – 100%)
- **LMS Engagement:** Weekly portal hours and weekly logins count
- **Assignment Submission Punctuality:** On-time homework percentage (0 – 100%)
- **Independent Study Hours:** Dedicated study time outside lectures (Hours/Week)
- **Extracurricular Index:** Co-curricular activity score (0.0 – 10.0 scale)

### Key Outputs
- **Predicted Final GPA & Velocity:** Forecasted GPA with positive/negative delta relative to Semester 3
- **Academic Standing & Grade Band:** First Class with Distinction, Dean's Honors, Good Standing, Academic Warning, or Probation
- **Risk Status & Probability Distribution:** Probabilities for On-Track, Moderate Risk, and At-Risk
- **Graduation Retention Index:** Composite percentage (0 – 100%)
- **Key Academic Factor Weights:** Importance attributions across all 10 features
- **Actionable Interventions:** Tactical recommendations prioritized by severity
- **What-If Sandbox:** Real-time simulation of attendance and study hour improvements

---

## 4. Directory Structure
```
modules/student_performance/
├── __init__.py          # Exports render() and StudentPerformancePredictor
├── interface.py         # Streamlit UI contract implementation
├── model.py             # Dual-pipeline ML model & synthetic dataset generator
├── config.py            # Feature schemas, bounds, grade bands & sample personas
├── train.py             # Standalone training & evaluation pipeline script
├── README.md            # Module documentation
├── data/
│   ├── .gitkeep         # Tracked directory anchor
│   └── student_academic_records.csv  # Generated dataset (1,500 records)
├── artifacts/
│   ├── .gitkeep         # Tracked directory anchor
│   └── student_performance_model.joblib # Serialized model pipeline (~235 KB)
└── tests/
    ├── .gitkeep
    └── test_student_performance.py   # Complete unit test suite
```

---

## 5. Verification & Testing
To train the model and generate fresh artifacts:
```bash
python modules/student_performance/train.py
```

To run the unit test suite:
```bash
python -m pytest modules/student_performance/tests/ -v
```
