# 🛡️ Fraud Detection Model Development – Rule-Based Labeling + Supervised ML

This project demonstrates how to build a production-inspired fraud detection model by combining rule-based labeling with supervised machine learning. It walks through the full data science pipeline: from behavioral feature engineering, to intuitive label creation, to model training, evaluation, and export.

---

## 🧭 Project Objectives

- Enrich transaction data with behavioral and contextual risk signals.
- Design a transparent, rule-based fraud scoring system.
- Generate weakly-supervised fraud labels using risk scores.
- Train a machine learning model to detect fraud using enriched features.
- Evaluate model performance using industry-relevant metrics.
- Save the model for integration into a fraud scoring pipeline.

---

## 📂 Contents

| Section | Description |
|--------|-------------|
| [Feature Engineering](#-feature-engineering) | Add behavioral context to raw transactions |
| [Rule-Based Scoring & Labeling](#-rule-based-scoring--labeling) | Generate labels using a custom fraud score |
| [Data Preparation](#-data-preparation) | Encode and split the data |
| [Model Training & Evaluation](#-model-training--evaluation) | Train model, analyze features, assess performance |
| [Model Export](#-model-export) | Save trained model for deployment |
| [Next Steps](#-next-steps--improvements) | Opportunities for future improvement |

---

## 🧪 Feature Engineering

### 🔍 Goal:
Enrich transactions with signals derived from customer login behavior and profile context.

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
Each transaction is scored based on features like:
- Failed logins
- Geo mismatch
- Risky merchants
- Fraud history
- Time-based login anomalies
- Z-score outliers in amount

Each rule contributes a weight (score). If a transaction's total score exceeds a defined threshold (`RISK_THRESHOLD = 5`), it's labeled as fraud (`label = 1`).

### ✅ Output:
- `label`: Final target column used for model training
- `risk_score`: Transparent risk score
- `flags`: List of triggered fraud rules

---

## 🧹 Data Preparation

### 🔢 Feature Set:
Selected meaningful features:
- Behavioral: `failed_logins_24h`, `night_login`, etc.
- Profile: `customer_has_fraud_history`, `customer_past_fraud_count`
- Context: `geo_mismatch`, `is_high_risk_merchant`, `transaction_amount`

### 🔄 Encoding:
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
