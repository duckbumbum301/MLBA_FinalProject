-- ================================================
-- Bảng AI_CHAT_HISTORY - Lịch sử chat với Gemini AI
-- ================================================

CREATE TABLE IF NOT EXISTS `ai_chat_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT,
    `context_type` VARCHAR(50),  -- 'Prediction', 'Model Comparison', 'General'
    `context_data` JSON,
    `user_message` TEXT,
    `ai_response` TEXT,
    `response_time_ms` INT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user (`user_id`),
    INDEX idx_created (`created_at` DESC),
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
