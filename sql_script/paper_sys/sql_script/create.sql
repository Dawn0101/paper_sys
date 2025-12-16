-- 创建数据库（可选）
CREATE DATABASE IF NOT EXISTS paper_sys;
USE paper_sys;

-- 1. 学院表
CREATE TABLE colleges (
    college_id INT PRIMARY KEY AUTO_INCREMENT,
    college_name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE
);

-- 2. 用户表（增加 updated_at）
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(100),
    role ENUM('student', 'college_admin', 'university_admin') NOT NULL,
    college_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (college_id) REFERENCES colleges(college_id)
);

-- 3. 分类表（arXiv 分类）
CREATE TABLE categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE,   -- 如 cs.CV
    name VARCHAR(100) NOT NULL
);

-- 4. 论文表（增加 updated_at）
CREATE TABLE papers (
    paper_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(500) NOT NULL,
    arxiv_id VARCHAR(50) NOT NULL UNIQUE,
    doi VARCHAR(100) UNIQUE,
    category_id INT NOT NULL,
    abstract TEXT,
    pdf_url VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- 5. 关键词表（用于词云）
CREATE TABLE keywords (
    keyword_id INT PRIMARY KEY AUTO_INCREMENT,
    word VARCHAR(100) NOT NULL UNIQUE,
    total_count INT DEFAULT 0
);

-- 6. 论文-关键词关联表（多对多）
CREATE TABLE paper_keywords (
    paper_id INT NOT NULL,
    keyword_id INT NOT NULL,
    PRIMARY KEY (paper_id, keyword_id),
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id) ON DELETE CASCADE,
    FOREIGN KEY (keyword_id) REFERENCES keywords(keyword_id) ON DELETE CASCADE
);

-- 7. 点击行为表（核心！替代 log 文件）
CREATE TABLE paper_clicks (
    click_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    paper_id INT NOT NULL,
    college_id INT NOT NULL,
    click_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_time (user_id, click_time),
    INDEX idx_college_time (college_id, click_time),
    INDEX idx_paper_time (paper_id, click_time),
    INDEX idx_click_time (click_time),
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id) ON DELETE CASCADE,
    FOREIGN KEY (college_id) REFERENCES colleges(college_id)
);

-- 8. 新增：用户事项表（用于 Settings 日程功能）
CREATE TABLE user_tasks (
    task_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    scheduled_date DATE NOT NULL,                -- 日历显示用
    title VARCHAR(200) NOT NULL,                 -- 事项内容
    priority ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    status ENUM('pending', 'completed') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_scheduled (user_id, scheduled_date),
    INDEX idx_scheduled_status (scheduled_date, status)
);