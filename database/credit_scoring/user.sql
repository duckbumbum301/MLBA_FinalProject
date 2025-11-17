-- ================================================
-- Bảng USER - Quản lý tài khoản đăng nhập (2 ROLES)
-- ================================================

CREATE TABLE IF NOT EXISTS `user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('User', 'Admin') NOT NULL DEFAULT 'User',
    `full_name` VARCHAR(100),
    `email` VARCHAR(100),
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `last_login` DATETIME,
    `is_active` BOOLEAN DEFAULT TRUE,
    INDEX idx_username (`username`),
    INDEX idx_role (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert demo users
-- Password cho tất cả: "123"
-- Hash (verified): $2b$12$3jGm14C9GlOONZhCsAHhPuQmGja08lPvreGq3SQWQiGRYSMXbcsLm

INSERT INTO `user` (`username`, `password_hash`, `role`, `full_name`) VALUES
    ('babyshark', '$2b$12$3jGm14C9GlOONZhCsAHhPuQmGja08lPvreGq3SQWQiGRYSMXbcsLm', 'User', 'Nhân viên A'),
    ('fathershark', '$2b$12$3jGm14C9GlOONZhCsAHhPuQmGja08lPvreGq3SQWQiGRYSMXbcsLm', 'Admin', 'Quản trị viên'),
    ('momshark', '$2b$12$3jGm14C9GlOONZhCsAHhPuQmGja08lPvreGq3SQWQiGRYSMXbcsLm', 'User', 'Nhân viên B')
ON DUPLICATE KEY UPDATE 
    `password_hash` = VALUES(`password_hash`),
    `role` = VALUES(`role`),
    `full_name` = VALUES(`full_name`);
