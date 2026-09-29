# UPI Fraud Detection System

A production-style machine learning web application to detect and analyze potentially fraudulent UPI (Unified Payments Interface) transactions using behavioral telemetry, contextual anomaly detection, and classification algorithms.

> **Important Educational Notice:** This application provides probabilistic fraud-risk indications for decision-support, research, and educational purposes. It does not provide an absolute guarantee of fraud or legitimacy.

---

## Architecture Overview

```
upi-fraud-detection/
│
├── frontend/                     # React + Vite + TypeScript Web Client
│   ├── src/
│   │   ├── components/           # Reusable UI components (StatCard, RiskBadge, etc.)
│   │   ├── pages/                # Page route views (Dashboard, Simulator, Explorer, Alerts, Model)
│   │   ├── layouts/              # MainLayout with header, navigation, and banners
│   │   ├── hooks/                # Custom React hooks (useHealth, etc.)
│   │   ├── services/             # Type-safe API client
│   │   ├── types/                # Strict TypeScript interfaces matching backend models
│   │   ├── utils/                # Formatters (currency, dates, risk styling)
│   │   ├── App.tsx               # React Router configuration
│   │   └── main.tsx              # React entry point
│   ├── package.json              # Frontend dependencies (React, Recharts, Lucide, Tailwind)
│   ├── tailwind.config.js        # Tailwind CSS design system
│   ├── tsconfig.json             # TypeScript strict mode configuration
│   ├── vite.config.ts            # Vite bundler configuration
│   └── .env.example              # Frontend environment variables
│
├── backend/                      # Python FastAPI REST API & ML Service
│   ├── app/
│   │   ├── main.py               # FastAPI application entry point with CORS
│   │   ├── routes/               # Modular REST endpoints
│   │   │   ├── health.py         # System health & database connection status
│   │   │   ├── predict.py        # Fraud inference & transaction simulation
│   │   │   ├── transactions.py   # Transaction history & audit log queries
│   │   │   ├── alerts.py         # Fraud alerts queue & analyst dispositions
│   │   │   ├── analytics.py      # Aggregated dashboard metrics & trends
│   │   │   └── model.py          # Model evaluation metrics & feature definitions
│   │   ├── services/             # Core business & database services
│   │   │   ├── db_service.py     # Database adapter (Supabase PostgreSQL + SQLite)
│   │   │   └── prediction_service.py # Model inference & explainability engine
│   │   ├── models/               # Internal data structures
│   │   │   └── db_models.py
│   │   ├── schemas/              # Strict Pydantic v2 validation models
│   │   │   ├── transaction.py
│   │   │   ├── alert.py
│   │   │   └── analytics.py
│   │   └── utils/                # Constants and logging helpers
│   │       ├── constants.py
│   │       └── logger.py
│   ├── ml/                       # Machine Learning Pipeline
│   │   ├── preprocess.py         # Cleaning, outlier clipping, scaling
│   │   ├── features.py           # Domain behavioral feature engineering & explainability
│   │   ├── train.py              # Model training (SMOTE, RF vs XGBoost, Stratified CV)
│   │   ├── evaluate.py           # Classification metrics (ROC-AUC, PR-AUC, Confusion Matrix)
│   │   └── predict.py            # Standalone inference helper
│   ├── config.py                 # Central backend configuration
│   ├── requirements.txt          # Python dependencies
│   ├── run.py                    # Server startup script
│   └── .env.example              # Backend environment template
│
├── data/
│   ├── raw/                      # Raw datasets (X_train, X_test, y_train, y_test)
│   └── processed/                # Preprocessed & scaled feature matrices
│
├── models/                       # Persisted ML artifacts (model.pkl, scaler.pkl, metrics.json)
├── notebooks/                    # Research and EDA notebooks
├── reports/                      # Evaluation reports & diagnostic figures
├── README.md                     # Project documentation
└── .gitignore                    # Git ignore rules
```

---

## Machine Learning Model

- **Champion Algorithm:** XGBoost Classifier (selected over Random Forest through 5-Fold Stratified Cross-Validation)
- **Class Imbalance Handling:** SMOTE (Synthetic Minority Over-sampling Technique)
- **Performance Metrics (Held-Out Test Set):**
  - **ROC-AUC:** `0.9965`
  - **PR-AUC (Average Precision):** `0.9862`
  - **Recall (Fraud Detection Rate):** `93.73%`
  - **Precision:** `90.83%`
  - **F1-Score:** `0.9226`
  - **False Positive Rate:** `1.97%`

---

## Running Frontend and Backend Independently

### 1. Running the Backend

From the project root:

```bash
# Activate virtual environment
.\venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux/Mac

# Install backend dependencies
pip install -r backend/requirements.txt

# Start the FastAPI server
python backend/run.py
```

The backend server runs on `http://127.0.0.1:8000`:
- **API Health Check:** `http://127.0.0.1:8000/api/health`
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`
- **OpenAPI JSON:** `http://127.0.0.1:8000/openapi.json`

### 2. Running the Frontend

In a separate terminal window:

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start Vite development server
npm run dev
```

The React frontend starts at `http://localhost:5173`. It connects automatically to `http://localhost:8000/api`.

---

## Database Configuration

The system supports **Supabase PostgreSQL** with an automatic **SQLite fallback**:
- To connect to your Supabase instance, set `SUPABASE_URL` and `SUPABASE_KEY` in `backend/.env` (see `backend/.env.example`).
- If no Supabase credentials are provided, the backend operates via local SQLite (`data/upi_fraud.db`) with zero configuration required.
