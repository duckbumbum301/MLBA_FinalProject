"""
Query Service
Service xử lý truy vấn database (customers, predictions_log)
"""
import json
from typing import List, Optional, Dict
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
        raw_input_dict: Dict
    ) -> bool:
        """
        Lưu lịch sử dự báo vào database
        
        Args:
            customer_id: ID khách hàng (nullable)
            model_name: Tên mô hình ML
            predicted_label: Nhãn dự đoán (0/1)
            probability: Xác suất
            raw_input_dict: Dict chứa input đầy đủ
        
        Returns:
            True nếu thành công, False nếu thất bại
        """
        # Chuyển dict thành JSON string
        raw_input_json = json.dumps(raw_input_dict)
        
        query = """
            INSERT INTO predictions_log (
                customer_id, model_name, predicted_label, probability, raw_input_json
            ) VALUES (%s, %s, %s, %s, %s)
        """
        
        params = (customer_id, model_name, predicted_label, probability, raw_input_json)
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
