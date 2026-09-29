"""
train.py - Reproducible training and model selection pipeline for UPI Fraud Detection.
Trains and compares 4 candidate architectures:
  1. Logistic Regression
  2. Decision Tree
  3. Random Forest
  4. Gradient Boosting
Selects champion model using ROC-AUC and F1-score (not accuracy alone).
Saves champion model using joblib.
"""

from typing import Dict, Any
from pathlib import Path
import json
import joblib
import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

from ml.preprocessing import full_preprocessing_pipeline, ARTIFACTS_DIR, PROJECT_ROOT
from ml.evaluate import (
    compute_comprehensive_metrics,
    plot_confusion_matrix,
    plot_comparative_roc_curves,
    plot_feature_importance,
    save_evaluation_report,
)

RANDOM_SEED = 42


def train_logistic_regression(X_train: pd.DataFrame, y_train: pd.Series) -> LogisticRegression:
    """Candidate 1: Baseline Linear Classifier with balanced weighting."""
    print("  [1/4] Training Logistic Regression...")
    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        C=1.0,
        random_state=RANDOM_SEED,
    )
    model.fit(X_train, y_train)
    return model


def train_decision_tree(X_train: pd.DataFrame, y_train: pd.Series) -> DecisionTreeClassifier:
    """Candidate 2: Non-linear Tree Classifier with regularized depth."""
    print("  [2/4] Training Decision Tree Classifier...")
    model = DecisionTreeClassifier(
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=4,
        class_weight="balanced",
        random_state=RANDOM_SEED,
    )
    model.fit(X_train, y_train)
    return model


def train_random_forest(X_train: pd.DataFrame, y_train: pd.Series) -> RandomForestClassifier:
    """Candidate 3: Ensemble Bagging Classifier."""
    print("  [3/4] Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    return model


def train_gradient_boosting(X_train: pd.DataFrame, y_train: pd.Series) -> GradientBoostingClassifier:
    """Candidate 4: Ensemble Boosting Classifier (Sequential error gradient minimization)."""
    print("  [4/4] Training Gradient Boosting Classifier...")
    model = GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.08,
        max_depth=5,
        subsample=0.8,
        random_state=RANDOM_SEED,
    )
    model.fit(X_train, y_train)
    return model


def run_cross_validation(model, X: pd.DataFrame, y: pd.Series, cv: int = 5) -> float:
    """Runs 5-Fold Stratified Cross-Validation on training data using ROC-AUC."""
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=RANDOM_SEED)
    scores = cross_val_score(model, X, y, cv=skf, scoring="roc_auc", n_jobs=-1)
    return float(scores.mean())


def train_and_compare_models() -> Dict[str, Any]:
    """
    Executes end-to-end model training, comparative benchmark, and champion export.
    """
    # 1. Preprocess dataset
    X_train, y_train, X_test, y_test, feature_names = full_preprocessing_pipeline()

    # 2. Train all 4 candidate models
    print("\n" + "=" * 65)
    print("   TRAINING MULTIPLE CANDIDATE ALGORITHMS")
    print("=" * 65)

    candidates = {
        "Logistic Regression": train_logistic_regression(X_train, y_train),
        "Decision Tree": train_decision_tree(X_train, y_train),
        "Random Forest": train_random_forest(X_train, y_train),
        "Gradient Boosting": train_gradient_boosting(X_train, y_train),
    }

    # 3. Evaluate each model on unseen test set & cross-validation
    print("\n" + "=" * 65)
    print("   MODEL COMPARISON & BENCHMARK ON UNSEEN TEST DATA")
    print("=" * 65)

    comparison_results: Dict[str, Dict[str, Any]] = {}

    header = f"{'Model':<22} | {'Accuracy':<8} | {'Precision':<9} | {'Recall':<8} | {'F1-Score':<8} | {'ROC-AUC':<8}"
    print(header)
    print("-" * len(header))

    for name, model in candidates.items():
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None

        metrics = compute_comprehensive_metrics(y_test, y_pred, y_prob)
        cv_auc = run_cross_validation(model, X_train, y_train, cv=5)
        metrics["cv_roc_auc"] = round(cv_auc, 4)
        comparison_results[name] = metrics

        print(
            f"{name:<22} | "
            f"{metrics['accuracy']:<8.4f} | "
            f"{metrics['precision']:<9.4f} | "
            f"{metrics['recall']:<8.4f} | "
            f"{metrics['f1_score']:<8.4f} | "
            f"{metrics['roc_auc']:<8.4f}"
        )

    # 4. Champion selection: Select using ROC-AUC and F1-score (NOT accuracy alone!)
    champion_name = max(
        candidates.keys(),
        key=lambda k: (comparison_results[k]["roc_auc"], comparison_results[k]["f1_score"]),
    )
    champion_model = candidates[champion_name]
    champion_metrics = comparison_results[champion_name]

    print("\n" + "=" * 65)
    print(f">>> SELECTED CHAMPION MODEL: {champion_name}")
    print(f"    Test ROC-AUC:  {champion_metrics['roc_auc']:.4f}")
    print(f"    Test F1-Score: {champion_metrics['f1_score']:.4f}")
    print(f"    Fraud Recall:  {champion_metrics['recall']:.4f} (Detection Rate)")
    print(f"    Precision:     {champion_metrics['precision']:.4f}")
    print(f"    Accuracy:      {champion_metrics['accuracy']:.4f}")
    print("=" * 65)

    # 5. Save Final Model using joblib
    final_model_path = ARTIFACTS_DIR / "final_model.joblib"
    joblib.dump(champion_model, final_model_path)
    print(f"\n[Persistence] Final model saved to {final_model_path}")

    # Also sync to models/model.pkl and metrics.json for backend compatibility
    backend_model_path = PROJECT_ROOT / "models" / "model.pkl"
    backend_model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(champion_model, backend_model_path)

    backend_metrics_path = PROJECT_ROOT / "models" / "metrics.json"
    with open(backend_metrics_path, "w") as f:
        champion_metrics["model_name"] = champion_name
        json.dump(champion_metrics, f, indent=2)

    # 6. Generate Figures & Artifacts
    # Comparative ROC Curves
    plot_comparative_roc_curves(candidates, X_test, y_test, ARTIFACTS_DIR / "roc_curves.png")

    # Confusion Matrix for Champion
    y_test_pred = champion_model.predict(X_test)
    plot_confusion_matrix(y_test, y_test_pred, champion_name, ARTIFACTS_DIR / "confusion_matrix.png")

    # Feature Importance for Champion
    plot_feature_importance(champion_model, feature_names, ARTIFACTS_DIR / "feature_importance.png")

    # Evaluation Report JSON & Markdown
    save_evaluation_report(comparison_results, champion_name, ARTIFACTS_DIR / "model_evaluation_report.json")

    return {
        "champion_name": champion_name,
        "metrics": champion_metrics,
        "all_models": comparison_results,
    }


if __name__ == "__main__":
    train_and_compare_models()
