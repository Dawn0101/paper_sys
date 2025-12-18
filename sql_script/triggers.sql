-- =============================================
-- 文件: triggers.sql
-- 作用: 为 paper_keywords 表创建自动维护 keywords.total_count 的触发器
-- 要求: 
--   - keywords 表必须包含 total_count INT DEFAULT 0 字段
--   - paper_keywords 表已存在
-- =============================================

-- 更改语句结束符为 $$，避免与触发器内部的 ; 冲突
DELIMITER $$

-- -------------------------------------------------
-- 触发器: tr_paper_keywords_after_insert
-- 时机: 每当向 paper_keywords 表插入一条新记录后
-- 功能: 自动将对应关键词的 total_count 计数 +1
-- -------------------------------------------------
CREATE TRIGGER tr_paper_keywords_after_insert
AFTER INSERT ON paper_keywords
FOR EACH ROW
BEGIN
    -- NEW.keyword_id 是刚插入的那条记录中的 keyword_id
    UPDATE keywords 
    SET total_count = total_count + 1 
    WHERE keyword_id = NEW.keyword_id;
END$$

-- -------------------------------------------------
-- 触发器: tr_paper_keywords_after_delete
-- 时机: 每当从 paper_keywords 表删除一条记录后
-- 功能: 自动将对应关键词的 total_count 计数 -1
-- 应用场景:
--   - 手动删除 paper_keywords 记录
--   - 删除 papers 表中的论文（因外键 ON DELETE CASCADE 自动删除关联）
-- -------------------------------------------------
CREATE TRIGGER tr_paper_keywords_after_delete
AFTER DELETE ON paper_keywords
FOR EACH ROW
BEGIN
    -- OLD.keyword_id 是被删除的那条记录中的 keyword_id
    UPDATE keywords 
    SET total_count = total_count - 1 
    WHERE keyword_id = OLD.keyword_id;
END$$

-- 恢复默认语句结束符
DELIMITER ;