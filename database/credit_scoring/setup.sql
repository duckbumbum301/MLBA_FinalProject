-- ================================================
-- SETUP SCRIPT - Tạo database và các bảng
-- Chạy script này để khởi tạo toàn bộ database
-- ================================================

-- Tạo database nếu chưa có
CREATE DATABASE IF NOT EXISTS `credit_risk_db` 
    DEFAULT CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Sử dụng database
USE `credit_risk_db`;

-- Tạo các bảng (source từ các file riêng)
SOURCE user.sql;
SOURCE customers.sql;
SOURCE predictions_log.sql;

-- Hiển thị danh sách bảng đã tạo
SHOW TABLES;

-- Kiểm tra user demo
SELECT username, role FROM `user`;
