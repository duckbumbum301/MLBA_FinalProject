-- ================================================
-- Bảng DATA_QUALITY_LOG - Theo dõi chất lượng dữ liệu
-- ================================================

CREATE TABLE IF NOT EXISTS `data_quality_log` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `record_id` INT,
    `record_type` ENUM('Customer', 'Prediction'),
    `issue_type` VARCHAR(100),  -- 'Outlier', 'Missing Value', 'Invalid Range'
    `severity` ENUM('Low', 'Medium', 'High'),
    `detection_method` VARCHAR(50),  -- 'Isolation Forest', 'LOF', 'Manual'
    `detected_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `detected_by` VARCHAR(50),
    
    `action_taken` ENUM('Deleted', 'Fixed', 'Ignored', 'Pending') DEFAULT 'Pending',
    `action_at` DATETIME,
    `action_by` VARCHAR(50),
    `notes` TEXT,
    
    INDEX idx_record (`record_id`),
    INDEX idx_issue (`issue_type`),
    INDEX idx_status (`action_taken`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
