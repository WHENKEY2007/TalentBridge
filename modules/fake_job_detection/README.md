# Fake Job Posting Detection

**Assigned Lead:** Member 2  
**Module Identifier:** `modules.fake_job_detection`  
**Status:** Implemented — Initial ML Screening Version

## 1. Module Overview

The Fake Job Posting Detection module uses Natural Language Processing (NLP) and machine learning to screen job postings and help job seekers discover potentially legitimate listings.

Instead of requiring users to enter individual job details for prediction, the module automatically evaluates postings from a historical dataset and displays only those classified as legitimate by the model.

**Important:** The listings are historical demonstration data, not confirmed current vacancies. Model predictions are estimates and do not guarantee that a job is genuine.

## 2. Features Implemented

- Automatic screening of historical job postings.
- TF-IDF text feature extraction.
- Logistic Regression classification.
- Fraud probability estimation.
- Filtering of postings predicted as fraudulent.
- Searchable job listings.
- Expandable listing details, including descriptions, requirements, benefits, and company information.
- Saved model pipeline for reuse.
- Automated unit tests for model initialization and screening behaviour.

## 3. Interface Contract

TalentBridge AI loads this module through the `render()` function in `interface.py`.

```python
def render() -> None:
    # Display searchable, ML-screened job listings
    pass
```

The module preserves the existing `render()` contract and exports `FakeJobDetector` through `__init__.py`.

## 4. Machine Learning Architecture

### Algorithm

The initial implementation uses a Scikit-learn Pipeline containing:

1. **TF-IDF Vectorizer:** Converts job-posting text into numerical features.
2. **Logistic Regression:** Estimates whether a posting is legitimate or fraudulent.

The text fields used are:

- Job title
- Company profile
- Job description
- Requirements
- Benefits

The model uses a stratified 80/20 train-test split with a fixed random seed and class weighting to account for the imbalance between legitimate and fraudulent examples.

### Dataset

The model was trained using the `fake_job_postings.csv` dataset.

- Total records: 17,880
- Legitimate postings (`fraudulent = 0`): 17,014
- Fraudulent postings (`fraudulent = 1`): 866

### Initial Evaluation

On the held-out test split:

| Metric | Result |
|---|---:|
| Accuracy | 98.69% |
| Legitimate precision | 99.53% |
| Legitimate recall | 99.09% |
| Fraudulent precision | 83.51% |
| Fraudulent recall | 90.75% |

These results describe performance on the dataset's held-out split. They do not guarantee equivalent performance on new or real-world job postings.

## 5. Screening Logic

The `FakeJobDetector` class provides the following methods:

- `train(data=None)`: Trains and evaluates the model, then saves the pipeline.
- `load()`: Loads a previously saved model.
- `predict(features)`: Predicts the fraud probability for one posting.
- `screen_jobs(jobs)`: Returns only postings with a predicted fraud probability below `0.5`.

The screening threshold is currently fixed at `0.5`. Postings with a fraud probability of `0.5` or higher are excluded from the displayed results.

The Streamlit interface loads the trained model, screens the historical dataset, and provides a search box and expandable listing details.

## 6. Setup and Execution

Run these commands from the TalentBridge repository root.

### Step 1: Install dependencies

Activate your existing virtual environment, if applicable, and install the repository dependencies:

```bash
python -m pip install -r requirements.txt
```

### Step 2: Add the dataset

Place `fake_job_postings.csv` at:

```text
modules/fake_job_detection/data/fake_job_postings.csv
```

The dataset and generated model artifact are excluded from Git by the repository's ignore rules. Obtain the dataset through the project's approved data-sharing process before running the module on another machine.

### Step 3: Train the model

If no saved model exists, train it from the repository root:

```bash
python -c "from modules.fake_job_detection.model import FakeJobDetector; print(FakeJobDetector().train())"
```

The trained pipeline is saved at:

```text
modules/fake_job_detection/artifacts/fake_job_model.joblib
```

### Step 4: Run TalentBridge AI

```bash
python -m streamlit run app.py
```

Open the local URL shown in the terminal and navigate to the Fake Job Detection module.

## 7. Automated Tests

Run the module's tests from the repository root:

```bash
python -m pytest modules/fake_job_detection/tests/ -v
```

The current test suite checks:

- Detector initialization.
- Prediction before training or loading.
- Screening before training or loading.
- Filtering of postings whose predicted fraud probability is `0.5` or higher.

The current test suite has **4 passing tests**.

## 8. Directory Structure

```text
modules/fake_job_detection/
├── __init__.py
├── interface.py
├── interface.py.bak
├── model.py
├── model.py.bak
├── README.md
├── data/
│   ├── .gitkeep
│   └── fake_job_postings.csv
├── artifacts/
│   └── .gitkeep
└── tests/
    ├── .gitkeep
    └── test_fake_job_detection.py
```

The `.bak` files are temporary local backups and should be removed before committing. The CSV dataset and generated model artifact are excluded from Git.

## 9. Future Improvements

- Evaluate performance on an independent dataset.
- Tune the screening threshold based on validation results and the cost of false positives and false negatives.
- Explore additional structured features, such as employment type and company-logo presence.
- Add stronger safeguards against misleading or suspicious job postings.
- Improve dataset versioning and model reproducibility.

## 10. Development Ownership

This module is maintained by Member 2. Changes should remain within `modules/fake_job_detection/` unless the team agrees otherwise. Do not modify the shared application entry point, shared utilities, or other members' modules as part of this work.