-- 联邦学习训练记录表
CREATE TABLE IF NOT EXISTS federated_training (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    client_id VARCHAR(50) NOT NULL,
    round_number INT NOT NULL,
    accuracy FLOAT DEFAULT 0,
    loss FLOAT DEFAULT 0,
    training_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'training', 'completed', 'failed') DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- 联邦学习设备表
CREATE TABLE IF NOT EXISTS federated_device (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    device_id VARCHAR(50) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    status ENUM('online', 'offline') DEFAULT 'offline',
    last_participate DATETIME DEFAULT NULL,
    training_count INT DEFAULT 0,
    contribution FLOAT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- 联邦学习统计表
CREATE TABLE IF NOT EXISTS federated_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    total_participants INT DEFAULT 0,
    total_devices INT DEFAULT 0,
    total_rounds INT DEFAULT 0,
    average_accuracy FLOAT DEFAULT 0,
    average_loss FLOAT DEFAULT 0,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 初始化联邦学习统计数据
INSERT INTO federated_stats (total_participants, total_devices, total_rounds, average_accuracy, average_loss)
VALUES (0, 0, 0, 0, 0)
ON DUPLICATE KEY UPDATE id = id;

-- 信号监测检测次数表
CREATE TABLE IF NOT EXISTS signal_detection_count (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    detection_count INT DEFAULT 0,
    last_detection DATETIME DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);
