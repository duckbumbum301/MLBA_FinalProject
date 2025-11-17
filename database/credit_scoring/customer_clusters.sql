-- ================================================
-- Bảng CUSTOMER_CLUSTERS - Phân cụm khách hàng
-- ================================================

CREATE TABLE IF NOT EXISTS `customer_clusters` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `customer_id` INT,
    `cluster_id` INT,
    `risk_level` ENUM('Low', 'Medium', 'High', 'Critical'),
    `cluster_center_distance` DECIMAL(10,4),
    `clustered_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_customer (`customer_id`),
    INDEX idx_cluster (`cluster_id`),
    INDEX idx_risk (`risk_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
