"""
Gemini AI Service
Service tích hợp Google Gemini cho AI Assistant
"""
import json
import decimal
import time
from typing import Optional, Dict, Any
from datetime import datetime

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except (ImportError, TypeError) as e:
    GEMINI_AVAILABLE = False
    if isinstance(e, TypeError):
        print("⚠ google-generativeai không tương thích với Python 3.14. Hãy dùng Python 3.11-3.12")
    else:
        print("⚠ google-generativeai not installed. Install with: pip install google-generativeai")

from config.gemini_config import GeminiConfig
from database.connector import DatabaseConnector


class GeminiService:
    """
    Service quản lý tương tác với Gemini AI
    """
    
    def __init__(self, db_connector: DatabaseConnector, user_id: int):
        """
        Khởi tạo Gemini Service
        
        Args:
            db_connector: Database connector
            user_id: ID của user đang sử dụng
        """
        self.db = db_connector
        self.user_id = user_id
        self.model = None
        self.chat_session = None
        
        # Initialize if API key is configured
        if GEMINI_AVAILABLE and GeminiConfig.is_configured():
            try:
                genai.configure(api_key=GeminiConfig.API_KEY)
                
                self.model = genai.GenerativeModel(
                    model_name=GeminiConfig.MODEL_NAME,
                    generation_config={
                        "temperature": GeminiConfig.TEMPERATURE,
                        "top_p": GeminiConfig.TOP_P,
                        "top_k": GeminiConfig.TOP_K,
                        "max_output_tokens": GeminiConfig.MAX_OUTPUT_TOKENS,
                    },
                    safety_settings=GeminiConfig.SAFETY_SETTINGS,
                    system_instruction=GeminiConfig.SYSTEM_INSTRUCTION
                )
                
                self.chat_session = self.model.start_chat(history=[])
                print("✓ Gemini AI initialized successfully")
                
            except Exception as e:
                print(f"✗ Failed to initialize Gemini: {e}")
                self.model = None
        else:
            if not GEMINI_AVAILABLE:
                print("✗ Gemini not available: package not installed")
            elif not GeminiConfig.is_configured():
                print("✗ Gemini not configured: Please set API_KEY in config/gemini_config.py")
    
    def is_available(self) -> bool:
        """Kiểm tra Gemini có sẵn sàng không"""
        return self.model is not None
    
    def send_message(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None,
        context_type: str = "General"
    ) -> str:
        """
        Gửi message tới Gemini
        
        Args:
            message: Câu hỏi/message từ user
            context: Context data (customer data, prediction results, etc.)
            context_type: Loại context ('Prediction', 'Model Comparison', 'General')
        
        Returns:
            Response từ Gemini
        """
        if not self.is_available():
            return "❌ Gemini AI chưa được cấu hình. Vui lòng thêm API key vào config/gemini_config.py"
        
        try:
            # Prepare full prompt with context
            def _to_json_safe(obj):
                if obj is None:
                    return None
                if isinstance(obj, (str, int, float, bool)):
                    return obj
                if isinstance(obj, decimal.Decimal):
                    try:
                        return float(obj)
                    except Exception:
                        return float(str(obj))
                if isinstance(obj, datetime):
                    return obj.isoformat()
                if isinstance(obj, bytes):
                    try:
                        return obj.decode('utf-8', errors='ignore')
                    except Exception:
                        return str(obj)
                if isinstance(obj, (list, tuple, set)):
                    return [ _to_json_safe(x) for x in list(obj) ]
                if isinstance(obj, dict):
                    return { str(k): _to_json_safe(v) for k, v in obj.items() }
                try:
                    return json.loads(json.dumps(obj))
                except Exception:
                    return str(obj)

            if context:
                context_safe = _to_json_safe(context)
                context_str = json.dumps(context_safe, indent=2, ensure_ascii=False)
                full_prompt = f"""
Context Data:
```json
{context_str}
```

User Question: {message}

Hãy phân tích và trả lời câu hỏi dựa trên context data ở trên.
"""
            else:
                full_prompt = message
            
            # Send to Gemini
            start_time = time.time()
            response = self.chat_session.send_message(full_prompt)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            try:
                response_text = getattr(response, 'text', None)
                if not response_text:
                    # Try generate_content as a fallback
                    try:
                        alt = self.model.generate_content(full_prompt)
                        response_text = getattr(alt, 'text', None)
                    except Exception:
                        response_text = None
                if not response_text:
                    # Build safety-aware message
                    reason = None
                    try:
                        d = response.to_dict()
                        reason = str(d.get('candidates',[{}])[0].get('finish_reason'))
                    except Exception:
                        pass
                    response_text = f"⚠ Không thể đọc phản hồi từ Gemini. finish_reason={reason or 'unknown'}. Vui lòng thử lại với câu hỏi rõ ràng hơn."
            except Exception:
                response_text = "⚠ Không thể đọc phản hồi từ Gemini."
            
            # Save to database
            self._save_chat_history(
                context_type=context_type,
                context_data=context_safe if context else None,
                user_message=message,
                ai_response=response_text,
                response_time_ms=response_time_ms
            )
            
            return response_text
        
        except Exception as e:
            error_msg = f"❌ Lỗi khi gọi Gemini API: {str(e)}"
            print(error_msg)
            return error_msg
    
    def explain_prediction(
        self, 
        customer_data: Dict[str, Any], 
        prediction_result: Dict[str, Any]
    ) -> str:
        """
        Giải thích kết quả dự báo cho khách hàng
        
        Args:
            customer_data: Dữ liệu khách hàng (41 features)
            prediction_result: Kết quả dự báo (probability, label, model_name)
        
        Returns:
            Giải thích từ Gemini
        """
        context = {
            "type": "Prediction Explanation",
            "customer": customer_data,
            "prediction": prediction_result
        }
        
        prompt = f"""
Phân tích kết quả dự báo rủi ro tín dụng cho khách hàng này:

**Kết quả dự báo:**
- Model: {prediction_result.get('model_name', 'XGBoost')}
- Xác suất vỡ nợ: {prediction_result.get('probability', 0)*100:.1f}%
- Đánh giá: {prediction_result.get('risk_label', 'Unknown')}

**Yêu cầu:**
1. Giải thích tại sao khách hàng này có mức rủi ro như vậy
2. Phân tích 3-5 yếu tố quan trọng nhất
3. So sánh với khách hàng trung bình
4. Đưa ra 3 khuyến nghị cụ thể

Trả lời ngắn gọn, dùng bullet points và emoji.
"""
        
        return self.send_message(prompt, context, "Prediction")
    
    def compare_models(
        self, 
        customer_data: Dict[str, Any],
        predictions: Dict[str, Any]
    ) -> str:
        """
        So sánh kết quả từ nhiều models
        
        Args:
            customer_data: Dữ liệu khách hàng
            predictions: Dict {model_name: prediction_result}
        
        Returns:
            Phân tích so sánh từ Gemini
        """
        context = {
            "type": "Model Comparison",
            "customer": customer_data,
            "predictions": predictions
        }
        
        prompt = """
So sánh kết quả dự đoán từ các mô hình Machine Learning khác nhau:

**Yêu cầu:**
1. So sánh xác suất từ từng model
2. Giải thích tại sao có sự khác biệt
3. Model nào đáng tin cậy nhất cho trường hợp này?
4. Có điểm bất thường nào không?

Trả lời ngắn gọn với bullet points.
"""
        
        return self.send_message(prompt, context, "Model Comparison")
    
    def generate_report(
        self, 
        stats: Dict[str, Any],
        report_type: str = "monthly"
    ) -> str:
        """
        Tạo báo cáo tự động
        
        Args:
            stats: Dữ liệu thống kê
            report_type: Loại báo cáo ('monthly', 'weekly', 'custom')
        
        Returns:
            Báo cáo Markdown từ Gemini
        """
        context = {
            "type": "Report Generation",
            "report_type": report_type,
            "statistics": stats
        }
        
        prompt = f"""
Tạo báo cáo {report_type} cho hệ thống Credit Risk Scoring:

**Format báo cáo (Markdown):**
1. ## 📊 Tóm Tắt Tổng Quan (Executive Summary)
2. ## 📈 Thống Kê Dự Báo (Prediction Statistics)
3. ## 🎯 Phân Tích Rủi Ro (Risk Analysis)
4. ## 🤖 Hiệu Suất Mô Hình (Model Performance)
5. ## 💡 Khuyến Nghị (Recommendations)
6. ## 📉 Xu Hướng (Trends)

Dùng tables, bullet points, và emoji. Ngắn gọn, tập trung vào insights quan trọng.
"""
        
        return self.send_message(prompt, context, "Report Generation")
    
    def ask_general(self, question: str) -> str:
        """
        Hỏi câu hỏi chung về credit risk
        
        Args:
            question: Câu hỏi
        
        Returns:
            Câu trả lời từ Gemini
        """
        return self.send_message(question, None, "General")
    
    def _save_chat_history(
        self,
        context_type: str,
        context_data: Optional[Dict],
        user_message: str,
        ai_response: str,
        response_time_ms: int
    ):
        """Lưu lịch sử chat vào database"""
        try:
            query = """
                INSERT INTO ai_chat_history 
                (user_id, context_type, context_data, user_message, ai_response, response_time_ms)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            def _to_json_safe_db(obj):
                # Reuse same logic as above but avoid circular reference
                if obj is None:
                    return None
                if isinstance(obj, (str, int, float, bool)):
                    return obj
                if isinstance(obj, decimal.Decimal):
                    try:
                        return float(obj)
                    except Exception:
                        return float(str(obj))
                if isinstance(obj, datetime):
                    return obj.isoformat()
                if isinstance(obj, bytes):
                    try:
                        return obj.decode('utf-8', errors='ignore')
                    except Exception:
                        return str(obj)
                if isinstance(obj, (list, tuple, set)):
                    return [ _to_json_safe_db(x) for x in list(obj) ]
                if isinstance(obj, dict):
                    return { str(k): _to_json_safe_db(v) for k, v in obj.items() }
                return str(obj)

            context_json = json.dumps(_to_json_safe_db(context_data)) if context_data else None
            
            self.db.execute_query(
                query,
                (self.user_id, context_type, context_json, user_message, ai_response, response_time_ms)
            )
        except Exception as e:
            print(f"⚠ Could not save chat history: {e}")
    
    def get_chat_history(self, limit: int = 50) -> list:
        """
        Lấy lịch sử chat của user
        
        Args:
            limit: Số lượng messages tối đa
        
        Returns:
            List of chat messages
        """
        query = """
            SELECT context_type, user_message, ai_response, created_at
            FROM ai_chat_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        
        results = self.db.fetch_all(query, (self.user_id, limit))
        
        history = []
        for row in results:
            history.append({
                'context_type': row[0],
                'user_message': row[1],
                'ai_response': row[2],
                'created_at': row[3]
            })
        
        return list(reversed(history))  # Oldest first
    
    def clear_chat_history(self):
        """Xóa lịch sử chat và reset session"""
        if self.chat_session and self.model:
            self.chat_session = self.model.start_chat(history=[])
            print("✓ Chat session reset")
