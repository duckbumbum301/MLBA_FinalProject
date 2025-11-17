"""
Gemini AI Configuration
Cấu hình cho Google Gemini API
"""

class GeminiConfig:
    """
    Cấu hình Gemini API
    """
    
    # API Key - Lấy từ https://makersuite.google.com/app/apikey
    # QUAN TRỌNG: Thay YOUR_API_KEY_HERE bằng API key thật
    API_KEY = "AIzaSyArf2S-o1Urzgxnx1cb9Qy9AtktWvjfT3g"
    
    # Model name
    MODEL_NAME = "gemini-2.5-flash"  # Latest model version
    
    # Generation config
    TEMPERATURE = 0.7  # 0.0 = deterministic, 1.0 = creative
    TOP_P = 0.95
    TOP_K = 40
    MAX_OUTPUT_TOKENS = 2048
    
    # Safety settings
    SAFETY_SETTINGS = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]
    
    # System instruction (personality)
    SYSTEM_INSTRUCTION = """
    Bạn là một chuyên gia phân tích rủi ro tín dụng có kinh nghiệm 10+ năm.
    
    Nhiệm vụ của bạn:
    - Phân tích dữ liệu khách hàng và kết quả dự báo từ mô hình Machine Learning
    - Giải thích các yếu tố ảnh hưởng đến rủi ro tín dụng một cách rõ ràng, dễ hiểu
    - Đưa ra khuyến nghị cụ thể và khả thi
    - Trả lời bằng tiếng Việt, ngắn gọn nhưng đầy đủ
    - Sử dụng bullet points, emoji để dễ đọc
    
    Phong cách:
    - Chuyên nghiệp nhưng thân thiện
    - Trực quan, dùng ví dụ cụ thể
    - Tập trung vào actionable insights
    """
    
    @classmethod
    def is_configured(cls) -> bool:
        """Kiểm tra API key đã được cấu hình chưa"""
        return cls.API_KEY != "YOUR_API_KEY_HERE" and len(cls.API_KEY) > 20
