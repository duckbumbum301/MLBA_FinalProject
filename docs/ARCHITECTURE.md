# Architecture Overview

The application follows a layered architecture with clear boundaries:

- UI layer (`ui/`): PyQt6 widgets and MainWindow wrapper
- Services layer (`services/`): Business logic (AI chat, model mgmt, data quality, queries)
- Data access layer (`database/`): MySQL connector and SQL scripts
- Domain models (`models/`): User and domain entities
- Config layer (`config/`): DB and Gemini settings
- Scripts/Tests: Launchers and utilities in `tests/` and root

## Directory Layout (key parts)
```
config/
  database_config.py
  gemini_config.py
database/
  connector.py
  credit_scoring/*.sql
models/
  user.py
services/
  gemini_service.py
  model_management_service.py
  data_quality_service.py
  query_service.py
ui/
  MainWindowEx.py
  AIAssistantWidget.py
  ModelManagementWidget.py
  SystemManagementWidget.py
  PredictionTabWidget.py
  DashboardTabWidget.py
outputs/
  models/
  evaluation/
``` 

## Data Flow (high-level)
1. UI widgets invoke service methods (e.g., `ModelManagementService.train_model`)
2. Services fetch/store via `DatabaseConnector` (parameterized queries)
3. Models serialized in `outputs/models`; registry rows in `model_registry`
4. AI chat flows through `GeminiService` (optional if API key set)

## Permissions Model
- `models/user.py` provides helpers: `is_admin()`, `has_access_to_model_management()`, etc.
- `MainWindowEx.setup_tabs()` adds tabs based on role.

## Extending
- New UI tab: create a widget in `ui/`, import, and mount in `MainWindowEx`
- New service: place in `services/`, keep DB access in service or add repository module
- New table: add SQL in `database/credit_scoring/`, update services accordingly

