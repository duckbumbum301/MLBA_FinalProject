-- ================================================
-- Bảng USER - Quản lý tài khoản đăng nhập
-- ================================================

CREATE TABLE IF NOT EXISTS `user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('Admin', 'Technical', 'Secretary') NOT NULL DEFAULT 'Secretary',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert 3 demo users (password đã hash bằng bcrypt)
-- Password cho tất cả: "123"
-- Hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY.4HYoVYYlDqBu

INSERT INTO `user` (`username`, `password_hash`, `role`) VALUES
    ('babyshark', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY.4HYoVYYlDqBu', 'Admin'),
    ('fathershark', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY.4HYoVYYlDqBu', 'Technical'),
    ('momshark', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY.4HYoVYYlDqBu', 'Secretary')
ON DUPLICATE KEY UPDATE 
    `password_hash` = VALUES(`password_hash`),
    `role` = VALUES(`role`);
