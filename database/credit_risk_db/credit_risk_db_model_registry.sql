-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: credit_risk_db
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `model_registry`
--

DROP TABLE IF EXISTS `model_registry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `model_registry` (
  `id` int NOT NULL AUTO_INCREMENT,
  `model_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `model_type` enum('Single','Ensemble') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'Single',
  `algorithm` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `version` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '1.0',
  `auc_score` decimal(5,4) DEFAULT NULL,
  `accuracy` decimal(5,4) DEFAULT NULL,
  `precision_score` decimal(5,4) DEFAULT NULL,
  `recall_score` decimal(5,4) DEFAULT NULL,
  `f1_score` decimal(5,4) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '0',
  `training_time` int DEFAULT NULL,
  `trained_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `trained_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `model_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `model_size_mb` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `model_name` (`model_name`),
  KEY `idx_active` (`is_active`),
  KEY `idx_auc` (`auc_score` DESC)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `model_registry`
--

LOCK TABLES `model_registry` WRITE;
/*!40000 ALTER TABLE `model_registry` DISABLE KEYS */;
INSERT INTO `model_registry` VALUES (1,'XGBoost','Single','XGBoost','1.0',0.7604,0.8200,0.7800,0.8500,0.8100,1,NULL,'2025-11-17 16:39:32',NULL,'outputs/models/xgb_model.pkl',NULL),(2,'LightGBM','Single','LightGBM','1.0',0.7811,0.8300,0.7900,0.8600,0.8200,0,NULL,'2025-11-17 16:39:32',NULL,'outputs/models/lgbm_model.pkl',NULL),(3,'LogisticRegression','Single','LogisticRegression','1.0',0.7099,0.7500,0.7200,0.7800,0.7400,0,NULL,'2025-11-17 16:39:32',NULL,'outputs/models/lr_cal_model.pkl',NULL);
/*!40000 ALTER TABLE `model_registry` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-18 12:24:11
