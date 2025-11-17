# UI Guide (PyQt6)

Main window wrapper: `ui/MainWindowEx.py`

## Tabs by Role
- User: 
  - `📊 Dự Báo Rủi Ro` → `PredictionTabWidget`
  - `📈 Dashboard` → `DashboardTabWidget`
  - `🤖 AI Trợ Lý` → `AIAssistantWidget`
- Admin (adds):
  - `🎯 Quản Lý ML` → `ModelManagementWidget`
  - `⚙️ Hệ Thống` → `SystemManagementWidget`

## Key Widgets
- `PredictionTabWidget(user, query_service)`
  - Shows input fields and prediction output
  - Admin may see model selector if logic enabled in widget
- `DashboardTabWidget()`
  - Shows evaluation charts/metrics (loaded from `outputs/evaluation` if present)
- `AIAssistantWidget(user, db_connector)`
  - Chat UI, disables input if Gemini not configured
- `ModelManagementWidget(user, db_connector)`
  - Table of models (metrics, status), actions: Train, Set Active, Delete, Compare
- `SystemManagementWidget(user, db_connector)`
  - Outlier detection + customer clustering with progress dialogs

## Signals/Slots
- Button clicks are connected in each widget (`clicked.connect(...)`)
- Long-running tasks offloaded to QThread workers in `SystemManagementWidget`

## Styling
- Light CSS-style tweaks are embedded in widgets via `setStyleSheet`

## Extending UI
- Create a new `QWidget` under `ui/`
- Import and mount in `MainWindowEx.setup_tabs()` based on role
- Keep long tasks in QThread to avoid UI freeze
