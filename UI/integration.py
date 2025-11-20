import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent
project_root = base_dir.parent  # MLBA_FinalProject
sys.path.insert(0, str(project_root))

from config.database_config import DatabaseConfig
from database.connector import DatabaseConnector
from services.query_service import QueryService
from services.ml_service import MLService

def get_db_connector() -> DatabaseConnector:
    cfg = DatabaseConfig.default()
    db = DatabaseConnector(cfg)
    db.connect()
    return db

def get_query_service(db: DatabaseConnector) -> QueryService:
    return QueryService(db)

def get_ml_service(model_name: str = 'LightGBM') -> MLService:
    return MLService(model_name=model_name)
