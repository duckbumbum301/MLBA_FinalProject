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
-- Table structure for table `ai_chat_history`
--

DROP TABLE IF EXISTS `ai_chat_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ai_chat_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `context_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `context_data` json DEFAULT NULL,
  `user_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `ai_response` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `response_time_ms` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_created` (`created_at` DESC)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ai_chat_history`
--

LOCK TABLES `ai_chat_history` WRITE;
/*!40000 ALTER TABLE `ai_chat_history` DISABLE KEYS */;
INSERT INTO `ai_chat_history` VALUES (1,1,'Hỏi chung về Credit Risk',NULL,'Giải thích credit risk scoring là gì?','Chào bạn, với kinh nghiệm hơn 10 năm trong ngành, tôi sẽ giúp bạn hiểu rõ về **Credit Risk Scoring** – một công cụ cốt lõi trong phân tích tín dụng. ?\n\n---\n\n### **Credit Risk Scoring (Hệ thống chấm điểm rủi ro tín dụng) là gì?**\n\nNói một cách đơn giản, đây là **hệ thống đánh giá định lượng** khả năng một khách hàng (cá nhân hoặc doanh nghiệp) sẽ **hoàn trả khoản vay đúng hạn** hay có nguy cơ **vỡ nợ**. Hệ thống này sẽ gán cho mỗi khách hàng một **điểm số cụ thể**, phản ánh mức độ rủi ro tín dụng của họ.\n\n---\n\n### **Tại sao Credit Risk Scoring lại quan trọng? (Lợi ích cốt lõi)**\n\nCredit Risk Scoring mang lại nhiều lợi ích to lớn cho các tổ chức tài chính:\n\n*   ? **Quyết định nhanh chóng & khách quan:** Tự động hóa quá trình đánh giá, giảm thiểu sự chủ quan và thiên vị của con người.\n*   *   **Ví dụ:** Thay vì mất hàng giờ phân tích từng hồ sơ, mô hình có thể',24236,'2025-11-17 17:03:43'),(2,1,'Hỏi chung về Credit Risk',NULL,'Giải thích credit risk scoring là gì?','Chào bạn,\n\n**Hệ thống chấm điểm rủi ro tín dụng (Credit Risk Scoring)** là một công cụ phân tích cực kỳ quan trọng, đóng vai trò \"người gác cổng\" trong ngành tài chính, giúp các tổ chức cho vay đánh giá khả năng trả nợ của khách hàng.\n\n? **Nó là gì?**\n*   Là một phương pháp định lượng sử dụng các mô hình thống kê và Machine Learning để gán một **điểm số** cho từng cá nhân hoặc doanh nghiệp.\n*   Điểm số này phản ánh **khả năng** khách hàng sẽ thanh toán các khoản nợ (vay, thẻ tín dụng...) đúng hạn và đầy đủ trong tương lai.\n\n? **Mục đích chính:**\n*   **Quyết định cho vay nhanh chóng & khách quan:** Tự động hóa quá trình đánh giá, giúp ngân hàng đưa ra quyết định \"Có nên cho vay không?\" và \"Cho vay bao nhiêu, với lãi suất nào?\" một cách hiệu quả và ít thiên vị.\n*   **Giảm thiểu rủi ro nợ xấu:** Xác định sớm những khách hàng có khả năng vỡ nợ cao để từ chối hoặc áp dụng các biện pháp phòng ngừa rủi ro phù hợp.\n*   **Tối ưu hóa lợi nhuận:** Phân bổ nguồn vốn hiệu quả hơn cho những khách hàng có rủi ro chấp nhận được, đồng thời đảm bảo lợi nhuận.\n\n? **Hoạt động như thế nào?**\nCác mô hình Credit Scoring phân tích rất nhiều dữ liệu từ khách hàng, bao gồm:\n*   **Lịch sử tín dụng:** ? Lịch sử trả nợ các khoản vay trước đó (có đúng hạn không?), số lượng tài khoản tín dụng đang có, mức độ sử dụng tín dụng.\n*   **Thông tin cá nhân/doanh nghiệp:** ?‍? Thu nhập, công việc, độ tuổi, tình trạng hôn nhân, địa chỉ cư trú, ngành nghề kinh doanh, tình hình tài chính doanh nghiệp.\n*   **Hành vi giao dịch:** ? Cách thức sử dụng tài khoản ngân hàng, tần suất giao dịch, số dư trung bình.\n\nDựa trên các yếu tố này, mô hình sẽ tính toán và đưa ra một điểm số.\n*   **Điểm càng cao** ⬆️: Rủi ro vỡ nợ càng thấp, khả năng được duyệt vay với điều kiện tốt càng cao.\n*   **Điểm càng thấp** ⬇️: Rủi ro vỡ nợ càng cao, khả năng bị từ chối hoặc phải chịu lãi suất cao hơn, hạn mức thấp hơn.\n\n⚖️ **Ví dụ dễ hiểu:**\nHãy hình dung Credit Score như một \"điểm thi\" về độ tin cậy tài chính của bạn.\n*   Nếu bạn đạt 800/1000 điểm, ngân hàng coi bạn là một \"học sinh giỏi\" có khả năng trả nợ rất cao.\n*   Nếu bạn chỉ đạt 400/1000 điểm, ngân hàng sẽ cẩn trọng hơn, có thể yêu cầu thêm tài sản đảm bảo hoặc từ chối cho vay để tránh rủi ro.\n\nTóm lại, Credit Risk Scoring là xương sống của quản lý rủi ro tín dụng hiện đại, giúp cân bằng giữa việc cung cấp tín dụng và bảo vệ tài sản của tổ chức tài chính.',19147,'2025-11-17 17:05:50'),(3,1,'Hỏi chung về Credit Risk',NULL,'nợ xấu','Chào bạn,\n\n**Nợ xấu (Non-Performing Loan - NPL)** là một thuật ngữ cực kỳ quan trọng trong ngành tài chính, dùng để chỉ các khoản vay mà người vay **không thể hoặc không thanh toán được** gốc và/hoặc lãi theo đúng thời hạn đã cam kết trong hợp đồng. ?\n\n? **Nó là gì?**\n*   Là các khoản nợ đã quá hạn thanh toán gốc và/hoặc lãi trong một khoảng thời gian nhất định, thường là **trên 90 ngày**.\n*   Khi một khoản vay trở thành nợ xấu, nó báo hiệu rủi ro cao rằng ngân hàng hoặc tổ chức tài chính sẽ **không thể thu hồi được đầy đủ** số tiền đã cho vay.\n\n? **Đặc điểm chính & Phân loại:**\nTại Việt Nam, nợ xấu thường được phân loại theo Thông tư 11/2021/TT-NHNN thành 3 nhóm chính dựa trên thời gian quá hạn:\n*   **Nhóm 3 (Nợ dưới tiêu chuẩn):** ⚠️ Các khoản nợ quá hạn từ **91 ngày đến 180 ngày**. Bắt đầu có dấu hiệu rủi ro.\n*   **Nhóm 4 (Nợ nghi ngờ):** ⛔ Các khoản nợ quá hạn từ **181 ngày đến 360 ngày**. Rủi ro cao hơn, khả năng mất vốn một phần.\n*   **Nhóm 5 (Nợ có khả năng mất vốn):** ? Các khoản nợ quá hạn **trên 360 ngày**. Rủi ro rất cao, khả năng mất vốn toàn bộ.\n\n? **Tại sao nợ xấu lại nghiêm trọng?**\nNợ xấu gây ra những tác động tiêu cực đáng kể cho cả người cho vay và nền kinh tế:\n\n**Đối với Ngân hàng/Tổ chức tài chính:**\n*   **Mất vốn & Giảm lợi nhuận:** ? Ngân hàng không thu hồi được tiền, ảnh hưởng trực tiếp đến lợi nhuận và nguồn vốn.\n*   **Tăng chi phí dự phòng:** ?️ Ngân hàng phải trích lập dự phòng rủi ro để bù đắp cho các khoản nợ xấu, làm giảm nguồn lực cho vay mới.\n*   **Ảnh hưởng đến dòng tiền:** ? Gây tắc nghẽn dòng tiền, giảm khả năng cấp tín dụng cho nền kinh tế.\n*   **Giảm uy tín:** ? Tỷ lệ nợ xấu cao có thể làm giảm niềm tin của nhà đầu tư và công chúng.\n\n**Đối với Nền kinh tế:**\n*   **Suy giảm tăng trưởng:** ? Nợ xấu kìm hãm khả năng cấp vốn cho doanh nghiệp và dự án, làm chậm tốc độ tăng trưởng kinh tế.\n*   **Rủi ro hệ thống:** ? Nếu tỷ lệ nợ xấu quá cao, có thể gây ra khủng hoảng tài chính toàn hệ thống.\n\n**Đối với Người vay:**\n*   **Ảnh hưởng lịch sử tín dụng:** ? Khi bị xếp vào nhóm nợ xấu, lịch sử tín dụng của cá nhân/doanh nghiệp sẽ bị ghi nhận tiêu cực trên CIC (Trung tâm Thông tin Tín dụng Quốc gia Việt Nam).\n*   **Khó vay vốn trong tương lai:** ❌ Các tổ chức tài chính khác sẽ rất e ngại khi cấp tín dụng cho người/doanh nghiệp có lịch sử nợ xấu, hoặc chỉ cấp với điều kiện rất khắt khe (lãi suất cao, tài sản đảm bảo lớn).\n\n⚖️ **Ví dụ dễ hiểu:**\nBạn cho bạn thân vay 10 triệu đồng, hứa trả sau 3 tháng.\n*   Nếu bạn ấy trả đúng hạn, đó là khoản nợ tốt.\n*   Nếu đến tháng thứ 4, thứ 5 bạn ấy vẫn chưa trả (quá hạn 30-60 ngày), đó là dấu hiệu của rủi ro.\n*   Nếu đến tháng thứ 7, thứ 8 (quá hạn 90-150 ngày), bạn ấy vẫn không trả và bắt đầu lảng tránh, đó chính là **nợ xấu (nhóm 3)**. Bạn sẽ bắt đầu lo lắng về khả năng thu hồi số tiền đó.\n\nTóm lại, nợ xấu là một \"vết sẹo\" trên bảng cân đối kế toán của ngân hàng và là một \"án treo\" đối với khả năng tiếp cận tín dụng của người vay trong tương lai. Việc quản lý và xử lý nợ xấu hiệu quả là yếu tố then chốt để duy trì sự ổn định và phát triển của hệ thống tài chính.',10955,'2025-11-17 17:06:15');
/*!40000 ALTER TABLE `ai_chat_history` ENABLE KEYS */;
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
