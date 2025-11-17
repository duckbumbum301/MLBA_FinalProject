-- ================================================
-- Bảng PREDICTIONS_LOG - Lịch sử dự báo
-- ================================================

CREATE TABLE IF NOT EXISTS `predictions_log` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `customer_id` INT COMMENT 'Foreign key tới customers.id (nullable)',
    `user_id` INT COMMENT 'User thực hiện dự báo',
    `model_name` VARCHAR(50) NOT NULL COMMENT 'Tên mô hình ML đã dùng',
    `model_version` VARCHAR(50) DEFAULT 'v1.0' COMMENT 'Version của model',
    `predicted_label` TINYINT NOT NULL COMMENT '0=Không vỡ nợ, 1=Vỡ nợ',
    `probability` DECIMAL(5, 4) NOT NULL COMMENT 'Xác suất vỡ nợ (0-1)',
    `confidence_score` DECIMAL(5, 4) COMMENT 'Độ tin cậy của dự báo',
    `cluster_id` INT COMMENT 'Cluster của khách hàng',
    `raw_input_json` TEXT COMMENT 'Dữ liệu input dạng JSON',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer (`customer_id`),
    INDEX idx_user (`user_id`),
    INDEX idx_model (`model_name`),
    INDEX idx_created (`created_at`),
    INDEX idx_confidence (`confidence_score` DESC),
    FOREIGN KEY (`customer_id`) REFERENCES `customers`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
