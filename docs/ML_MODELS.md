# ML Models & Training

## Model Registry
Table: `model_registry` tracks:
- `model_name`, `algorithm`, `version`, metrics (AUC, accuracy, precision, recall, F1), `is_active`
- `trained_by`, `trained_at`, `training_time`, `model_path`, `model_size_mb`

Active model is used by prediction UI; switch via `ModelManagementWidget`.

## Supported Models
- XGBoost, LightGBM, Logistic Regression, CatBoost, RandomForest
- Neural Network (TensorFlow/Keras)
- Ensembles: Voting, Stacking

## Artifacts
- Saved to `outputs/models/*.pkl` (TensorFlow can save H5/pb depending on implementation)
- Evaluation artifacts: `outputs/evaluation/*`

## Training Flow (Service)
- `ModelManagementService.train_model(...)` creates model, fits, computes metrics, persists artifact, and updates `model_registry`
- Data loading must be provided to service (X_train/y_train/X_test/y_test)

## Adding a New Model
1. Extend `_create_model` factory in `model_management_service.py`
2. Add metrics computation if special handling is needed
3. Update UI (`ModelManagementWidget`) to include new selector option
4. Seed/update `model_registry` if you want it listed immediately

## Comparing Models
- `compare_models(model_names, X_test, y_test)` returns metrics for a set of models
- UI shows comparison summary
