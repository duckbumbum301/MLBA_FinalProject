# Services API

This document summarizes the primary services for AI IDEs and developers.

## `services/gemini_service.py` — GeminiService
- Purpose: Chat with Gemini for explanations, reports, comparisons
- Init: `GeminiService(db_connector: DatabaseConnector, user_id: int)`
- Key methods:
  - `is_available() -> bool`
  - `send_message(message: str, context: Optional[dict] = None, context_type: str = "General") -> str`
  - `explain_prediction(customer_data: dict, prediction_result: dict) -> str`
  - `compare_models(customer_data: dict, predictions: dict) -> str`
  - `generate_report(stats: dict, report_type: str) -> str`
  - `get_chat_history(limit: int = 50) -> list`
  - `clear_chat_history() -> None`
- Config: `config/gemini_config.py` with `MODEL_NAME = "gemini-2.5-flash"`

## `services/model_management_service.py` — ModelManagementService
- Purpose: Manage training, activation, deletion, and comparison of models
- Key methods:
  - `get_all_models() -> list`
  - `get_active_model() -> dict`
  - `set_active_model(model_name: str, username: str) -> bool`
  - `train_model(model_name: str, X_train, y_train, X_test, y_test, username: str, progress_callback=None) -> dict`
  - `delete_model(model_name: str) -> bool`
  - `load_model(model_name: str)`
  - `compare_models(model_names: list, X_test, y_test) -> dict`
- Models supported: LightGBM, CatBoost, RandomForest, Logistic, NeuralNet, Voting, Stacking, XGBoost
- Persistence: `outputs/models/*.pkl`; metadata in `model_registry`

## `services/data_quality_service.py` — DataQualityService
- Purpose: Outlier detection and customer clustering
- Key methods:
  - `detect_outliers(method: str = 'IsolationForest'|'LOF'|'ZScore', contamination: float = 0.05) -> dict`
  - `cluster_customers(algorithm: str = 'KMeans'|'DBSCAN', n_clusters: int = 4) -> dict`
- Writes to: `customer_clusters`, `data_quality_log`
- Uses: `sklearn` (IsolationForest, LocalOutlierFactor, KMeans, DBSCAN, PCA, StandardScaler), `scipy.stats`

## `services/query_service.py`
- Purpose: Read-only queries and lightweight data retrieval for UI
- Pattern: All DB I/O via `DatabaseConnector`

## Notes
- All services assume an active DB connection
- Prefer passing `user_id` from UI for auditing (where applicable)
