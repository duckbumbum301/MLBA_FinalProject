# Database Guide

MySQL 8.x with UTF8MB4. App creates DB if missing.

## Core Tables
- `user`: authentication with two roles (`User`, `Admin`), plus `full_name`, `email`, `last_login`, `is_active`
- `customers`: UCI credit card dataset fields (~46 columns inc. 41 features)
- `predictions_log`: tracks predictions with `user_id`, `model_version`, `confidence_score`, `cluster_id`
- `model_registry`: ML models, metrics (AUC, accuracy, precision, recall, F1), `is_active`, `trained_by`, `model_path`
- `customer_clusters`: clustering assignments with risk levels
- `data_quality_log`: outlier/quality issues
- `ai_chat_history`: chat transcripts with context type and timestamps

See SQL files under `database/credit_scoring/`.

## Migrations & Utilities
- `quick_db_update.py`: convenience migration/seed
- `update_database_schema.py`: comprehensive schema application
- `fix_roles.py`: converts legacy roles to new 2-role system

## Connection
`database/connector.py` handles connection, auto-create DB on errno 1049.
Config at `config/database_config.py`.

## Data Safety
- Parameterized queries
- Recommended: restricted DB user in production

