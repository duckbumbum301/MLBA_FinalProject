"""
Query Service
Service xử lý truy vấn database (customers, predictions_log)
"""
import json
from typing import List, Optional, Dict
from datetime import datetime
from database.connector import DatabaseConnector
from models.customer import Customer


class QueryService:
    """
    Service quản lý truy vấn dữ liệu khách hàng và predictions log
    """
    
    def __init__(self, db_connector: DatabaseConnector):
        """
        Khởi tạo QueryService
        
        Args:
            db_connector: Instance DatabaseConnector
        """
        self.db = db_connector
        try:
            from pathlib import Path
            self._project_root = Path(__file__).resolve().parents[1]
            self._eval_path = self._project_root / 'outputs' / 'evaluation' / 'evaluation_data.npz'
        except Exception:
            self._eval_path = None
    
    def save_customer(self, customer: Customer) -> Optional[int]:
        """
        Lưu thông tin khách hàng vào database (41 fields)
        
        Args:
            customer: Instance Customer
        
        Returns:
            Customer ID nếu thành công, None nếu thất bại
        """
        query = """
            INSERT INTO customers (
                customer_name, customer_id_card,
                LIMIT_BAL, SEX, EDUCATION, MARRIAGE, AGE,
                PAY_0, PAY_2, PAY_3, PAY_4, PAY_5, PAY_6, PAY_7, PAY_8, PAY_9, PAY_10, PAY_11, PAY_12,
                BILL_AMT1, BILL_AMT2, BILL_AMT3, BILL_AMT4, BILL_AMT5, BILL_AMT6,
                BILL_AMT7, BILL_AMT8, BILL_AMT9, BILL_AMT10, BILL_AMT11, BILL_AMT12,
                PAY_AMT1, PAY_AMT2, PAY_AMT3, PAY_AMT4, PAY_AMT5, PAY_AMT6,
                PAY_AMT7, PAY_AMT8, PAY_AMT9, PAY_AMT10, PAY_AMT11, PAY_AMT12
            ) VALUES (
                %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
        """
        
        params = (
            customer.customer_name, customer.customer_id_card,
            customer.LIMIT_BAL, customer.SEX, customer.EDUCATION, customer.MARRIAGE, customer.AGE,
            customer.PAY_0, customer.PAY_2, customer.PAY_3, customer.PAY_4, customer.PAY_5, customer.PAY_6,
            customer.PAY_7, customer.PAY_8, customer.PAY_9, customer.PAY_10, customer.PAY_11, customer.PAY_12,
            customer.BILL_AMT1, customer.BILL_AMT2, customer.BILL_AMT3, 
            customer.BILL_AMT4, customer.BILL_AMT5, customer.BILL_AMT6,
            customer.BILL_AMT7, customer.BILL_AMT8, customer.BILL_AMT9,
            customer.BILL_AMT10, customer.BILL_AMT11, customer.BILL_AMT12,
            customer.PAY_AMT1, customer.PAY_AMT2, customer.PAY_AMT3,
            customer.PAY_AMT4, customer.PAY_AMT5, customer.PAY_AMT6,
            customer.PAY_AMT7, customer.PAY_AMT8, customer.PAY_AMT9,
            customer.PAY_AMT10, customer.PAY_AMT11, customer.PAY_AMT12
        )
        
        success = self.db.execute_query(query, params)
        
        if success:
            # Lấy ID vừa insert
            result = self.db.fetch_one("SELECT LAST_INSERT_ID()")
            if result:
                customer_id = result[0]
                print(f"✓ Đã lưu customer ID: {customer_id}")
                return customer_id
        
        print("✗ Không thể lưu customer")
        return None
    
    def save_prediction_log(
        self,
        customer_id: Optional[int],
        model_name: str,
        predicted_label: int,
        probability: float,
        raw_input_dict: Dict,
        user_id: Optional[int] = None
    ) -> bool:
        """
        Lưu lịch sử dự báo vào database
        
        Args:
            customer_id: ID khách hàng (nullable)
            model_name: Tên mô hình ML
            predicted_label: Nhãn dự đoán (0/1)
            probability: Xác suất
            raw_input_dict: Dict chứa input đầy đủ
            user_id: ID user thực hiện dự báo (nullable)
        
        Returns:
            True nếu thành công, False nếu thất bại
        """
        # Chuyển dict thành JSON string
        raw_input_json = json.dumps(raw_input_dict)
        
        query = """
            INSERT INTO predictions_log (
                customer_id, model_name, predicted_label, probability, raw_input_json, user_id
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = (customer_id, model_name, predicted_label, probability, raw_input_json, user_id)
        success = self.db.execute_query(query, params)
        
        if success:
            print(f"✓ Đã lưu prediction log cho customer_id={customer_id}")
        else:
            print("✗ Không thể lưu prediction log")
        
        return success
    
    def get_recent_predictions(self, limit: int = 10) -> List[Dict]:
        """
        Lấy danh sách predictions log gần đây
        
        Args:
            limit: Số lượng records tối đa
        
        Returns:
            List các dict chứa thông tin predictions
        """
        query = """
            SELECT 
                id, customer_id, model_name, predicted_label, probability, created_at, raw_input_json
            FROM predictions_log
            ORDER BY created_at DESC
            LIMIT %s
        """
        
        results = self.db.fetch_all(query, (limit,))
        
        predictions = []
        for row in results:
            predictions.append({
                'id': row[0],
                'customer_id': row[1],
                'model_name': row[2],
                'predicted_label': row[3],
                'probability': float(row[4]),
                'created_at': row[5],
                'raw_input_json': row[6]
            })
        
        return predictions

    def save_model_threshold(self, model_name: str, threshold: float, updated_by: str) -> bool:
        try:
            q1 = "INSERT INTO model_thresholds (model_name, threshold, updated_by) VALUES (%s, %s, %s)"
            ok1 = self.db.execute_query(q1, (model_name, float(threshold), updated_by))
            q2 = "UPDATE model_registry SET threshold = %s WHERE model_name = %s"
            ok2 = self.db.execute_query(q2, (float(threshold), model_name))
            return bool(ok1 and ok2)
        except Exception:
            return False

    # ===================== Aggregates for User Dashboard =====================
    def get_risk_bucket_counts(self) -> Dict[str, int]:
        """Đếm số lượng predictions theo các bucket xác suất"""
        query = """
            SELECT 
                SUM(CASE WHEN probability >= 0 AND probability < 0.20 THEN 1 ELSE 0 END) AS b0_20,
                SUM(CASE WHEN probability >= 0.20 AND probability < 0.40 THEN 1 ELSE 0 END) AS b20_40,
                SUM(CASE WHEN probability >= 0.40 AND probability < 0.60 THEN 1 ELSE 0 END) AS b40_60,
                SUM(CASE WHEN probability >= 0.60 AND probability < 0.80 THEN 1 ELSE 0 END) AS b60_80,
                SUM(CASE WHEN probability >= 0.80 AND probability <= 1.00 THEN 1 ELSE 0 END) AS b80_100
            FROM predictions_log
        """
        row = self.db.fetch_one(query)
        if not row:
            return {'0_20': 0, '20_40': 0, '40_60': 0, '60_80': 0, '80_100': 0}
        return {
            '0_20': int(row[0] or 0),
            '20_40': int(row[1] or 0),
            '40_60': int(row[2] or 0),
            '60_80': int(row[3] or 0),
            '80_100': int(row[4] or 0),
        }

    def get_risk_bucket_counts_since(self, since_iso: str) -> Dict[str, int]:
        query = """
            SELECT 
                SUM(CASE WHEN probability >= 0 AND probability < 0.20 THEN 1 ELSE 0 END) AS b0_20,
                SUM(CASE WHEN probability >= 0.20 AND probability < 0.40 THEN 1 ELSE 0 END) AS b20_40,
                SUM(CASE WHEN probability >= 0.40 AND probability < 0.60 THEN 1 ELSE 0 END) AS b40_60,
                SUM(CASE WHEN probability >= 0.60 AND probability < 0.80 THEN 1 ELSE 0 END) AS b60_80,
                SUM(CASE WHEN probability >= 0.80 AND probability <= 1.00 THEN 1 ELSE 0 END) AS b80_100
            FROM predictions_log
            WHERE created_at >= %s
        """
        row = self.db.fetch_one(query, (since_iso,))
        if not row:
            return {'0_20': 0, '20_40': 0, '40_60': 0, '60_80': 0, '80_100': 0}
        return {
            '0_20': int(row[0] or 0),
            '20_40': int(row[1] or 0),
            '40_60': int(row[2] or 0),
            '60_80': int(row[3] or 0),
            '80_100': int(row[4] or 0),
        }

    def get_monthly_default_rate(self, months: int = 12) -> List[Dict]:
        """Tính % default (predicted_label=1) theo tháng gần nhất, bổ sung các tháng thiếu với 0"""
        # Lấy aggregate theo tháng hiện có
        query = """
            SELECT DATE_FORMAT(created_at,'%Y-%m') AS ym,
                   COUNT(*) AS total,
                   SUM(CASE WHEN predicted_label = 1 THEN 1 ELSE 0 END) AS defaults
            FROM predictions_log
            GROUP BY ym
            ORDER BY ym ASC
        """
        rows = self.db.fetch_all(query)
        agg = {r[0]: (int(r[1] or 0), int(r[2] or 0)) for r in rows}
        # Tạo danh sách tháng liên tục
        keys = []
        now = datetime.now()
        y = now.year; m = now.month
        for _ in range(months):
            keys.append(f"{y}-{m:02d}")
            m -= 1
            if m == 0:
                m = 12; y -= 1
        keys.reverse()
        result = []
        for k in keys:
            total, defaults = agg.get(k, (0, 0))
            rate = (defaults / total) if total > 0 else 0.0
            result.append({'period': k, 'rate': rate})
        return result

    def get_monthly_default_rate_recent(self, months: int = 12) -> List[Dict]:
        query = """
            SELECT DATE_FORMAT(created_at,'%Y-%m') AS ym,
                   COUNT(*) AS total,
                   SUM(CASE WHEN predicted_label = 1 THEN 1 ELSE 0 END) AS defaults
            FROM predictions_log
            GROUP BY ym
            ORDER BY ym ASC
        """
        rows = self.db.fetch_all(query)
        if not rows:
            return []
        start = max(0, len(rows) - months)
        result = []
        for ym, total, defaults in rows[start:]:
            t = int(total or 0)
            d = int(defaults or 0)
            rate = (d / t) if t > 0 else 0.0
            result.append({'period': ym, 'rate': rate})
        return result

    def get_quarterly_high_risk_rate(self, quarters: int = 8, threshold: float = 0.60) -> List[Dict]:
        """Tính % high-risk theo quý (probability >= threshold), bổ sung quý thiếu với 0"""
        thr = self._get_dashboard_threshold_override(threshold)
        query = """
            SELECT YEAR(created_at) AS y, QUARTER(created_at) AS q,
                   COUNT(*) AS total,
                   SUM(CASE WHEN probability >= %s THEN 1 ELSE 0 END) AS high
            FROM predictions_log
            GROUP BY y, q
            ORDER BY y ASC, q ASC
        """
        rows = self.db.fetch_all(query, (thr,))
        agg = {f"{int(r[0])}-Q{int(r[1])}": (int(r[2] or 0), int(r[3] or 0)) for r in rows}
        # Tạo danh sách quý liên tục
        keys = []
        now = datetime.now()
        y = now.year; q = (now.month - 1)//3 + 1
        for _ in range(quarters):
            keys.append(f"{y}-Q{q}")
            q -= 1
            if q == 0:
                q = 4; y -= 1
        keys.reverse()
        result = []
        for k in keys:
            total, high = agg.get(k, (0, 0))
            rate = (high / total) if total > 0 else 0.0
            result.append({'period': k, 'rate': rate})
        return result

    def get_quarterly_high_risk_rate_recent(self, quarters: int = 8, threshold: float = 0.60) -> List[Dict]:
        thr = self._get_dashboard_threshold_override(threshold)
        query = """
            SELECT YEAR(created_at) AS y, QUARTER(created_at) AS q,
                   COUNT(*) AS total,
                   SUM(CASE WHEN probability >= %s THEN 1 ELSE 0 END) AS high
            FROM predictions_log
            GROUP BY y, q
            ORDER BY y ASC, q ASC
        """
        rows = self.db.fetch_all(query, (thr,))
        if not rows:
            return []
        start = max(0, len(rows) - quarters)
        result = []
        for y, q, total, high in rows[start:]:
            t = int(total or 0)
            h = int(high or 0)
            rate = (h / t) if t > 0 else 0.0
            result.append({'period': f"{int(y)}-Q{int(q)}", 'rate': rate})
        return result

    def _get_dashboard_threshold_override(self, default_thr: float = 0.60) -> float:
        try:
            if not self._eval_path or not self._eval_path.exists():
                return float(default_thr)
            import numpy as np
            data = np.load(self._eval_path, allow_pickle=True)
            ov = data.get('dashboard_threshold', None)
            if ov is None:
                return float(default_thr)
            d = ov.item() if hasattr(ov, 'item') else ov
            return float(d.get('value', default_thr))
        except Exception:
            return float(default_thr)

    def get_weekly_default_rate(self, weeks: int = 8) -> List[Dict]:
        query = """
            SELECT YEAR(created_at) AS y, WEEK(created_at, 3) AS w,
                   COUNT(*) AS total,
                   SUM(CASE WHEN predicted_label = 1 THEN 1 ELSE 0 END) AS defaults
            FROM predictions_log
            GROUP BY y, w
            ORDER BY y ASC, w ASC
        """
        rows = self.db.fetch_all(query)
        agg = {f"{int(r[0])}-W{int(r[1]):02d}": (int(r[2] or 0), int(r[3] or 0)) for r in rows}
        # Build continuous series of last N weeks
        from datetime import datetime, timedelta
        now = datetime.now()
        keys = []
        cur = now
        for _ in range(weeks):
            y = cur.isocalendar().year
            w = cur.isocalendar().week
            keys.append(f"{y}-W{w:02d}")
            cur = cur - timedelta(days=7)
        keys.reverse()
        result = []
        for k in keys:
            total, defaults = agg.get(k, (0, 0))
            rate = (defaults / total) if total > 0 else 0.0
            result.append({'period': k, 'rate': rate})
        return result

    def get_demographics_counts(self) -> tuple:
        """Lấy thống kê số lượng khách hàng theo Gender, Marriage, Education"""
        # Gender
        rows = self.db.fetch_all("SELECT SEX, COUNT(*) FROM customers GROUP BY SEX")
        gender_map = {self._map_sex_label(r[0]): int(r[1]) for r in rows}
        # Marriage
        rows = self.db.fetch_all("SELECT MARRIAGE, COUNT(*) FROM customers GROUP BY MARRIAGE")
        marriage_map = {self._map_marriage_label(r[0]): int(r[1]) for r in rows}
        # Education
        rows = self.db.fetch_all("SELECT EDUCATION, COUNT(*) FROM customers GROUP BY EDUCATION")
        education_map = {self._map_education_label(r[0]): int(r[1]) for r in rows}
        return gender_map, marriage_map, education_map

    def get_demographics_counts_since(self, since_iso: str) -> tuple:
        """Thống kê theo thời gian: join predictions_log để chỉ tính các khách hàng có dự báo trong khoảng kể từ since"""
        try:
            # Gender by predictions within range
            rows = self.db.fetch_all(
                """
                SELECT c.SEX, COUNT(*)
                FROM customers c
                JOIN predictions_log p ON p.customer_id = c.id
                WHERE p.created_at >= %s
                GROUP BY c.SEX
                """,
                (since_iso,)
            )
            gender_map = {self._map_sex_label(r[0]): int(r[1]) for r in rows}
        except Exception:
            rows = self.db.fetch_all("SELECT SEX, COUNT(*) FROM customers GROUP BY SEX")
            gender_map = {self._map_sex_label(r[0]): int(r[1]) for r in rows}

        try:
            rows = self.db.fetch_all(
                """
                SELECT c.MARRIAGE, COUNT(*)
                FROM customers c
                JOIN predictions_log p ON p.customer_id = c.id
                WHERE p.created_at >= %s
                GROUP BY c.MARRIAGE
                """,
                (since_iso,)
            )
            marriage_map = {self._map_marriage_label(r[0]): int(r[1]) for r in rows}
        except Exception:
            rows = self.db.fetch_all("SELECT MARRIAGE, COUNT(*) FROM customers GROUP BY MARRIAGE")
            marriage_map = {self._map_marriage_label(r[0]): int(r[1]) for r in rows}

        try:
            rows = self.db.fetch_all(
                """
                SELECT c.EDUCATION, COUNT(*)
                FROM customers c
                JOIN predictions_log p ON p.customer_id = c.id
                WHERE p.created_at >= %s
                GROUP BY c.EDUCATION
                """,
                (since_iso,)
            )
            education_map = {self._map_education_label(r[0]): int(r[1]) for r in rows}
        except Exception:
            rows = self.db.fetch_all("SELECT EDUCATION, COUNT(*) FROM customers GROUP BY EDUCATION")
            education_map = {self._map_education_label(r[0]): int(r[1]) for r in rows}

        return gender_map, marriage_map, education_map

    def get_shap_lite_importance_since(self, since_iso: str) -> Dict[str, float]:
        """Tính điểm ảnh hưởng đơn giản theo thời gian (proxy):
        - LIMIT_BAL: chênh lệch tỷ lệ high-risk giữa nhóm trên/ dưới trung bình
        - AGE: chênh lệch tỷ lệ high-risk giữa nhóm >=30 và <30
        - MARRIAGE: chênh lệch tối đa so với overall
        - PAY_0, PAY_2: nếu có trong bảng customers hoặc bảng payment, cố gắng tính; nếu không có, trả 0.
        """
        def overall_high_rate():
            row = self.db.fetch_one(
                """
                SELECT AVG(CASE WHEN probability >= 0.60 THEN 1 ELSE 0 END)
                FROM predictions_log
                WHERE created_at >= %s
                """,
                (since_iso,)
            )
            return float(row[0] or 0.0)

        overall = overall_high_rate()
        scores: Dict[str, float] = {}

        # LIMIT_BAL split by average
        try:
            row = self.db.fetch_one("SELECT AVG(LIMIT_BAL) FROM customers")
            avg_limit = float(row[0] or 0.0)
            def_rate_hi = self.db.fetch_one(
                """
                SELECT AVG(CASE WHEN p.probability >= 0.60 THEN 1 ELSE 0 END)
                FROM predictions_log p JOIN customers c ON p.customer_id = c.id
                WHERE p.created_at >= %s AND c.LIMIT_BAL >= %s
                """,
                (since_iso, avg_limit)
            )[0]
            def_rate_lo = self.db.fetch_one(
                """
                SELECT AVG(CASE WHEN p.probability >= 0.60 THEN 1 ELSE 0 END)
                FROM predictions_log p JOIN customers c ON p.customer_id = c.id
                WHERE p.created_at >= %s AND c.LIMIT_BAL < %s
                """,
                (since_iso, avg_limit)
            )[0]
            scores['LIMIT_BAL'] = abs(float(def_rate_hi or 0.0) - float(def_rate_lo or 0.0))
        except Exception:
            scores['LIMIT_BAL'] = 0.0

        # AGE split by 30
        try:
            def_rate_older = self.db.fetch_one(
                """
                SELECT AVG(CASE WHEN p.probability >= 0.60 THEN 1 ELSE 0 END)
                FROM predictions_log p JOIN customers c ON p.customer_id = c.id
                WHERE p.created_at >= %s AND c.AGE >= 30
                """,
                (since_iso,)
            )[0]
            def_rate_younger = self.db.fetch_one(
                """
                SELECT AVG(CASE WHEN p.probability >= 0.60 THEN 1 ELSE 0 END)
                FROM predictions_log p JOIN customers c ON p.customer_id = c.id
                WHERE p.created_at >= %s AND c.AGE < 30
                """,
                (since_iso,)
            )[0]
            scores['Tuổi'] = abs(float(def_rate_older or 0.0) - float(def_rate_younger or 0.0))
        except Exception:
            scores['Tuổi'] = 0.0

        # MARRIAGE categories vs overall
        try:
            rows = self.db.fetch_all(
                """
                SELECT c.MARRIAGE,
                       AVG(CASE WHEN p.probability >= 0.60 THEN 1 ELSE 0 END) AS rate
                FROM predictions_log p JOIN customers c ON p.customer_id = c.id
                WHERE p.created_at >= %s
                GROUP BY c.MARRIAGE
                """,
                (since_iso,)
            )
            diffs = [abs(float(r[1] or 0.0) - overall) for r in rows]
            scores['Tình trạng hôn nhân'] = max(diffs) if diffs else 0.0
        except Exception:
            scores['Tình trạng hôn nhân'] = 0.0

        # PAY_0, PAY_2 (if available on customers)
        for col, label in [('PAY_0', 'PAY_0'), ('PAY_2', 'PAY_2')]:
            try:
                rows = self.db.fetch_all(
                    f"""
                    SELECT c.{col}, AVG(CASE WHEN p.probability >= 0.60 THEN 1 ELSE 0 END) AS rate
                    FROM predictions_log p JOIN customers c ON p.customer_id = c.id
                    WHERE p.created_at >= %s
                    GROUP BY c.{col}
                    """,
                    (since_iso,)
                )
                diffs = [abs(float(r[1] or 0.0) - overall) for r in rows]
                scores[label] = max(diffs) if diffs else 0.0
            except Exception:
                scores[label] = 0.0

        return scores

    def get_prediction_stats(self) -> Dict:
        query = """
            SELECT 
                COUNT(*) AS total_predictions,
                SUM(CASE WHEN probability >= 0.60 THEN 1 ELSE 0 END) AS high_risk_count,
                AVG(probability) AS avg_probability
            FROM predictions_log
        """
        row = self.db.fetch_one(query)
        if not row:
            return {'total_predictions': 0, 'high_risk_count': 0, 'avg_probability': 0.0}
        return {
            'total_predictions': int(row[0] or 0),
            'high_risk_count': int(row[1] or 0),
            'avg_probability': float(row[2] or 0.0)
        }

    def _build_time_where(self, time_range: str) -> str:
        tr = (time_range or '').strip().lower()
        if 'hôm nay' in tr or 'hom nay' in tr or 'today' in tr:
            return "DATE(p.created_at) = CURDATE()"
        if 'tuần' in tr or 'tuan' in tr or 'week' in tr:
            return "YEARWEEK(p.created_at) = YEARWEEK(CURDATE())"
        if 'quý' in tr or 'quy' in tr or 'quarter' in tr:
            return "YEAR(p.created_at) = YEAR(CURDATE()) AND QUARTER(p.created_at) = QUARTER(CURDATE())"
        if 'năm' in tr or 'nam' in tr or 'year' in tr:
            return "YEAR(p.created_at) = YEAR(CURDATE())"
        if 'tất cả' in tr or 'tat ca' in tr or 'all' in tr:
            return "1 = 1"
        return "DATE_FORMAT(p.created_at,'%Y-%m') = DATE_FORMAT(CURDATE(),'%Y-%m')"

    def get_prediction_stats_filtered(self, time_range: str, status_filter: str, user_id: Optional[int] = None) -> Dict:
        where_parts = [self._build_time_where(time_range)]
        sf = (status_filter or '').strip().lower()
        if 'nguy cơ cao' in sf or 'cao' in sf or 'high' in sf:
            where_parts.append("p.predicted_label = 1")
        elif 'nguy cơ thấp' in sf or 'thấp' in sf or 'low' in sf:
            where_parts.append("p.predicted_label = 0")
        if user_id is not None:
            where_parts.append("p.user_id = %s")
        where_sql = ' AND '.join(where_parts)
        query = f"""
            SELECT 
                COUNT(*) AS total_predictions,
                SUM(CASE WHEN p.predicted_label = 1 THEN 1 ELSE 0 END) AS high_risk_count,
                AVG(p.probability) AS avg_probability
            FROM predictions_log p
            WHERE {where_sql}
        """
        params = (user_id,) if user_id is not None else tuple()
        row = self.db.fetch_one(query, params if params else None)
        if not row:
            return {'total_predictions': 0, 'high_risk_count': 0, 'avg_probability': 0.0}
        return {
            'total_predictions': int(row[0] or 0),
            'high_risk_count': int(row[1] or 0),
            'avg_probability': float(row[2] or 0.0)
        }

    def get_prediction_stats_range(self, start_date: Optional[str], end_date: Optional[str], status_filter: str, user_id: Optional[int] = None) -> Dict:
        where_parts = []
        if start_date and end_date:
            where_parts.append("DATE(p.created_at) BETWEEN %s AND %s")
        sf = (status_filter or '').strip().lower()
        if 'nguy cơ cao' in sf or 'cao' in sf or 'high' in sf:
            where_parts.append("p.predicted_label = 1")
        elif 'nguy cơ thấp' in sf or 'thấp' in sf or 'low' in sf:
            where_parts.append("p.predicted_label = 0")
        if user_id is not None:
            where_parts.append("p.user_id = %s")
        where_sql = ' AND '.join(where_parts) if where_parts else '1=1'
        query = f"""
            SELECT 
                COUNT(*) AS total_predictions,
                SUM(CASE WHEN p.predicted_label = 1 THEN 1 ELSE 0 END) AS high_risk_count,
                AVG(p.probability) AS avg_probability
            FROM predictions_log p
            WHERE {where_sql}
        """
        params: list = []
        if start_date and end_date:
            params += [start_date, end_date]
        if user_id is not None:
            params += [user_id]
        row = self.db.fetch_one(query, tuple(params) if params else None)
        if not row:
            return {'total_predictions': 0, 'high_risk_count': 0, 'avg_probability': 0.0}
        return {
            'total_predictions': int(row[0] or 0),
            'high_risk_count': int(row[1] or 0),
            'avg_probability': float(row[2] or 0.0)
        }

    def get_predictions_join_customers_range(self, start_date: Optional[str], end_date: Optional[str], status_filter: str, limit: int = 200, user_id: Optional[int] = None) -> List[Dict]:
        where_parts = []
        if start_date and end_date:
            where_parts.append("DATE(p.created_at) BETWEEN %s AND %s")
        sf = (status_filter or '').strip().lower()
        if 'nguy cơ cao' in sf or 'cao' in sf or 'high' in sf:
            where_parts.append("p.predicted_label = 1")
        elif 'nguy cơ thấp' in sf or 'thấp' in sf or 'low' in sf:
            where_parts.append("p.predicted_label = 0")
        if user_id is not None:
            where_parts.append("p.user_id = %s")
        where_sql = ' AND '.join(where_parts) if where_parts else '1=1'
        query = f"""
            SELECT p.customer_id, p.probability, p.predicted_label, p.created_at, p.raw_input_json, p.user_id,
                   c.customer_name, c.customer_id_card, c.LIMIT_BAL, c.AGE, c.PAY_0, c.BILL_AMT1
            FROM predictions_log p
            LEFT JOIN customers c ON p.customer_id = c.id
            WHERE {where_sql}
            ORDER BY p.created_at DESC
            LIMIT %s
        """
        params: list = []
        if start_date and end_date:
            params += [start_date, end_date]
        if user_id is not None:
            params += [user_id]
        params += [limit]
        rows = self.db.fetch_all(query, tuple(params))
        results: List[Dict] = []
        for r in rows:
            results.append({
                'customer_id': int(r[0] or 0),
                'probability': float(r[1] or 0.0),
                'label': int(r[2] or 0),
                'created_at': r[3],
                'raw_input_json': r[4],
                'user_id': int(r[5] or 0) if r[5] is not None else None,
                'customer_name': r[6],
                'customer_id_card': r[7],
                'LIMIT_BAL': float(r[8] or 0.0),
                'AGE': int(r[9] or 0) if r[9] is not None else None,
                'PAY_0': int(r[10] or 0) if r[10] is not None else None,
                'BILL_AMT1': float(r[11] or 0.0),
            })
        return results

    def get_predictions_join_customers(self, time_range: str, status_filter: str, limit: int = 200, user_id: Optional[int] = None) -> List[Dict]:
        where_parts = [self._build_time_where(time_range)]
        sf = (status_filter or '').strip().lower()
        if 'nguy cơ cao' in sf or 'cao' in sf or 'high' in sf:
            where_parts.append("p.predicted_label = 1")
        elif 'nguy cơ thấp' in sf or 'thấp' in sf or 'low' in sf:
            where_parts.append("p.predicted_label = 0")
        if user_id is not None:
            where_parts.append("p.user_id = %s")
        where_sql = ' AND '.join(where_parts)
        query = f"""
            SELECT p.customer_id, p.probability, p.predicted_label, p.created_at, p.raw_input_json, p.user_id,
                   c.customer_name, c.customer_id_card, c.LIMIT_BAL, c.AGE, c.PAY_0, c.BILL_AMT1
            FROM predictions_log p
            LEFT JOIN customers c ON p.customer_id = c.id
            WHERE {where_sql}
            ORDER BY p.created_at DESC
            LIMIT %s
        """
        params: tuple = (user_id, limit) if user_id is not None else (limit,)
        rows = self.db.fetch_all(query, params)
        results: List[Dict] = []
        for r in rows:
            results.append({
                'customer_id': int(r[0] or 0),
                'probability': float(r[1] or 0.0),
                'label': int(r[2] or 0),
                'created_at': r[3],
                'raw_input_json': r[4],
                'user_id': int(r[5] or 0) if r[5] is not None else None,
                'customer_name': r[6],
                'customer_id_card': r[7],
                'LIMIT_BAL': float(r[8] or 0.0),
                'AGE': int(r[9] or 0) if r[9] is not None else None,
                'PAY_0': int(r[10] or 0) if r[10] is not None else None,
                'BILL_AMT1': float(r[11] or 0.0),
            })
        return results

    def get_top_predictions_join_customers_filtered(self, ascending: bool, time_range: str, limit: int = 10, user_id: Optional[int] = None) -> List[Dict]:
        order = "ASC" if ascending else "DESC"
        where_parts = [self._build_time_where(time_range)]
        if user_id is not None:
            where_parts.append("p.user_id = %s")
        where_sql = ' AND '.join(where_parts)
        query = f"""
            SELECT p.customer_id, p.probability, p.predicted_label,
                   c.customer_name, c.customer_id_card
            FROM predictions_log p
            INNER JOIN customers c ON p.customer_id = c.id
            WHERE {where_sql}
            ORDER BY p.probability {order}
            LIMIT %s
        """
        params: tuple = (user_id, limit) if user_id is not None else (limit,)
        rows = self.db.fetch_all(query, params)
        results: List[Dict] = []
        for r in rows:
            results.append({
                'customer_id': int(r[0] or 0),
                'probability': float(r[1] or 0.0),
                'label': int(r[2] or 0),
                'customer_name': r[3],
                'customer_id_card': r[4],
            })
        return results

    def get_demographics_counts_filtered(self, time_range: str, user_id: Optional[int] = None) -> tuple:
        where_parts = [self._build_time_where(time_range)]
        if user_id is not None:
            where_parts.append("p.user_id = %s")
        where_sql = ' AND '.join(where_parts)
        # Gender
        rows = self.db.fetch_all(
            f"""
            SELECT c.SEX, COUNT(*)
            FROM customers c JOIN predictions_log p ON p.customer_id = c.id
            WHERE {where_sql}
            GROUP BY c.SEX
            """,
            (user_id,) if user_id is not None else None
        )
        gender_map = {self._map_sex_label(r[0]): int(r[1]) for r in rows}
        # Marriage
        rows = self.db.fetch_all(
            f"""
            SELECT c.MARRIAGE, COUNT(*)
            FROM customers c JOIN predictions_log p ON p.customer_id = c.id
            WHERE {where_sql}
            GROUP BY c.MARRIAGE
            """,
            (user_id,) if user_id is not None else None
        )
        marriage_map = {self._map_marriage_label(r[0]): int(r[1]) for r in rows}
        # Education
        rows = self.db.fetch_all(
            f"""
            SELECT c.EDUCATION, COUNT(*)
            FROM customers c JOIN predictions_log p ON p.customer_id = c.id
            WHERE {where_sql}
            GROUP BY c.EDUCATION
            """,
            (user_id,) if user_id is not None else None
        )
        education_map = {self._map_education_label(r[0]): int(r[1]) for r in rows}
        return gender_map, marriage_map, education_map

    def get_latest_day_bucket_counts(self) -> Dict[str, int]:
        row = self.db.fetch_one("SELECT DATE(created_at) FROM predictions_log ORDER BY created_at DESC LIMIT 1")
        if not row or not row[0]:
            return {'0_20': 0, '20_40': 0, '40_60': 0, '60_80': 0, '80_100': 0}
        d = row[0]
        query = """
            SELECT 
                SUM(CASE WHEN probability >= 0 AND probability < 0.20 THEN 1 ELSE 0 END) AS b0_20,
                SUM(CASE WHEN probability >= 0.20 AND probability < 0.40 THEN 1 ELSE 0 END) AS b20_40,
                SUM(CASE WHEN probability >= 0.40 AND probability < 0.60 THEN 1 ELSE 0 END) AS b40_60,
                SUM(CASE WHEN probability >= 0.60 AND probability < 0.80 THEN 1 ELSE 0 END) AS b60_80,
                SUM(CASE WHEN probability >= 0.80 AND probability <= 1.00 THEN 1 ELSE 0 END) AS b80_100
            FROM predictions_log
            WHERE DATE(created_at) = %s
        """
        r = self.db.fetch_one(query, (d,))
        if not r:
            return {'0_20': 0, '20_40': 0, '40_60': 0, '60_80': 0, '80_100': 0}
        return {
            '0_20': int(r[0] or 0),
            '20_40': int(r[1] or 0),
            '40_60': int(r[2] or 0),
            '60_80': int(r[3] or 0),
            '80_100': int(r[4] or 0),
        }

    def get_latest_day_predictions_join_customers(self, limit: int = 2000) -> List[Dict]:
        row = self.db.fetch_one("SELECT DATE(created_at) FROM predictions_log ORDER BY created_at DESC LIMIT 1")
        if not row or not row[0]:
            return []
        d = row[0]
        query = """
            SELECT p.customer_id, p.probability, p.predicted_label,
                   c.customer_name, c.customer_id_card,
                   c.LIMIT_BAL, c.AGE, c.EDUCATION, c.MARRIAGE, c.SEX,
                   c.PAY_0, c.BILL_AMT1
            FROM predictions_log p
            LEFT JOIN customers c ON p.customer_id = c.id
            WHERE DATE(p.created_at) = %s
            ORDER BY p.probability DESC
            LIMIT %s
        """
        rows = self.db.fetch_all(query, (d, limit))
        results: List[Dict] = []
        for r in rows:
            results.append({
                'customer_id': int(r[0] or 0),
                'probability': float(r[1] or 0.0),
                'label': int(r[2] or 0),
                'customer_name': r[3],
                'customer_id_card': r[4],
                'LIMIT_BAL': float(r[5] or 0.0),
                'AGE': int(r[6] or 0) if r[6] is not None else None,
                'EDUCATION': int(r[7] or 0) if r[7] is not None else None,
                'MARRIAGE': int(r[8] or 0) if r[8] is not None else None,
                'SEX': int(r[9] or 0) if r[9] is not None else None,
                'PAY_0': int(r[10] or 0) if r[10] is not None else None,
                'BILL_AMT1': float(r[11] or 0.0),
            })
        return results

    def get_top_predictions_join_customers(self, limit: int = 10, ascending: bool = False) -> List[Dict]:
        order = "ASC" if ascending else "DESC"
        query = f"""
            SELECT p.customer_id, p.probability, p.predicted_label,
                   c.customer_name, c.customer_id_card
            FROM predictions_log p
            INNER JOIN customers c ON p.customer_id = c.id
            ORDER BY p.probability {order}
            LIMIT %s
        """
        rows = self.db.fetch_all(query, (limit,))
        results: List[Dict] = []
        for r in rows:
            results.append({
                'customer_id': int(r[0] or 0),
                'probability': float(r[1] or 0.0),
                'label': int(r[2] or 0),
                'customer_name': r[3],
                'customer_id_card': r[4],
            })
        return results

    def get_recent_predictions_join_customers(self, period: str = 'today', limit: int = 100) -> List[Dict]:
        period = (period or 'today').strip().lower()
        if period in ('today', 'hôm nay', 'hom nay'):
            where = "WHERE DATE(p.created_at) = CURDATE()"
        elif period in ('week', 'tuần này', 'tuan nay'):
            where = "WHERE p.created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
        else:
            # month
            where = "WHERE DATE_FORMAT(p.created_at,'%Y-%m') = DATE_FORMAT(CURDATE(),'%Y-%m')"
        query = f"""
            SELECT p.customer_id, p.predicted_label, p.probability, p.created_at, p.raw_input_json, p.user_id,
                   c.customer_name, c.customer_id_card
            FROM predictions_log p
            LEFT JOIN customers c ON p.customer_id = c.id
            {where}
            ORDER BY p.created_at DESC
            LIMIT %s
        """
        rows = self.db.fetch_all(query, (limit,))
        if not rows and period in ('today','hôm nay','hom nay'):
            drow = self.db.fetch_one("SELECT DATE(created_at) FROM predictions_log ORDER BY created_at DESC LIMIT 1")
            if drow and drow[0]:
                query2 = """
                    SELECT p.customer_id, p.predicted_label, p.probability, p.created_at, p.raw_input_json, p.user_id,
                           c.customer_name, c.customer_id_card
                    FROM predictions_log p
                    LEFT JOIN customers c ON p.customer_id = c.id
                    WHERE DATE(p.created_at) = %s
                    ORDER BY p.probability DESC
                    LIMIT %s
                """
                rows = self.db.fetch_all(query2, (drow[0], limit))
        results: List[Dict] = []
        for r in rows:
            results.append({
                'customer_id': int(r[0] or 0),
                'predicted_label': int(r[1] or 0),
                'probability': float(r[2] or 0.0),
                'created_at': r[3],
                'raw_input_json': r[4],
                'user_id': r[5],
                'customer_name': r[6],
                'customer_id_card': r[7],
            })
        return results

    def get_payment_status_distribution(self) -> Dict[str, int]:
        query = """
            SELECT
                SUM(CASE WHEN PAY_0 <= 0 THEN 1 ELSE 0 END) AS on_time,
                SUM(CASE WHEN PAY_0 = 1 THEN 1 ELSE 0 END) AS late_1,
                SUM(CASE WHEN PAY_0 = 2 THEN 1 ELSE 0 END) AS late_2,
                SUM(CASE WHEN PAY_0 >= 3 THEN 1 ELSE 0 END) AS late_3p
            FROM customers
        """
        r = self.db.fetch_one(query)
        if not r:
            return {'On time': 0, '1 mo late': 0, '2 mo late': 0, '3+ mo late': 0}
        return {
            'On time': int(r[0] or 0),
            '1 mo late': int(r[1] or 0),
            '2 mo late': int(r[2] or 0),
            '3+ mo late': int(r[3] or 0),
        }

    def get_top_late_customers_with_risk(self, limit: int = 20) -> List[Dict]:
        row = self.db.fetch_one("SELECT DATE(created_at) FROM predictions_log ORDER BY created_at DESC LIMIT 1")
        d = row[0] if row and row[0] else None
        if d:
            query = """
                SELECT c.customer_name, c.customer_id_card,
                       CASE WHEN p.probability >= 0.60 THEN 'High'
                            WHEN p.probability >= 0.40 THEN 'Medium'
                            ELSE 'Low' END AS risk,
                       c.PAY_0,
                       GREATEST(c.BILL_AMT1 - c.PAY_AMT1, 0) AS overdue
                FROM customers c
                LEFT JOIN predictions_log p ON p.customer_id = c.id AND DATE(p.created_at) = %s
                WHERE c.PAY_0 >= 1
                ORDER BY c.PAY_0 DESC, overdue DESC
                LIMIT %s
            """
            rows = self.db.fetch_all(query, (d, limit))
        else:
            query = """
                SELECT c.customer_name, c.customer_id_card,
                       'Low' AS risk,
                       c.PAY_0,
                       GREATEST(c.BILL_AMT1 - c.PAY_AMT1, 0) AS overdue
                FROM customers c
                WHERE c.PAY_0 >= 1
                ORDER BY c.PAY_0 DESC, overdue DESC
                LIMIT %s
            """
            rows = self.db.fetch_all(query, (limit,))
        result: List[Dict] = []
        for r in rows:
            result.append({
                'customer_name': r[0],
                'customer_id_card': r[1],
                'risk': r[2],
                'months_late': int(r[3] or 0),
                'amount_overdue': float(r[4] or 0.0),
            })
        return result

    # ===================== Label mapping helpers =====================
    @staticmethod
    def _map_sex_label(code: int) -> str:
        return {1: 'Nam', 2: 'Nữ'}.get(code, str(code))

    @staticmethod
    def _map_marriage_label(code: int) -> str:
        return {1: 'Kết hôn', 2: 'Độc thân', 3: 'Khác'}.get(code, str(code))

    @staticmethod
    def _map_education_label(code: int) -> str:
        return {1: 'Cao học', 2: 'Đại học', 3: 'Trung học', 4: 'Khác'}.get(code, str(code))

    def get_customers_by_probability_range(self, min_prob: float, max_prob: Optional[float] = None, limit: int = 50) -> List[Dict]:
        query = """
            SELECT 
                p.id as prediction_id,
                p.customer_id,
                p.probability,
                c.customer_id_card,
                c.customer_name
            FROM predictions_log p
            LEFT JOIN customers c ON p.customer_id = c.id
            WHERE p.probability >= %s {upper}
            ORDER BY p.created_at DESC
            LIMIT %s
        """
        upper_clause = "AND p.probability < %s" if max_prob is not None else ""
        query = query.format(upper=upper_clause)
        params = (min_prob, max_prob, limit) if max_prob is not None else (min_prob, limit)
        rows = self.db.fetch_all(query, params)
        results = []
        for r in rows:
            results.append({
                'prediction_id': r[0],
                'customer_id': r[1],
                'probability': float(r[2]),
                'customer_id_card': r[3],
                'customer_name': r[4],
            })
        return results

    def get_customers_by_tier(self, tier: str, limit: int = 50) -> List[Dict]:
        tier = tier.strip().lower()
        if tier in ('trung bình', 'trung binh', 'medium'):
            return self.get_customers_by_probability_range(0.4, 0.6, limit)
        if tier in ('cao', 'high'):
            return self.get_customers_by_probability_range(0.6, 0.8, limit)
        if tier in ('rất cao', 'rat cao', 'very high'):
            return self.get_customers_by_probability_range(0.8, None, limit)
        if tier in ('rất thấp', 'rat thap', 'very low'):
            return self.get_customers_by_probability_range(0.0, 0.2, limit)
        if tier in ('thấp', 'thap', 'low'):
            return self.get_customers_by_probability_range(0.2, 0.4, limit)
        return []
    
    def search_customers(self, keyword: str, limit: int = 50) -> List[Dict]:
        like = f"%{keyword}%"
        query = """
            SELECT id, customer_name, customer_id_card, SEX, EDUCATION, MARRIAGE, AGE
            FROM customers
            WHERE customer_name LIKE %s OR customer_id_card LIKE %s
            ORDER BY id DESC
            LIMIT %s
        """
        rows = self.db.fetch_all(query, (like, like, limit))
        results = []
        for r in rows:
            results.append({
                'id': r[0],
                'customer_name': r[1],
                'customer_id_card': r[2],
                'SEX': r[3],
                'EDUCATION': r[4],
                'MARRIAGE': r[5],
                'AGE': r[6],
            })
        return results

    def list_customers(self, limit: int = 100) -> List[Dict]:
        query = """
            SELECT id, customer_name, customer_id_card, SEX, EDUCATION, MARRIAGE, AGE
            FROM customers
            ORDER BY id DESC
            LIMIT %s
        """
        rows = self.db.fetch_all(query, (limit,))
        return [
            {
                'id': r[0],
                'customer_name': r[1],
                'customer_id_card': r[2],
                'SEX': r[3],
                'EDUCATION': r[4],
                'MARRIAGE': r[5],
                'AGE': r[6],
            } for r in rows
        ]
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        """
        Lấy thông tin khách hàng theo ID (41 fields)
        
        Args:
            customer_id: ID khách hàng
        
        Returns:
            Instance Customer hoặc None nếu không tìm thấy
        """
        query = """
            SELECT 
                customer_name, customer_id_card,
                LIMIT_BAL, SEX, EDUCATION, MARRIAGE, AGE,
                PAY_0, PAY_2, PAY_3, PAY_4, PAY_5, PAY_6, PAY_7, PAY_8, PAY_9, PAY_10, PAY_11, PAY_12,
                BILL_AMT1, BILL_AMT2, BILL_AMT3, BILL_AMT4, BILL_AMT5, BILL_AMT6,
                BILL_AMT7, BILL_AMT8, BILL_AMT9, BILL_AMT10, BILL_AMT11, BILL_AMT12,
                PAY_AMT1, PAY_AMT2, PAY_AMT3, PAY_AMT4, PAY_AMT5, PAY_AMT6,
                PAY_AMT7, PAY_AMT8, PAY_AMT9, PAY_AMT10, PAY_AMT11, PAY_AMT12
            FROM customers
            WHERE id = %s
        """
        
        result = self.db.fetch_one(query, (customer_id,))
        
        if not result:
            return None
        
        customer = Customer(
            customer_name=result[0],
            customer_id_card=result[1],
            LIMIT_BAL=float(result[2]),
            SEX=result[3],
            EDUCATION=result[4],
            MARRIAGE=result[5],
            AGE=result[6],
            PAY_0=result[7],
            PAY_2=result[8],
            PAY_3=result[9],
            PAY_4=result[10],
            PAY_5=result[11],
            PAY_6=result[12],
            PAY_7=result[13],
            PAY_8=result[14],
            PAY_9=result[15],
            PAY_10=result[16],
            PAY_11=result[17],
            PAY_12=result[18],
            BILL_AMT1=float(result[19]),
            BILL_AMT2=float(result[20]),
            BILL_AMT3=float(result[21]),
            BILL_AMT4=float(result[22]),
            BILL_AMT5=float(result[23]),
            BILL_AMT6=float(result[24]),
            BILL_AMT7=float(result[25]),
            BILL_AMT8=float(result[26]),
            BILL_AMT9=float(result[27]),
            BILL_AMT10=float(result[28]),
            BILL_AMT11=float(result[29]),
            BILL_AMT12=float(result[30]),
            PAY_AMT1=float(result[31]),
            PAY_AMT2=float(result[32]),
            PAY_AMT3=float(result[33]),
            PAY_AMT4=float(result[34]),
            PAY_AMT5=float(result[35]),
            PAY_AMT6=float(result[36]),
            PAY_AMT7=float(result[37]),
            PAY_AMT8=float(result[38]),
            PAY_AMT9=float(result[39]),
            PAY_AMT10=float(result[40]),
            PAY_AMT11=float(result[41]),
            PAY_AMT12=float(result[42])
        )
        
        return customer
    
    def get_customer_by_cmnd(self, cmnd: str) -> Optional[Customer]:
        """
        Lấy thông tin khách hàng theo số CMND (41 fields)
        
        Args:
            cmnd: Số CMND khách hàng
        
        Returns:
            Instance Customer hoặc None nếu không tìm thấy
        """
        query = """
            SELECT 
                customer_name, customer_id_card,
                LIMIT_BAL, SEX, EDUCATION, MARRIAGE, AGE,
                PAY_0, PAY_2, PAY_3, PAY_4, PAY_5, PAY_6, PAY_7, PAY_8, PAY_9, PAY_10, PAY_11, PAY_12,
                BILL_AMT1, BILL_AMT2, BILL_AMT3, BILL_AMT4, BILL_AMT5, BILL_AMT6,
                BILL_AMT7, BILL_AMT8, BILL_AMT9, BILL_AMT10, BILL_AMT11, BILL_AMT12,
                PAY_AMT1, PAY_AMT2, PAY_AMT3, PAY_AMT4, PAY_AMT5, PAY_AMT6,
                PAY_AMT7, PAY_AMT8, PAY_AMT9, PAY_AMT10, PAY_AMT11, PAY_AMT12
            FROM customers
            WHERE customer_id_card = %s
        """
        
        result = self.db.fetch_one(query, (cmnd,))
        
        if not result:
            return None
        
        customer = Customer(
            customer_name=result[0],
            customer_id_card=result[1],
            LIMIT_BAL=float(result[2]),
            SEX=result[3],
            EDUCATION=result[4],
            MARRIAGE=result[5],
            AGE=result[6],
            PAY_0=result[7],
            PAY_2=result[8],
            PAY_3=result[9],
            PAY_4=result[10],
            PAY_5=result[11],
            PAY_6=result[12],
            PAY_7=result[13],
            PAY_8=result[14],
            PAY_9=result[15],
            PAY_10=result[16],
            PAY_11=result[17],
            PAY_12=result[18],
            BILL_AMT1=float(result[19]),
            BILL_AMT2=float(result[20]),
            BILL_AMT3=float(result[21]),
            BILL_AMT4=float(result[22]),
            BILL_AMT5=float(result[23]),
            BILL_AMT6=float(result[24]),
            BILL_AMT7=float(result[25]),
            BILL_AMT8=float(result[26]),
            BILL_AMT9=float(result[27]),
            BILL_AMT10=float(result[28]),
            BILL_AMT11=float(result[29]),
            BILL_AMT12=float(result[30]),
            PAY_AMT1=float(result[31]),
            PAY_AMT2=float(result[32]),
            PAY_AMT3=float(result[33]),
            PAY_AMT4=float(result[34]),
            PAY_AMT5=float(result[35]),
            PAY_AMT6=float(result[36]),
            PAY_AMT7=float(result[37]),
            PAY_AMT8=float(result[38]),
            PAY_AMT9=float(result[39]),
            PAY_AMT10=float(result[40]),
            PAY_AMT11=float(result[41]),
            PAY_AMT12=float(result[42])
        )
        
        return customer

    def update_customer(self, cmnd: str, customer: Customer) -> bool:
        """
        Cáº­p nháº­t thÃ´ng tin khÃ¡ch hÃ ng theo CMND
        
        Args:
            cmnd: Sá»‘ CMND cáº§n update
            customer: Instance Customer vá»›i dá»¯ liá»‡u má»›i
        
        Returns:
            True náº¿u thÃ nh cÃ´ng, False náº¿u tháº¥t báº¡i
        """
        query = """
            UPDATE customers SET
                customer_name = %s,
                LIMIT_BAL = %s, SEX = %s, EDUCATION = %s, MARRIAGE = %s, AGE = %s,
                PAY_0 = %s, PAY_2 = %s, PAY_3 = %s, PAY_4 = %s, PAY_5 = %s, PAY_6 = %s,
                PAY_7 = %s, PAY_8 = %s, PAY_9 = %s, PAY_10 = %s, PAY_11 = %s, PAY_12 = %s,
                BILL_AMT1 = %s, BILL_AMT2 = %s, BILL_AMT3 = %s, BILL_AMT4 = %s, BILL_AMT5 = %s, BILL_AMT6 = %s,
                BILL_AMT7 = %s, BILL_AMT8 = %s, BILL_AMT9 = %s, BILL_AMT10 = %s, BILL_AMT11 = %s, BILL_AMT12 = %s,
                PAY_AMT1 = %s, PAY_AMT2 = %s, PAY_AMT3 = %s, PAY_AMT4 = %s, PAY_AMT5 = %s, PAY_AMT6 = %s,
                PAY_AMT7 = %s, PAY_AMT8 = %s, PAY_AMT9 = %s, PAY_AMT10 = %s, PAY_AMT11 = %s, PAY_AMT12 = %s
            WHERE customer_id_card = %s
        """
        
        params = (
            customer.customer_name,
            customer.LIMIT_BAL, customer.SEX, customer.EDUCATION, customer.MARRIAGE, customer.AGE,
            customer.PAY_0, customer.PAY_2, customer.PAY_3, customer.PAY_4, customer.PAY_5, customer.PAY_6,
            customer.PAY_7, customer.PAY_8, customer.PAY_9, customer.PAY_10, customer.PAY_11, customer.PAY_12,
            customer.BILL_AMT1, customer.BILL_AMT2, customer.BILL_AMT3, 
            customer.BILL_AMT4, customer.BILL_AMT5, customer.BILL_AMT6,
            customer.BILL_AMT7, customer.BILL_AMT8, customer.BILL_AMT9,
            customer.BILL_AMT10, customer.BILL_AMT11, customer.BILL_AMT12,
            customer.PAY_AMT1, customer.PAY_AMT2, customer.PAY_AMT3,
            customer.PAY_AMT4, customer.PAY_AMT5, customer.PAY_AMT6,
            customer.PAY_AMT7, customer.PAY_AMT8, customer.PAY_AMT9,
            customer.PAY_AMT10, customer.PAY_AMT11, customer.PAY_AMT12,
            cmnd
        )
        
        success = self.db.execute_query(query, params)
        
        if success:
            print(f"âœ“ ÄÃ£ cáº­p nháº­t customer CMND: {cmnd}")
        else:
            print(f"âœ— KhÃ´ng thá»ƒ cáº­p nháº­t customer CMND: {cmnd}")
        
        return success
    
    def delete_customer(self, cmnd: str) -> bool:
        """
        XÃ³a khÃ¡ch hÃ ng theo CMND
        
        Args:
            cmnd: Sá»‘ CMND cáº§n xÃ³a
        
        Returns:
            True náº¿u thÃ nh cÃ´ng, False náº¿u tháº¥t báº¡i
        """
        query = "DELETE FROM customers WHERE customer_id_card = %s"
        success = self.db.execute_query(query, (cmnd,))
        
        if success:
            print(f"âœ“ ÄÃ£ xÃ³a customer CMND: {cmnd}")
        else:
            print(f"âœ— KhÃ´ng thá»ƒ xÃ³a customer CMND: {cmnd}")
        
        return success
