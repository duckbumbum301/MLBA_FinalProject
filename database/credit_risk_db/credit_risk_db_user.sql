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
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('User','Admin') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'User',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `full_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  KEY `idx_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'babyshark','$2b$12$3jGm14C9GlOONZhCsAHhPuQmGja08lPvreGq3SQWQiGRYSMXbcsLm','User','2025-11-16 17:49:13','Nhân viên A',NULL,'2025-11-18 12:16:41',1),(2,'fathershark','$2b$12$3jGm14C9GlOONZhCsAHhPuQmGja08lPvreGq3SQWQiGRYSMXbcsLm','Admin','2025-11-16 17:49:13','Quản trị viên',NULL,'2025-11-20 18:52:28',1),(3,'momshark','$2b$12$3jGm14C9GlOONZhCsAHhPuQmGja08lPvreGq3SQWQiGRYSMXbcsLm','User','2025-11-16 17:49:13','Nhân viên B',NULL,'2025-11-20 18:14:53',1),(4,'ilovetranduythanh1','$2b$12$TH4gz3tb6YZC6mBMWArvx.GKa6whRix6gj7Rk7hu8XBAncSbTigeC','User','2025-11-20 13:22:05',NULL,NULL,'2025-11-20 18:32:56',1),(5,'ilovetranduythanh2','$2b$12$FU5KYBrhcpTbfRvxQ5hDpeAo8MhB/idwURdWqOTETMsj8Vwv8DycC','Admin','2025-11-20 13:25:48',NULL,NULL,'2025-11-20 19:39:27',1),(6,'meomeo1','$2b$12$4kX.ZGg6koVIgQZQ2pb3fOyyXVlKKXh6hafDXaHLVywZB/ll02B4K','User','2025-11-20 14:15:24',NULL,NULL,NULL,1),(7,'ilovetdt123','$2b$12$k8e88wxfewQyHTPUqFJoeenPfRHzcw/P6nLR4MoUItkgj5aLhnIfC','User','2025-11-20 14:15:30',NULL,NULL,NULL,1),(8,'meomeomeo','$2b$12$4hrvTdG4fM.ChQnhBtPGxu8HYQvmaO0bLRIHJND6bp/AmXlgpaRAm','User','2025-11-20 14:15:32',NULL,NULL,NULL,1),(9,'ilovetdt3','$2b$12$bH7aHy7VYtFWkooPn2l.lusq8blOzBBijYJQLCh834s4tDIk3u6ia','User','2025-11-20 14:21:36',NULL,NULL,NULL,1),(10,'ilovetdt5000','$2b$12$jBz3Yi9yDrWa8fuTdzOwq.1i2o69AgfzGdVFHqcNkT.Z7dGjtasZS','User','2025-11-20 18:22:27',NULL,NULL,NULL,1),(11,'ilovetdt1000000','$2b$12$OGrH66mbmdCo2SzJGaMs8OIn9Mw19qbgo0czhoZH5LmHKE0.U4kUu','User','2025-11-20 18:22:29',NULL,NULL,NULL,1),(12,'ilovetdt1000','$2b$12$.Ak33Ofktrjoj/QTk7L2K.aG74CvACYpPTWyUX.ZL0EWOD.xtcTVm','User','2025-11-20 18:22:30',NULL,NULL,NULL,1),(13,'welovemrtdt','$2b$12$3TyJaqvqTjwGh.hxKLEdzeKhczXiKbYRDn5eVbLpiDlhIPIveHhLS','User','2025-11-20 18:26:58',NULL,NULL,NULL,1),(14,'aenytdtlancuoi','$2b$12$pBjqGtQ08A.IxYzQPOWgIuAhxf0KdbuV6hAQVrUzeCu7dH6Q/I/a2','User','2025-11-20 19:39:34',NULL,NULL,NULL,1);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
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
