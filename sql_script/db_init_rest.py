# init_demo_data.py
import mysql.connector
import random
from datetime import datetime, timedelta

# === 配置 ===
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '4252210zxc',  # 改成你的密码
    'database': 'paper_sys'
}

COLLEGES = [
    ('计算机科学与技术学院', 'CS'),
    ('电子工程学院', 'EE'),
    ('数学学院', 'MATH'),
    ('信息与通信工程学院', 'ICE'),
    ('自动化学院', 'AUTO'),
    ('软件学院', 'SE'),
    ('人工智能学院', 'AI'),
    ('网络空间安全学院', 'CYBER'),
    ('数据科学与大数据技术学院', 'DS'),
    ('光电工程学院', 'OE')
]

STUDENT_NAMES = [
    "张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
    "郑一", "冯二", "陈三", "褚四", "卫五", "蒋六", "沈七", "韩八",
    "杨九", "朱十", "秦一", "尤二", "许三", "何四", "吕五", "施六",
    "孔八", "曹九", "严十", "华一", "金二", "魏三", "陶四", "姜五"
]  # 可扩展

PASSWORD_HASH = "123456"  # 明文，仅演示用！

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def main():
    conn = get_connection()
    cur = conn.cursor()

    try:
        print("🔧 开始初始化演示数据...")

        # 1. 清空相关表（谨慎！）
        print("🧹 清空旧数据...")
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        cur.execute("TRUNCATE TABLE paper_clicks")
        cur.execute("TRUNCATE TABLE users")
        cur.execute("TRUNCATE TABLE colleges")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")

        # 2. 插入学院
        print("🏫 插入 10 个学院...")
        college_ids = {}
        for name, code in COLLEGES:
            cur.execute(
                "INSERT INTO colleges (college_name, code) VALUES (%s, %s)",
                (name, code)
            )
            college_ids[code] = cur.lastrowid
        conn.commit()

        # 3. 插入用户
        print("👥 插入用户（1 校级 + 10 院级 + 200 学生）...")
        user_id_map = {}

        # 校级管理员
        cur.execute("""
            INSERT INTO users (username, password_hash, real_name, role, college_id)
            VALUES (%s, %s, %s, %s, %s)
        """, ('admin_uni', PASSWORD_HASH, '张校长', 'UNIVERSITY_ADMIN', list(college_ids.values())[0]))
        user_id_map['admin_uni'] = cur.lastrowid

        # 院级管理员
        admin_users = []
        for i, (name, code) in enumerate(COLLEGES):
            username = f'admin_{code.lower()}'
            real_name = f'{["李", "王", "刘", "陈", "杨", "赵", "周", "吴", "郑", "孙"][i]}院长'
            cur.execute("""
                INSERT INTO users (username, password_hash, real_name, role, college_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, PASSWORD_HASH, real_name, 'COLLEGE_ADMIN', college_ids[code]))
            admin_users.append(cur.lastrowid)

        # 学生：每学院 20 人
        student_users = []
        for code, cid in college_ids.items():
            for j in range(20):
                idx = (len(student_users) + j) % len(STUDENT_NAMES)
                real_name = STUDENT_NAMES[idx] + f"({code}{j+1:02d})"
                username = f"stu_{code.lower()}_{j+1:02d}"
                cur.execute("""
                    INSERT INTO users (username, password_hash, real_name, role, college_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, PASSWORD_HASH, real_name, 'STUDENT', cid))
                student_users.append(cur.lastrowid)
        conn.commit()

        # 4. 获取所有论文（只取 paper_id 和 category_id）
        print("📚 读取现有论文...")
        cur.execute("SELECT paper_id, category_id FROM papers")
        papers = cur.fetchall()
        if not papers:
            raise Exception("papers 表为空！请先导入论文数据。")
        print(f"✅ 共加载 {len(papers)} 篇论文")

        # 5. 生成点击记录（≥1000 条）
        print("🖱️ 生成点击记录...")
        click_records = []
        total_clicks = 1200  # 可调整

        for _ in range(total_clicks):
            # 随机选一个学生
            user_id = random.choice(student_users)
            # 随机选一篇论文
            paper_id, category_id = random.choice(papers)
            # 推断学院：简单按 category 分配（实际可更复杂）
            # 这里我们直接用用户所属学院（需查 user 表，但为简化，假设 student_users 顺序对应）
            # 更准确做法：查 user_id 对应的 college_id
            cur.execute("SELECT college_id FROM users WHERE user_id = %s", (user_id,))
            college_id = cur.fetchone()[0]
            # 随机时间：最近 30 天内
            delta = timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            click_time = datetime.now() - delta
            click_records.append((user_id, paper_id, college_id, click_time))

        # 批量插入
        cur.executemany("""
            INSERT INTO paper_clicks (user_id, paper_id, college_id, click_time)
            VALUES (%s, %s, %s, %s)
        """, click_records)
        conn.commit()
        print(f"✅ 成功插入 {len(click_records)} 条点击记录")

        # 6. （可选）更新关键词频次
        print("🔄 更新关键词总频次...")
        cur.execute("""
            UPDATE keywords k
            SET total_count = (
                SELECT COUNT(*) FROM paper_keywords pk WHERE pk.keyword_id = k.keyword_id
            )
        """)
        conn.commit()

        print("\n🎉 演示数据初始化完成！")
        print(f"   - 学院: {len(COLLEGES)}")
        print(f"   - 用户: {1 + 10 + len(student_users)}")
        print(f"   - 点击: {len(click_records)}")

    except Exception as e:
        conn.rollback()
        print(f"❌ 初始化失败: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()