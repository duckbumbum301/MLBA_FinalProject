-- ================================================
-- Bảng MODEL_REGISTRY - Quản lý các mô hình ML
-- ================================================

CREATE TABLE IF NOT EXISTS `model_registry` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `model_name` VARCHAR(50) UNIQUE NOT NULL,
    `model_type` ENUM('Single', 'Ensemble') DEFAULT 'Single',
    `algorithm` VARCHAR(50),  -- 'XGBoost', 'LightGBM', 'CatBoost', etc.
    `version` VARCHAR(20) DEFAULT '1.0',
    
    -- Performance Metrics
    `auc_score` DECIMAL(5,4),
    `accuracy` DECIMAL(5,4),
    `precision_score` DECIMAL(5,4),
    `recall_score` DECIMAL(5,4),
    `f1_score` DECIMAL(5,4),
    
    -- Status
    `is_active` BOOLEAN DEFAULT FALSE,
    `training_time` INT,  -- seconds
    `trained_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `trained_by` VARCHAR(50),  -- username
    
    -- File Information
    `model_path` VARCHAR(255),
    `model_size_mb` DECIMAL(10,2),
    
    INDEX idx_active (`is_active`),
    INDEX idx_auc (`auc_score` DESC),
    INDEX idx_trained_at (`trained_at` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert existing 3 models
INSERT INTO `model_registry` 
    (`model_name`, `model_type`, `algorithm`, `auc_score`, `accuracy`, `precision_score`, 
     `recall_score`, `f1_score`, `is_active`, `model_path`) 
VALUES
    ('XGBoost', 'Single', 'XGBoost', 0.7604, 0.8200, 0.7800, 0.8500, 0.8100, TRUE, 'outputs/models/xgb_model.pkl'),
    ('LightGBM', 'Single', 'LightGBM', 0.7811, 0.8300, 0.7900, 0.8600, 0.8200, FALSE, 'outputs/models/lgbm_model.pkl'),
    ('LogisticRegression', 'Single', 'LogisticRegression', 0.7099, 0.7500, 0.7200, 0.7800, 0.7400, FALSE, 'outputs/models/lr_cal_model.pkl')
ON DUPLICATE KEY UPDATE 
    `auc_score` = VALUES(`auc_score`),
    `accuracy` = VALUES(`accuracy`);
