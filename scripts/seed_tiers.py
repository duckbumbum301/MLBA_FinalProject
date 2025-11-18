import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from config.database_config import DatabaseConfig
from database.connector import DatabaseConnector
from services.query_service import QueryService

def main():
    cfg = DatabaseConfig.default()
    db = DatabaseConnector(cfg)
    if not db.connect():
        print("DB connect failed")
        return
    qs = QueryService(db)

    def count_ge_lt(ge: float, lt: float) -> int:
        r = db.fetch_one(
            "SELECT COUNT(*) FROM predictions_log WHERE probability >= %s AND probability < %s",
            (ge, lt),
        )
        return int(r[0]) if r else 0

    def count_ge(ge: float) -> int:
        r = db.fetch_one(
            "SELECT COUNT(*) FROM predictions_log WHERE probability >= %s",
            (ge,),
        )
        return int(r[0]) if r else 0

    inserted = 0
    if count_ge_lt(0.4, 0.6) == 0:
        qs.save_prediction_log(None, "XGBoost", 0, 0.48, {})
        inserted += 1
    if count_ge_lt(0.6, 0.8) == 0:
        qs.save_prediction_log(None, "XGBoost", 1, 0.72, {})
        inserted += 1
    if count_ge(0.8) == 0:
        qs.save_prediction_log(None, "XGBoost", 1, 0.89, {})
        inserted += 1

    print(f"Seeded {inserted} records")

    def show_tier(name: str, tier_key: str):
        rows = qs.get_customers_by_tier(tier_key, limit=20)
        probs = [round(float(r.get("probability")), 4) for r in rows][:10]
        print(f"{name}: {len(rows)} records, probs={probs}")

    show_tier("Trung bình", "trung bình")
    show_tier("Cao", "cao")
    show_tier("Rất cao", "rất cao")

    db.close()

if __name__ == "__main__":
    main()