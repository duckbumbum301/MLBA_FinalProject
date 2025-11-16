-- ================================================
-- Bảng CUSTOMERS - Thông tin khách hàng
-- ================================================

CREATE TABLE IF NOT EXISTS `customers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `customer_name` VARCHAR(100),
    `customer_id_card` VARCHAR(50),
    
    -- Thông tin cá nhân (23 fields từ UCI Credit Card dataset)
    `LIMIT_BAL` DECIMAL(12, 2) NOT NULL COMMENT 'Hạn mức thẻ tín dụng',
    `SEX` TINYINT NOT NULL COMMENT '1=Nam, 2=Nữ',
    `EDUCATION` TINYINT NOT NULL COMMENT '1=Cao học, 2=Đại học, 3=Trung học, 4=Khác',
    `MARRIAGE` TINYINT NOT NULL COMMENT '1=Kết hôn, 2=Độc thân, 3=Khác',
    `AGE` INT NOT NULL COMMENT 'Tuổi',
    
    -- Lịch sử thanh toán (PAY_0 ~ PAY_11) - 12 tháng
    `PAY_0` TINYINT NOT NULL COMMENT 'Trạng thái thanh toán tháng 12',
    `PAY_2` TINYINT NOT NULL COMMENT 'Trạng thái thanh toán tháng 11',
    `PAY_3` TINYINT NOT NULL COMMENT 'Trạng thái thanh toán tháng 10',
    `PAY_4` TINYINT NOT NULL COMMENT 'Trạng thái thanh toán tháng 9',
    `PAY_5` TINYINT NOT NULL COMMENT 'Trạng thái thanh toán tháng 8',
    `PAY_6` TINYINT NOT NULL COMMENT 'Trạng thái thanh toán tháng 7',
    `PAY_7` TINYINT NOT NULL COMMENT 'Trạng thái thanh toán tháng 6',
    `PAY_8` TINYINT NOT NULL COMMENT 'Trạng thái thanh toán tháng 5',
    `PAY_9` TINYINT NOT NULL COMMENT 'Trạng thái thanh toán tháng 4',
    `PAY_10` TINYINT NOT NULL COMMENT 'Trạng thái thanh toán tháng 3',
    `PAY_11` TINYINT NOT NULL COMMENT 'Trạng thái thanh toán tháng 2',
    `PAY_12` TINYINT NOT NULL COMMENT 'Trạng thái thanh toán tháng 1',
    
    -- Số dư sao kê (BILL_AMT1 ~ BILL_AMT12) - 12 tháng
    `BILL_AMT1` DECIMAL(12, 2) NOT NULL COMMENT 'Số dư sao kê tháng 12',
    `BILL_AMT2` DECIMAL(12, 2) NOT NULL COMMENT 'Số dư sao kê tháng 11',
    `BILL_AMT3` DECIMAL(12, 2) NOT NULL COMMENT 'Số dư sao kê tháng 10',
    `BILL_AMT4` DECIMAL(12, 2) NOT NULL COMMENT 'Số dư sao kê tháng 9',
    `BILL_AMT5` DECIMAL(12, 2) NOT NULL COMMENT 'Số dư sao kê tháng 8',
    `BILL_AMT6` DECIMAL(12, 2) NOT NULL COMMENT 'Số dư sao kê tháng 7',
    `BILL_AMT7` DECIMAL(12, 2) NOT NULL COMMENT 'Số dư sao kê tháng 6',
    `BILL_AMT8` DECIMAL(12, 2) NOT NULL COMMENT 'Số dư sao kê tháng 5',
    `BILL_AMT9` DECIMAL(12, 2) NOT NULL COMMENT 'Số dư sao kê tháng 4',
    `BILL_AMT10` DECIMAL(12, 2) NOT NULL COMMENT 'Số dư sao kê tháng 3',
    `BILL_AMT11` DECIMAL(12, 2) NOT NULL COMMENT 'Số dư sao kê tháng 2',
    `BILL_AMT12` DECIMAL(12, 2) NOT NULL COMMENT 'Số dư sao kê tháng 1',
    
    -- Số tiền thanh toán (PAY_AMT1 ~ PAY_AMT12) - 12 tháng
    `PAY_AMT1` DECIMAL(12, 2) NOT NULL COMMENT 'Số tiền thanh toán tháng 12',
    `PAY_AMT2` DECIMAL(12, 2) NOT NULL COMMENT 'Số tiền thanh toán tháng 11',
    `PAY_AMT3` DECIMAL(12, 2) NOT NULL COMMENT 'Số tiền thanh toán tháng 10',
    `PAY_AMT4` DECIMAL(12, 2) NOT NULL COMMENT 'Số tiền thanh toán tháng 9',
    `PAY_AMT5` DECIMAL(12, 2) NOT NULL COMMENT 'Số tiền thanh toán tháng 8',
    `PAY_AMT6` DECIMAL(12, 2) NOT NULL COMMENT 'Số tiền thanh toán tháng 7',
    `PAY_AMT7` DECIMAL(12, 2) NOT NULL COMMENT 'Số tiền thanh toán tháng 6',
    `PAY_AMT8` DECIMAL(12, 2) NOT NULL COMMENT 'Số tiền thanh toán tháng 5',
    `PAY_AMT9` DECIMAL(12, 2) NOT NULL COMMENT 'Số tiền thanh toán tháng 4',
    `PAY_AMT10` DECIMAL(12, 2) NOT NULL COMMENT 'Số tiền thanh toán tháng 3',
    `PAY_AMT11` DECIMAL(12, 2) NOT NULL COMMENT 'Số tiền thanh toán tháng 2',
    `PAY_AMT12` DECIMAL(12, 2) NOT NULL COMMENT 'Số tiền thanh toán tháng 1',
    
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer_id (`customer_id_card`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
