# UPI Fraud Detection — Results Summary

## Dataset
| Split    | Samples | Features |
|----------|---------|----------|
| Train    | TBD     | 18       |
| Test     | TBD     | 18       |

## Model Performance

> Fill in after running `notebooks/04_evaluation.ipynb`

| Metric    | Random Forest | XGBoost |
|-----------|--------------|---------|
| Accuracy  | -            | -       |
| Precision | -            | -       |
| Recall    | -            | -       |
| F1-Score  | -            | -       |
| ROC-AUC   | -            | -       |

## Best Model
- **Model:** TBD
- **ROC-AUC:** TBD

## Key Observations
- Top fraud-correlated features: TBD (see `reports/figures/feature_importance.png`)
- Fraud rate in training set: TBD%
- Optimal decision threshold: TBD

## Generated Figures
| File | Description |
|------|-------------|
| `figures/class_distribution.png`   | Fraud vs Legit class counts |
| `figures/feature_distributions.png` | Per-feature histograms by class |
| `figures/correlation_heatmap.png`  | Feature correlation matrix |
| `figures/boxplots.png`             | Box plots of key features |
| `figures/confusion_matrix.png`     | Confusion matrix on test set |
| `figures/roc_curve.png`            | ROC curve with AUC score |
| `figures/feature_importance.png`   | Top feature importances |
| `figures/threshold_analysis.png`   | Precision/Recall/F1 vs threshold |
