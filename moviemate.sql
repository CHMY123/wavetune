-- MySQL dump 10.13  Distrib 8.0.39, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: wavetune
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '用户ID',
  `feedback_type` varchar(20) NOT NULL COMMENT '反馈类型',
  `content` text NOT NULL COMMENT '反馈内容',
  `score` int NOT NULL COMMENT '满意度评分',
  `status` varchar(20) DEFAULT 'pending' COMMENT '处理状态',
  `admin_reply` text COMMENT '管理员回复',
  `submit_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
  `reply_time` datetime DEFAULT NULL COMMENT '回复时间',
  PRIMARY KEY (`id`),
  KEY `idx_feedback_user_id` (`user_id`),
  KEY `idx_feedback_type` (`feedback_type`),
  KEY `idx_feedback_submit_time` (`submit_time`),
  CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feedback`
--

LOCK TABLES `feedback` WRITE;
/*!40000 ALTER TABLE `feedback` DISABLE KEYS */;
INSERT INTO `feedback` VALUES (2,4,'accuracy','很不错，下次还会用的！',5,'pending',NULL,'2025-11-17 15:48:28',NULL),(3,4,'music','很好听，下次还会继续听的',5,'pending',NULL,'2025-12-04 09:52:21',NULL);
/*!40000 ALTER TABLE `feedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `music`
--

DROP TABLE IF EXISTS `music`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `music` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL COMMENT '音乐标题',
  `artist` varchar(100) DEFAULT NULL COMMENT '艺术家/创作者',
  `duration` varchar(10) DEFAULT NULL COMMENT '时长',
  `cover` varchar(255) DEFAULT NULL COMMENT '封面图URL',
  `audio_url` varchar(255) DEFAULT NULL COMMENT '音频文件URL',
  `reason` text COMMENT '推荐理由',
  `music_type` varchar(20) DEFAULT NULL COMMENT '音乐类型',
  `fatigue_level` varchar(50) DEFAULT NULL COMMENT '适配疲劳等级',
  `match_rate` int DEFAULT '0' COMMENT '匹配度',
  `play_count` int DEFAULT '0' COMMENT '播放次数',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否启用',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_music_type` (`music_type`),
  KEY `idx_music_fatigue_level` (`fatigue_level`),
  KEY `idx_music_match_rate` (`match_rate`),
  KEY `idx_music_is_active` (`is_active`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `music`
--

LOCK TABLES `music` WRITE;
/*!40000 ALTER TABLE `music` DISABLE KEYS */;
INSERT INTO `music` VALUES (1,'小小阿布   悲伤剧情— 伴奏','小小阿布','02:46','http://localhost:8000/static/music_cover/微信图片_20240527153857_2.jpg','http://localhost:8000/static/music/小小阿布 - 悲伤剧情—-伴奏_2.mp3','因为我喜欢。','natural','medium',50,0,1,'2025-11-18 20:39:46','2025-11-18 21:36:30'),(21,'B站伊丽莎白鼠   如何用100秒让张杰感受UP主的爱','伊丽萨黑白','01:46','http://localhost:8000/static/music_cover/微信图片_20240922234533.jpg','http://localhost:8000/static/music/B站伊丽莎白鼠 - 如何用100秒让张杰感受UP主的爱.mp3','很不错','natural','medium',50,0,1,'2025-11-19 16:18:28','2025-11-19 16:18:28'),(22,'小小阿布   悲伤剧情— 伴奏','小小阿布','02:46','http://localhost:8000/static/music_cover/微信图片_20240527153857.jpg','http://localhost:8000/static/music/小小阿布 - 悲伤剧情—-伴奏.mp3','很不错','natural','heavy',50,0,1,'2025-11-19 18:09:55','2025-11-19 18:09:55');
/*!40000 ALTER TABLE `music` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `update_music_time` BEFORE UPDATE ON `music` FOR EACH ROW BEGIN
    SET NEW.`update_time` = CURRENT_TIMESTAMP;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Temporary view structure for view `music_stats_view`
--

DROP TABLE IF EXISTS `music_stats_view`;
/*!50001 DROP VIEW IF EXISTS `music_stats_view`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `music_stats_view` AS SELECT 
 1 AS `id`,
 1 AS `title`,
 1 AS `artist`,
 1 AS `music_type`,
 1 AS `fatigue_level`,
 1 AS `match_rate`,
 1 AS `play_count`,
 1 AS `is_active`,
 1 AS `scene_usage_count`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `operation_log`
--

DROP TABLE IF EXISTS `operation_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `operation_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL COMMENT '用户ID',
  `operation_type` varchar(50) NOT NULL COMMENT '操作类型',
  `operation_desc` varchar(255) DEFAULT NULL COMMENT '操作描述',
  `request_method` varchar(10) DEFAULT NULL COMMENT '请求方法',
  `request_url` varchar(255) DEFAULT NULL COMMENT '请求URL',
  `request_params` text COMMENT '请求参数',
  `response_status` int DEFAULT NULL COMMENT '响应状态码',
  `ip_address` varchar(45) DEFAULT NULL COMMENT 'IP地址',
  `user_agent` text COMMENT '用户代理',
  `execution_time` int DEFAULT NULL COMMENT '执行时间(ms)',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_log_user_id` (`user_id`),
  KEY `idx_log_operation_type` (`operation_type`),
  KEY `idx_log_create_time` (`create_time`),
  CONSTRAINT `operation_log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=191 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `operation_log`
--

LOCK TABLES `operation_log` WRITE;
/*!40000 ALTER TABLE `operation_log` DISABLE KEYS */;
INSERT INTO `operation_log` VALUES (1,4,'user_register','用户注册成功','POST','http://localhost:8000/api/auth/register',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-29 12:39:00'),(2,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-29 12:39:05'),(3,1,'user_login','登录失败-密码错误','POST','http://localhost:8000/api/auth/login',NULL,401,'127.0.0.1','Mozilla/5.0 (Windows NT; Windows NT 10.0; zh-CN) WindowsPowerShell/5.1.26100.6899',NULL,'2025-10-29 12:59:59'),(4,1,'user_login','登录失败-密码错误','POST','http://localhost:8000/api/auth/login',NULL,401,'127.0.0.1','Mozilla/5.0 (Windows NT; Windows NT 10.0; zh-CN) WindowsPowerShell/5.1.26100.6899',NULL,'2025-10-29 13:04:12'),(5,1,'user_login','登录失败-密码错误','POST','http://localhost:8000/api/auth/login',NULL,401,'127.0.0.1','Mozilla/5.0 (Windows NT; Windows NT 10.0; zh-CN) WindowsPowerShell/5.1.26100.6899',NULL,'2025-10-29 13:17:13'),(6,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-29 13:33:50'),(7,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-29 13:33:56'),(8,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-29 16:45:47'),(9,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-29 22:19:21'),(10,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-29 22:19:28'),(11,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-29 22:31:24'),(12,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-29 22:34:05'),(13,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-29 23:04:22'),(14,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-29 23:04:22'),(15,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-30 17:52:45'),(16,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-30 17:52:46'),(17,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-30 17:52:53'),(18,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-30 17:52:53'),(19,4,'update_preference','更新偏好设置-default_fatigue_level','PUT','http://localhost:8000/api/auth/preference?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-30 17:52:58'),(20,4,'update_preference','更新偏好设置-default_fatigue_level','PUT','http://localhost:8000/api/auth/preference?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-30 17:53:00'),(21,4,'user_logout','用户登出','POST','http://localhost:8000/api/auth/logout',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-30 17:54:00'),(22,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-30 17:54:19'),(23,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-31 18:04:20'),(24,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-31 18:04:20'),(25,4,'user_logout','用户登出','POST','http://localhost:8000/api/auth/logout',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-31 18:05:08'),(26,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-31 18:05:10'),(27,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-31 18:20:58'),(28,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-31 18:20:59'),(29,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-31 18:25:31'),(30,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-31 18:25:31'),(31,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-31 19:04:18'),(32,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',NULL,'2025-10-31 19:04:18'),(33,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-04 22:58:54'),(34,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-04 22:58:54'),(35,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:39:27'),(36,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:39:27'),(37,4,'update_profile','更新用户资料成功','PUT','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:39:35'),(38,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:39:36'),(39,4,'change_password','修改密码成功','POST','http://localhost:8000/api/auth/change-password?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:40:52'),(40,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:41:15'),(41,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:41:15'),(42,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:41:39'),(43,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:41:39'),(44,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:42:12'),(45,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:42:13'),(46,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:55:36'),(47,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:55:36'),(48,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:55:54'),(49,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:55:54'),(50,4,'user_logout','用户登出','POST','http://localhost:8000/api/auth/logout',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:57:14'),(51,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 22:57:23'),(52,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 23:45:39'),(53,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 23:45:39'),(54,4,'user_logout','用户登出','POST','http://localhost:8000/api/auth/logout',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 23:46:03'),(55,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 23:46:06'),(56,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 23:46:11'),(57,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-16 23:46:11'),(58,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 00:04:06'),(59,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 00:04:06'),(60,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 08:41:45'),(61,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 08:41:45'),(62,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 08:52:38'),(63,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 08:52:38'),(64,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 08:54:23'),(65,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 08:54:23'),(66,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 08:54:54'),(67,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 08:54:54'),(68,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 08:55:33'),(69,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 08:55:33'),(70,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 08:58:23'),(71,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 08:58:23'),(72,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 09:01:26'),(73,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 09:01:26'),(74,4,'user_logout','用户登出','POST','http://localhost:8000/api/auth/logout',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 09:03:07'),(75,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 09:03:10'),(76,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 09:35:18'),(77,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 09:35:19'),(78,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 14:13:32'),(79,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-17 14:13:32'),(80,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-18 17:54:46'),(81,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-18 17:54:46'),(82,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-18 18:05:48'),(83,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-18 18:05:48'),(84,4,'user_logout','用户登出','POST','http://localhost:8000/api/auth/logout',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-18 18:05:54'),(85,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-18 18:06:08'),(86,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-18 23:15:52'),(87,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-18 23:15:52'),(88,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-18 23:16:42'),(89,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-18 23:16:43'),(90,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-18 23:17:09'),(91,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-18 23:17:10'),(92,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-19 14:28:57'),(93,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-19 14:28:57'),(94,4,'user_logout','用户登出','POST','http://localhost:8000/api/auth/logout',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-19 14:28:57'),(95,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-19 14:28:57'),(96,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-19 19:49:15'),(97,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-19 19:49:15'),(98,4,'user_logout','用户登出','POST','http://localhost:8000/api/auth/logout',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:15:20'),(99,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:15:30'),(100,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:15:34'),(101,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:15:48'),(102,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:15:56'),(103,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:23:34'),(104,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:28:03'),(105,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:32:05'),(106,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:32:09'),(107,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:32:11'),(108,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:32:15'),(109,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:32:23'),(110,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:32:33'),(111,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:36:23'),(112,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:36:30'),(113,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:39:00'),(114,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:39:09'),(115,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:41:04'),(116,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:41:57'),(117,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:44:50'),(118,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:45:12'),(119,NULL,'user_login','登录失败-用户不存在','POST','http://localhost:8000/api/auth/login',NULL,404,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:45:32'),(120,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-21 16:48:48'),(121,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',NULL,'2025-11-25 01:22:58'),(122,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 01:26:45'),(123,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 01:26:45'),(124,4,'update_preference','更新偏好设置-default_fatigue_level','PUT','http://localhost:8000/api/auth/preference?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 01:27:03'),(125,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 01:41:24'),(126,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 01:41:24'),(127,4,'update_preference','更新偏好设置-default_fatigue_level','PUT','http://localhost:8000/api/auth/preference?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 01:41:28'),(128,4,'user_logout','用户登出','POST','http://localhost:8000/api/auth/logout',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 01:50:10'),(129,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 01:56:23'),(130,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 01:56:50'),(131,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 01:56:51'),(132,4,'user_logout','用户登出','POST','http://localhost:8000/api/auth/logout',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 01:56:56'),(133,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 02:08:40'),(134,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 02:14:24'),(135,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 02:14:24'),(136,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',NULL,'2025-11-25 02:49:43'),(137,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',NULL,'2025-11-25 02:49:44'),(138,4,'user_logout','用户登出','POST','http://localhost:8000/api/auth/logout',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 13:59:57'),(139,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 14:00:55'),(140,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 14:04:21'),(141,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 14:04:22'),(142,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) TraeCN/1.104.3 Chrome/138.0.7204.251 Electron/37.6.1 Safari/537.36',NULL,'2025-11-25 14:29:17'),(143,4,'user_logout','用户登出','POST','http://localhost:8000/api/auth/logout',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 14:42:47'),(144,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-11-25 14:42:57'),(145,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-03 16:25:22'),(146,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-03 16:45:43'),(147,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-03 16:45:43'),(148,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:32:53'),(149,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:32:53'),(150,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:39:30'),(151,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:39:30'),(152,4,'revoke_session','撤销会话-10','DELETE','http://localhost:8000/api/auth/session/10?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:39:49'),(153,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:39:49'),(154,4,'revoke_session','撤销会话-14','DELETE','http://localhost:8000/api/auth/session/14?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:39:51'),(155,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:39:52'),(156,4,'revoke_session','撤销会话-15','DELETE','http://localhost:8000/api/auth/session/15?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:39:55'),(157,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:39:56'),(158,4,'user_logout','用户登出','POST','http://localhost:8000/api/auth/logout',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:40:00'),(159,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:40:02'),(160,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:40:05'),(161,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:40:06'),(162,4,'user_login','用户登录成功','POST','http://localhost:8000/api/auth/login',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:42:02'),(163,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:42:05'),(164,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:42:06'),(165,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:50:50'),(166,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:50:50'),(167,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:51:26'),(168,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:51:26'),(169,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:52:28'),(170,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:52:28'),(171,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:56:44'),(172,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 09:56:44'),(173,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 10:45:14'),(174,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 10:45:14'),(175,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 10:52:28'),(176,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 10:52:28'),(177,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 10:53:41'),(178,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-04 10:53:41'),(179,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-05 10:03:45'),(180,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-05 10:03:45'),(181,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-05 10:09:53'),(182,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-05 10:09:53'),(183,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-05 10:10:11'),(184,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-05 10:10:12'),(185,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-05 10:12:34'),(186,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',NULL,'2025-12-05 10:12:34'),(187,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0',NULL,'2025-12-08 00:21:00'),(188,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0',NULL,'2025-12-08 00:21:00'),(189,4,'get_profile','获取用户资料','GET','http://localhost:8000/api/auth/profile?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0',NULL,'2025-12-08 00:43:07'),(190,4,'get_sessions','获取用户会话列表','GET','http://localhost:8000/api/auth/sessions?user_id=4',NULL,200,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0',NULL,'2025-12-08 00:43:07');
/*!40000 ALTER TABLE `operation_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scene`
--

DROP TABLE IF EXISTS `scene`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `scene` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '用户ID',
  `scene_name` varchar(50) NOT NULL COMMENT '场景名称',
  `music_type` varchar(20) NOT NULL COMMENT '音乐类型',
  `description` text COMMENT '场景描述',
  `is_default` tinyint(1) DEFAULT '0' COMMENT '是否默认场景',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否启用',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`scene_name`),
  KEY `idx_scene_user_id` (`user_id`),
  KEY `idx_scene_name` (`scene_name`),
  KEY `idx_scene_is_default` (`is_default`),
  CONSTRAINT `scene_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scene`
--

LOCK TABLES `scene` WRITE;
/*!40000 ALTER TABLE `scene` DISABLE KEYS */;
INSERT INTO `scene` VALUES (1,1,'学习场景','piano','适合学习和工作的场景，使用钢琴音乐提升专注力',1,1,'2025-10-23 11:21:36','2025-10-23 11:21:36'),(2,1,'办公场景','whitenoise','适合办公环境的场景，使用白噪音减少干扰',1,1,'2025-10-23 11:21:36','2025-10-23 11:21:36'),(3,1,'休息场景','natural','适合休息放松的场景，使用自然音效缓解疲劳',1,1,'2025-10-23 11:21:36','2025-10-23 11:21:36');
/*!40000 ALTER TABLE `scene` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `update_scene_time` BEFORE UPDATE ON `scene` FOR EACH ROW BEGIN
    SET NEW.`update_time` = CURRENT_TIMESTAMP;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `system_stats`
--

DROP TABLE IF EXISTS `system_stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_stats` (
  `id` int NOT NULL AUTO_INCREMENT,
  `stat_name` varchar(50) NOT NULL COMMENT '统计名称',
  `stat_value` varchar(20) NOT NULL COMMENT '统计值',
  `stat_unit` varchar(10) DEFAULT NULL COMMENT '单位',
  `description` varchar(255) DEFAULT NULL COMMENT '描述',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `stat_name` (`stat_name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_stats`
--

LOCK TABLES `system_stats` WRITE;
/*!40000 ALTER TABLE `system_stats` DISABLE KEYS */;
INSERT INTO `system_stats` VALUES (1,'detection_count','1,234','次','系统总检测次数','2025-10-23 11:21:36'),(2,'intervention_count','856','次','系统总干预次数','2025-10-23 11:21:36'),(3,'device_count','12','台','参与联邦学习的设备数量','2025-10-23 11:21:36'),(4,'model_accuracy','89.2','%','模型准确率','2025-10-23 11:21:36'),(5,'active_users','156','人','活跃用户数量','2025-10-23 11:21:36'),(6,'music_tracks','10','首','音乐库曲目数量','2025-10-23 11:21:36');
/*!40000 ALTER TABLE `system_stats` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `update_stats_time` BEFORE UPDATE ON `system_stats` FOR EACH ROW BEGIN
    SET NEW.`update_time` = CURRENT_TIMESTAMP;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `student_id` varchar(20) NOT NULL COMMENT '学号',
  `password_hash` varchar(255) DEFAULT NULL COMMENT '密码哈希',
  `email` varchar(100) DEFAULT NULL COMMENT '邮箱',
  `phone` varchar(20) DEFAULT NULL COMMENT '手机号',
  `avatar` varchar(255) DEFAULT '' COMMENT '头像路径',
  `detection_count` int DEFAULT '0' COMMENT '检测次数',
  `intervention_count` int DEFAULT '0' COMMENT '干预次数',
  `last_login_time` datetime DEFAULT NULL COMMENT '最后登录时间',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否激活（MySQL 用 TINYINT(1) 替代 BOOLEAN）',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_user_username` (`username`),
  KEY `idx_user_create_time` (`create_time`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'李同学','2022001001',NULL,'li.student@example.com','13800138001','/static/avatar/default.jpg',12,8,NULL,1,'2025-10-23 11:21:36','2025-10-23 11:21:36'),(2,'张同学','2022001002',NULL,'zhang.student@example.com','13800138002','/static/avatar/default.jpg',8,5,NULL,1,'2025-10-23 11:21:36','2025-10-23 11:21:36'),(3,'王同学','2022001003',NULL,'wang.student@example.com','13800138003','/static/avatar/default.jpg',15,12,NULL,1,'2025-10-23 11:21:36','2025-10-23 11:21:36'),(4,'chmy','20232005118','0f9e2d74c6e6713a44f330983f629565:f60885c809a638d0e58aee44ca7528bf5acbf3342a340a9163e9ec0b0fcc9f56','924157960@qq.com','13724130633','/static/avatar/4_3f847ae4-e05b-4847-9dca-fcb8917ebec0.jpg',0,0,'2025-12-04 09:42:03',1,'2025-10-29 12:39:00','2025-12-04 09:42:02');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `update_user_time` BEFORE UPDATE ON `user` FOR EACH ROW BEGIN
    SET NEW.`update_time` = CURRENT_TIMESTAMP;  -- 直接更新新记录的 update_time
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `user_preference`
--

DROP TABLE IF EXISTS `user_preference`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_preference` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '用户ID',
  `preference_key` varchar(50) NOT NULL COMMENT '偏好键',
  `preference_value` text COMMENT '偏好值',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`preference_key`),
  KEY `idx_preference_user_id` (`user_id`),
  CONSTRAINT `user_preference_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_preference`
--

LOCK TABLES `user_preference` WRITE;
/*!40000 ALTER TABLE `user_preference` DISABLE KEYS */;
INSERT INTO `user_preference` VALUES (1,1,'default_fatigue_level','medium','2025-10-23 11:21:36','2025-10-23 11:21:36'),(2,1,'preferred_music_type','natural','2025-10-23 11:21:36','2025-10-23 11:21:36'),(3,1,'notification_enabled','true','2025-10-23 11:21:36','2025-10-23 11:21:36'),(4,1,'auto_play','false','2025-10-23 11:21:36','2025-10-23 11:21:36'),(5,2,'default_fatigue_level','light','2025-10-23 11:21:36','2025-10-23 11:21:36'),(6,2,'preferred_music_type','piano','2025-10-23 11:21:36','2025-10-23 11:21:36'),(7,2,'notification_enabled','false','2025-10-23 11:21:36','2025-10-23 11:21:36'),(8,2,'auto_play','true','2025-10-23 11:21:36','2025-10-23 11:21:36'),(9,4,'default_fatigue_level','medium','2025-10-29 12:39:00','2025-11-25 01:41:28'),(10,4,'preferred_music_type','natural','2025-10-29 12:39:00','2025-10-29 12:39:00'),(11,4,'notification_enabled','true','2025-10-29 12:39:00','2025-10-29 12:39:00'),(12,4,'auto_play','false','2025-10-29 12:39:00','2025-10-29 12:39:00');
/*!40000 ALTER TABLE `user_preference` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `update_preference_time` BEFORE UPDATE ON `user_preference` FOR EACH ROW BEGIN
    SET NEW.`update_time` = CURRENT_TIMESTAMP;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `user_session`
--

DROP TABLE IF EXISTS `user_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_session` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '用户ID',
  `session_token` varchar(255) NOT NULL COMMENT '会话令牌',
  `device_info` varchar(255) DEFAULT NULL COMMENT '设备信息',
  `ip_address` varchar(45) DEFAULT NULL COMMENT 'IP地址',
  `user_agent` text COMMENT '用户代理',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否活跃',
  `expire_time` datetime NOT NULL COMMENT '过期时间',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_activity` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '最后活动时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_token` (`session_token`),
  KEY `idx_session_user_id` (`user_id`),
  KEY `idx_session_expire_time` (`expire_time`),
  KEY `idx_session_is_active` (`is_active`),
  CONSTRAINT `user_session_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_session`
--

LOCK TABLES `user_session` WRITE;
/*!40000 ALTER TABLE `user_session` DISABLE KEYS */;
INSERT INTO `user_session` VALUES (1,4,'mJ7-Oj3ckX-vOyxvvVbBPzGgy06WORHg_wI60zQi6N0','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',0,'2025-10-30 22:34:06','2025-10-29 22:34:05','2025-10-30 17:54:00'),(2,4,'SZ3fSQMSXTM1qkH_mwfUKoLbMOahT3tJ74x_BL0SW7g','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',0,'2025-10-31 17:54:19','2025-10-30 17:54:19','2025-10-31 18:05:08'),(3,4,'DX1XU0U8vDJFwdfxTiM3Qlj9JPwnVCdtEHxqk4WRkZU','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',0,'2025-11-01 18:05:11','2025-10-31 18:05:10','2025-11-16 22:57:14'),(4,4,'sPrsLicVLbS1Zi4XKIR64ra7Pv62gQIXaQ8vJdVpTAw','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',0,'2025-11-17 22:57:23','2025-11-16 22:57:23','2025-11-16 23:46:03'),(5,4,'02wgylYr1OSoEuW_UwG8Kyi0uWR-8NhZnJyp38022os','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',0,'2025-11-17 23:46:06','2025-11-16 23:46:06','2025-11-17 09:03:07'),(6,4,'fOWbGXQkT4OEzjg4I6-yhDLL9Sx-ooyaLJYUBZ2FlnI','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',0,'2025-11-18 09:03:11','2025-11-17 09:03:10','2025-11-18 18:05:54'),(7,4,'GSp9Z4RtvU5EiZfcjkRgf0Giaw29HVzk94ZWiA10UU8','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',0,'2025-11-19 18:06:08','2025-11-18 18:06:08','2025-11-19 14:28:57'),(8,4,'JRr7rp_GEr0hcakac_tjnnT8l2znU8FtYnAI71YASSE','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',0,'2025-11-20 14:28:57','2025-11-19 14:28:57','2025-11-21 16:15:20'),(9,4,'76M-X0gp4Xomz1XMisTf9jtFQ_nniTFtDIk05Uo86BY','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',0,'2025-11-22 16:48:48','2025-11-21 16:48:48','2025-11-25 01:50:10'),(10,4,'SawiNYqJzwKwzJOnFiK4Sl1ohrzIe9ed1HcKsUMtxZ0','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',0,'2025-11-26 01:22:58','2025-11-25 01:22:58','2025-12-04 09:39:49'),(11,4,'mH-9Wyj3g8jYRDCS35tRjj72SA_NxzBuyf1bo5WKoMg','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',0,'2025-11-26 01:56:23','2025-11-25 01:56:23','2025-11-25 01:56:56'),(12,4,'K4-FDxjpv7Fgsy79C-waTOoLJRiUbn-L--YJd895kdk','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',0,'2025-11-26 02:08:40','2025-11-25 02:08:40','2025-11-25 13:59:57'),(13,4,'5EADTsPjOC4xGlO541kR62uzrV_0YZdqSdy7lElYfKU','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',0,'2025-11-26 14:00:55','2025-11-25 14:00:55','2025-11-25 14:42:47'),(14,4,'OdNopuC2di04p2MDME3xGlxlePe12b7qpBBaP6bawQk','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) TraeCN/1.104.3 Chrome/138.0.7204.251 Electron/37.6.1 Safari/537.36','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) TraeCN/1.104.3 Chrome/138.0.7204.251 Electron/37.6.1 Safari/537.36',0,'2025-11-26 14:29:17','2025-11-25 14:29:17','2025-12-04 09:39:51'),(15,4,'pN4EjCiX4mMlq3iZly2u-NyPuWoOBU8TqoFmEuuVvKI','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',0,'2025-11-26 14:42:57','2025-11-25 14:42:57','2025-12-04 09:39:55'),(16,4,'pP-FZ0LjMW2CDAiBx2jEGeoLzxyW754sS7nqvKDXGfM','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',0,'2025-12-04 16:25:23','2025-12-03 16:25:22','2025-12-04 09:40:00'),(17,4,'zlES60Gksqao3VAMpt8pxFfjQ3lItgJRxdQ978oWqFY','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',1,'2025-12-05 09:42:03','2025-12-04 09:40:02','2025-12-04 09:42:03');
/*!40000 ALTER TABLE `user_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `user_stats_view`
--

DROP TABLE IF EXISTS `user_stats_view`;
/*!50001 DROP VIEW IF EXISTS `user_stats_view`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `user_stats_view` AS SELECT 
 1 AS `id`,
 1 AS `username`,
 1 AS `student_id`,
 1 AS `detection_count`,
 1 AS `intervention_count`,
 1 AS `feedback_count`,
 1 AS `scene_count`,
 1 AS `last_login_time`,
 1 AS `is_active`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `music_stats_view`
--

/*!50001 DROP VIEW IF EXISTS `music_stats_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `music_stats_view` AS select `m`.`id` AS `id`,`m`.`title` AS `title`,`m`.`artist` AS `artist`,`m`.`music_type` AS `music_type`,`m`.`fatigue_level` AS `fatigue_level`,`m`.`match_rate` AS `match_rate`,`m`.`play_count` AS `play_count`,`m`.`is_active` AS `is_active`,count(distinct `s`.`id`) AS `scene_usage_count` from (`music` `m` left join `scene` `s` on((`m`.`music_type` = `s`.`music_type`))) group by `m`.`id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `user_stats_view`
--

/*!50001 DROP VIEW IF EXISTS `user_stats_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `user_stats_view` AS select `u`.`id` AS `id`,`u`.`username` AS `username`,`u`.`student_id` AS `student_id`,`u`.`detection_count` AS `detection_count`,`u`.`intervention_count` AS `intervention_count`,count(distinct `f`.`id`) AS `feedback_count`,count(distinct `s`.`id`) AS `scene_count`,`u`.`last_login_time` AS `last_login_time`,`u`.`is_active` AS `is_active` from ((`user` `u` left join `feedback` `f` on((`u`.`id` = `f`.`user_id`))) left join `scene` `s` on((`u`.`id` = `s`.`user_id`))) group by `u`.`id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-18 19:59:27
