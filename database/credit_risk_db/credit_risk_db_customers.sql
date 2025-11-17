-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: credit_risk_db
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_id_card` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `LIMIT_BAL` decimal(12,2) NOT NULL COMMENT 'Hạn mức thẻ tín dụng',
  `SEX` tinyint NOT NULL COMMENT '1=Nam, 2=Nữ',
  `EDUCATION` tinyint NOT NULL COMMENT '1=Cao học, 2=Đại học, 3=Trung học, 4=Khác',
  `MARRIAGE` tinyint NOT NULL COMMENT '1=Kết hôn, 2=Độc thân, 3=Khác',
  `AGE` int NOT NULL COMMENT 'Tuổi',
  `PAY_0` tinyint NOT NULL COMMENT 'Trạng thái thanh toán tháng 12',
  `PAY_2` tinyint NOT NULL COMMENT 'Trạng thái thanh toán tháng 11',
  `PAY_3` tinyint NOT NULL COMMENT 'Trạng thái thanh toán tháng 10',
  `PAY_4` tinyint NOT NULL COMMENT 'Trạng thái thanh toán tháng 9',
  `PAY_5` tinyint NOT NULL COMMENT 'Trạng thái thanh toán tháng 8',
  `PAY_6` tinyint NOT NULL COMMENT 'Trạng thái thanh toán tháng 7',
  `PAY_7` tinyint NOT NULL COMMENT 'Trạng thái thanh toán tháng 6',
  `PAY_8` tinyint NOT NULL COMMENT 'Trạng thái thanh toán tháng 5',
  `PAY_9` tinyint NOT NULL COMMENT 'Trạng thái thanh toán tháng 4',
  `PAY_10` tinyint NOT NULL COMMENT 'Trạng thái thanh toán tháng 3',
  `PAY_11` tinyint NOT NULL COMMENT 'Trạng thái thanh toán tháng 2',
  `PAY_12` tinyint NOT NULL COMMENT 'Trạng thái thanh toán tháng 1',
  `BILL_AMT1` decimal(12,2) NOT NULL COMMENT 'Số dư sao kê tháng 12',
  `BILL_AMT2` decimal(12,2) NOT NULL COMMENT 'Số dư sao kê tháng 11',
  `BILL_AMT3` decimal(12,2) NOT NULL COMMENT 'Số dư sao kê tháng 10',
  `BILL_AMT4` decimal(12,2) NOT NULL COMMENT 'Số dư sao kê tháng 9',
  `BILL_AMT5` decimal(12,2) NOT NULL COMMENT 'Số dư sao kê tháng 8',
  `BILL_AMT6` decimal(12,2) NOT NULL COMMENT 'Số dư sao kê tháng 7',
  `BILL_AMT7` decimal(12,2) NOT NULL COMMENT 'Số dư sao kê tháng 6',
  `BILL_AMT8` decimal(12,2) NOT NULL COMMENT 'Số dư sao kê tháng 5',
  `BILL_AMT9` decimal(12,2) NOT NULL COMMENT 'Số dư sao kê tháng 4',
  `BILL_AMT10` decimal(12,2) NOT NULL COMMENT 'Số dư sao kê tháng 3',
  `BILL_AMT11` decimal(12,2) NOT NULL COMMENT 'Số dư sao kê tháng 2',
  `BILL_AMT12` decimal(12,2) NOT NULL COMMENT 'Số dư sao kê tháng 1',
  `PAY_AMT1` decimal(12,2) NOT NULL COMMENT 'Số tiền thanh toán tháng 12',
  `PAY_AMT2` decimal(12,2) NOT NULL COMMENT 'Số tiền thanh toán tháng 11',
  `PAY_AMT3` decimal(12,2) NOT NULL COMMENT 'Số tiền thanh toán tháng 10',
  `PAY_AMT4` decimal(12,2) NOT NULL COMMENT 'Số tiền thanh toán tháng 9',
  `PAY_AMT5` decimal(12,2) NOT NULL COMMENT 'Số tiền thanh toán tháng 8',
  `PAY_AMT6` decimal(12,2) NOT NULL COMMENT 'Số tiền thanh toán tháng 7',
  `PAY_AMT7` decimal(12,2) NOT NULL COMMENT 'Số tiền thanh toán tháng 6',
  `PAY_AMT8` decimal(12,2) NOT NULL COMMENT 'Số tiền thanh toán tháng 5',
  `PAY_AMT9` decimal(12,2) NOT NULL COMMENT 'Số tiền thanh toán tháng 4',
  `PAY_AMT10` decimal(12,2) NOT NULL COMMENT 'Số tiền thanh toán tháng 3',
  `PAY_AMT11` decimal(12,2) NOT NULL COMMENT 'Số tiền thanh toán tháng 2',
  `PAY_AMT12` decimal(12,2) NOT NULL COMMENT 'Số tiền thanh toán tháng 1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_customer_id` (`customer_id_card`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-17 22:01:28
