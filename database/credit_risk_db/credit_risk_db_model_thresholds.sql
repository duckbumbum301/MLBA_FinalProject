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
-- Table structure for table `model_thresholds`
--

DROP TABLE IF EXISTS `model_thresholds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `model_thresholds` (
  `id` int NOT NULL AUTO_INCREMENT,
  `model_name` varchar(64) NOT NULL,
  `threshold` decimal(5,4) NOT NULL,
  `updated_by` varchar(64) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_model` (`model_name`),
  KEY `idx_created` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `model_thresholds`
--

LOCK TABLES `model_thresholds` WRITE;
/*!40000 ALTER TABLE `model_thresholds` DISABLE KEYS */;
INSERT INTO `model_thresholds` VALUES (1,'XGBoost',0.5800,'admin','2025-11-20 05:03:20'),(2,'XGBoost',0.5500,'admin','2025-11-20 11:58:28'),(3,'XGBoost',0.3700,'admin','2025-11-20 12:52:35'),(4,'XGBoost',0.3700,'admin','2025-11-20 13:28:46'),(5,'LightGBM',0.5100,'admin','2025-11-20 14:27:20'),(6,'XGBoost',0.3700,'admin','2025-11-20 14:47:00'),(7,'XGBoost',0.3700,'admin','2025-11-20 14:49:01'),(8,'LightGBM',0.5100,'admin','2025-11-20 18:54:04'),(9,'LightGBM',0.5100,'admin','2025-11-20 18:56:49'),(10,'LightGBM',0.5400,'admin','2025-11-20 18:56:57');
/*!40000 ALTER TABLE `model_thresholds` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-20 19:43:41
