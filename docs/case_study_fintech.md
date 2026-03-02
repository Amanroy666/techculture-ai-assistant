# Case Study: AI-Powered Fraud Detection for a Fintech Lending Platform

## Client Background

**Industry**: Fintech (NBFC / Digital Lending)
**Company Size**: 150 employees, Series B funded
**Location**: Mumbai, India
**Engagement Duration**: 5 months
**Engagement Type**: Custom AI Development + MLOps Setup

*Client name withheld under NDA. Details have been generalized.*

---

## The Problem

The client was a fast-growing digital lending company offering personal and business loans through a mobile app. Their loan book had scaled from ₹50 Cr to ₹400 Cr over 18 months, and with that growth came an increase in fraudulent applications.

Their existing rule-based fraud detection system was:
- **Too rigid**: Flagging 23% of applications as suspicious (way too many false positives), causing legitimate customers to drop off
- **Too slow to adapt**: New fraud patterns emerged every few weeks, and updating rules required manual intervention from the risk team
- **Not explainable**: Regulators and internal audit teams couldn't understand why certain decisions were made

The fraud team was manually reviewing hundreds of flagged applications every day — a process that was expensive and didn't scale.

**Key metrics at project start:**
- False positive rate: 23% (too many legit customers blocked)
- Fraud slippage rate: 3.1% (fraud that got through undetected)
- Manual review volume: ~400 applications/day
- Average review time per application: 18 minutes

---

## Our Approach

### Phase 1: Data Audit & Problem Framing (Weeks 1–3)

We started by auditing 24 months of historical loan application data — approximately 180,000 records. Key observations:
- Data quality issues: 12% of records had missing fields or inconsistent formats
- Strong signal features identified: device fingerprint, application timing patterns, bureau score trajectory, employer verification status, and cross-referencing with known fraud patterns
- Discovered that ~60% of fraud came from organized rings (clusters of coordinated applications) rather than individual bad actors

We reframed the problem: instead of building one classification model, we needed a layered detection system that could catch both individual fraud and organized ring fraud.

### Phase 2: Model Development (Weeks 3–10)

**Layer 1 – Individual Application Scoring**
- Built a gradient boosted model (XGBoost) using 47 engineered features
- Trained on 18 months of labeled historical data (fraud/no-fraud)
- Used SMOTE for class imbalance handling (fraud was ~2.8% of applications)
- Achieved AUC-ROC of 0.94 on hold-out test set

**Layer 2 – Ring Detection**
- Built a graph-based anomaly detection model using shared identifiers (phone numbers, addresses, device IDs, employer details) across applications
- Used community detection algorithms to identify clusters of coordinated fraud applications
- Flagged entire clusters when enough nodes showed suspicious behavior

**Layer 3 – Explainability**
- Integrated SHAP values for every decision — outputs a plain-English explanation of why an application was flagged
- Built a dashboard for the risk team showing top contributing factors per application
- Enables easier audit trail for regulatory compliance

### Phase 3: MLOps Pipeline & Deployment (Weeks 10–18)

- Containerized models with Docker, deployed on GCP Cloud Run (serverless, scales to zero)
- Built a real-time scoring API (FastAPI) that integrates directly with the client's loan origination system
- Set up automated retraining pipeline using Airflow — model retrains every 30 days on new data
- Implemented model monitoring with Evidently AI — alerts when data drift is detected
- Prediction latency: p99 < 180ms at 200 concurrent requests

---

## Results (Measured 3 Months Post-Launch)

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| False Positive Rate | 23% | 7.2% | ↓ 69% |
| Fraud Slippage Rate | 3.1% | 0.8% | ↓ 74% |
| Manual Review Volume | ~400/day | ~95/day | ↓ 76% |
| Avg Review Time | 18 min | 8 min (SHAP explanations help) | ↓ 56% |
| Estimated Annual Fraud Losses Prevented | — | ₹3.2 Cr | — |

The reduction in false positives also improved customer experience — fewer legitimate customers were getting stuck in manual review, which reduced application drop-off rates.

---

## Technologies Used

- **ML**: Python, XGBoost, NetworkX (graph analysis), SHAP
- **Data Processing**: PySpark, Pandas
- **MLOps**: MLflow, Airflow, Docker, GCP Cloud Run
- **Monitoring**: Evidently AI, Prometheus, Grafana
- **API**: FastAPI
- **Database**: PostgreSQL, BigQuery

---

## Key Learnings

1. **Rule-based systems can't keep up with adaptive fraud.** ML models that retrain automatically on new data are far more resilient.
2. **Explainability isn't optional for fintech.** Regulators and internal teams need to understand decisions — black-box models create compliance risk.
3. **Reducing false positives is as important as catching fraud.** A model that's too aggressive hurts customer experience and business growth.
4. **Organizational change management matters.** The risk team initially resisted the new system. We ran training sessions and involved them in the model evaluation — their buy-in was critical to adoption.

---

## Client Quote

*"The Techculture.ai team didn't just build a model — they helped us think through the whole problem differently. The reduction in manual reviews alone saved us significant operational cost, and catching organized fraud rings was something we didn't even think was possible before."*
— VP of Risk, Client Company (name withheld)
