-- 清空数据（开发用）
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE paper_clicks;
TRUNCATE TABLE paper_keywords;
TRUNCATE TABLE keywords;
TRUNCATE TABLE papers;
TRUNCATE TABLE categories;
TRUNCATE TABLE users;
TRUNCATE TABLE colleges;
SET FOREIGN_KEY_CHECKS = 1;

-- 插入学院
INSERT INTO colleges (college_name, code) VALUES
('计算机科学与技术学院', 'CS'),
('电子工程学院', 'EE'),
('数学学院', 'MATH');

-- 插入分类
INSERT INTO categories (code, name) VALUES
('cs.CV', '计算机视觉'),
('cs.LG', '机器学习'),
('cs.CL', '计算语言学'),
('math.OC', '优化控制');

-- 插入用户
-- 密码统一设为 "123456" 的明文（实际应哈希！）
INSERT INTO users (username, password_hash, real_name, role, college_id) VALUES
-- 学校管理员
('admin_uni', '123456', '张校长', 'university_admin', 1),

-- 学院管理员
('admin_cs', '123456', '李院长', 'college_admin', 1),
('admin_ee', '123456', '王院长', 'college_admin', 2),

-- 学生（CS 学院）
('zhangsan', '123456', '张三', 'student', 1),
('lisi', '123456', '李四', 'student', 1),
('wangwu', '123456', '王五', 'student', 1),

-- 学生（EE 学院）
('zhaoliu', '123456', '赵六', 'student', 2);

-- 插入论文
INSERT INTO papers (title, arxiv_id, category_id, pdf_url, abstract) VALUES
('Vision Transformers for Image Recognition', '2010.11929', 1, 'https://arxiv.org/pdf/2010.11929.pdf', 'We explore the use of Vision Transformers...'),
('Attention Is All You Need', '1706.03762', 3, 'https://arxiv.org/pdf/1706.03762.pdf', 'The dominant sequence transduction models...'),
('Deep Residual Learning for Image Recognition', '1512.03385', 1, 'https://arxiv.org/pdf/1512.03385.pdf', 'Deeper neural networks are more difficult to train...'),
('Federated Learning: Challenges and Opportunities', '1902.04885', 2, 'https://arxiv.org/pdf/1902.04885.pdf', 'Federated learning enables training on decentralized data...');

-- 插入关键词（注意去重）
INSERT IGNORE INTO keywords (word) VALUES
('transformer'), ('vision'), ('attention'), ('resnet'), ('federated'), ('learning'), ('image'), ('recognition');

-- 更新关键词 ID 映射（手动对应，实际代码中自动处理）
-- 假设插入后 keyword_id 如下：
-- transformer: 1, vision: 2, attention: 3, resnet: 4, federated: 5, learning: 6, image: 7, recognition: 8

-- 建立论文-关键词关联
INSERT INTO paper_keywords (paper_id, keyword_id) VALUES
-- Paper 1: Vision Transformers
(1, 1), (1, 2), (1, 6), (1, 7),
-- Paper 2: Attention Is All You Need
(2, 1), (2, 3), (2, 6),
-- Paper 3: ResNet
(3, 4), (3, 6), (3, 7), (3, 8),
-- Paper 4: Federated Learning
(4, 5), (4, 6);

-- 更新关键词总频次（模拟入库时累加）
UPDATE keywords SET total_count = (
    SELECT COUNT(*) FROM paper_keywords pk WHERE pk.keyword_id = keywords.keyword_id
);

-- 模拟用户点击行为（过去7天内）
INSERT INTO paper_clicks (user_id, paper_id, college_id, click_time) VALUES
-- CS 学院学生点击
(4, 1, 1, NOW() - INTERVAL 1 DAY),  -- 张三点 ViT
(4, 2, 1, NOW() - INTERVAL 2 DAY),  -- 张三点 Transformer
(5, 1, 1, NOW() - INTERVAL 1 HOUR), -- 李四点 ViT
(6, 3, 1, NOW() - INTERVAL 3 DAY),  -- 王五点 ResNet

-- EE 学院学生点击
(7, 4, 2, NOW() - INTERVAL 5 HOUR), -- 赵六点 Federated Learning
(7, 2, 2, NOW() - INTERVAL 1 DAY);  -- 赵六也点 Transformer