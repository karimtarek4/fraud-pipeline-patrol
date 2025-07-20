# 🎯 ML Fraud Detection Model

End-to-end machine learning pipeline for fraud detection: feature engineering, labeling, training, and evaluation.

---

## Objectives

- Enrich transaction data with behavioral infered data.
- Design a rule-based scoring system.
- Train a machine learning model to detect fraud using enriched features.
- Evaluate model performance.
- Save the model for integration.

---

## 📂 Notebook Contents

| Section | Description |
|--------|-------------|
| [Data Preparation](#-data-preparation) | Encode and split the data |
| [Model Training & Evaluation](#-model-training--evaluation) | Train model, analyze features, assess performance |
| [Model Export](#-model-export) | Save trained model for deployment |

---

## 🧪 Feature Engineering

### ⚙️ Features Created:
- `failed_logins_24h`: Number of failed logins in the 24h window before a transaction
- `geo_mismatch`: Whether the transaction location differs from the customer’s home location
- `odd_hours`: Last login happened between 12AM and 6AM
- `weekend_login`: Last login occurred on a weekend
- `night_login`: Custom signal for login during night hours

### 🛠️ How:
We joined each transaction with prior login events (same customer, before transaction) and engineered features from them. This gives us a richer behavioral context per transaction.

---

## 🏷️ Rule-Based Scoring & Labeling

### 🔍 Problem:
We had no real fraud labels. Instead of labeling fraud randomly, we built a scoring system based on domain logic.

### 📐 Logic:
Each transaction is scored based on selected features mentioned above. 

Each rule contributes a weight (score). If a transaction's total score exceeds a defined threshold (`RISK_THRESHOLD = 5`), it's labeled as fraud (`label = 1`).

### ✅ Output:
- `label`: Final target column used for model training
- `risk_score`: Transparent risk score

---

## 🧹 Data Preparation

### 🔄 Encoding For Categorical Feature.
Encoded `customer_risk_level` with ordinal values:
- `Low` → 0
- `Medium` → 1
- `High` → 2

### 🧪 Train/Test Split:
Used `train_test_split()` with `stratify=y` to preserve fraud ratio.
- 80% for training
- 20% for evaluation

---

## 🌲 Model Training & Evaluation

### 🧠 Trial 1 – Baseline Random Forest
- Model: `RandomForestClassifier(n_estimators=100, max_depth=5)`
- Features: All selected + encoded
- Observation: `customer_risk_level` had 0% feature importance

### 🔁 Trial 2 – Refined Model
- Dropped `customer_risk_level`
- Added `class_weight='balanced'` to handle fraud imbalance
- Retrained the model

### 📊 Feature Importance Highlights:
- Top features: `is_high_risk_merchant`, `geo_mismatch`, `night_login`
- Time-based behavior and risk flags dominated
- `transaction_amount` and fraud history had moderate impact

### 🧾 Evaluation Results:
| Metric     | Score |
|------------|-------|
| Accuracy   | 0.99  |
| Precision  | 0.97  |
| Recall     | 0.97  |
| F1 Score   | 0.97  |

- **Precision (0.97)**: Very few false alarms
- **Recall (0.97)**: Almost all real frauds were caught
- **F1 Score (0.97)**: Well-balanced performance

---

## 💾 Model Export

The final trained model was saved using `joblib`:

```python
joblib.dump(model_refined, "fraud_model.pkl")
