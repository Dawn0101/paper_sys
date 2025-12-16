import json
import re
import mysql.connector
import sys
from collections import Counter


# ======================
# 配置 & 工具函数
# ======================

ARXIV_CATEGORY_NAMES = {
    # 原有 32 项（保留并确认正确性）
    'cs.AI': 'Artificial Intelligence',
    'cs.AR': 'Hardware Architecture',
    'cs.CE': 'Computational Engineering, Finance, and Science',
    'cs.CG': 'Computational Geometry',
    'cs.CL': 'Computation and Language',
    'cs.CR': 'Cryptography and Security',
    'cs.CV': 'Computer Vision',
    'cs.CY': 'Computers and Society',
    'cs.DB': 'Databases',
    'cs.DC': 'Distributed, Parallel, and Cluster Computing',
    'cs.DL': 'Digital Libraries',
    'cs.DS': 'Data Structures and Algorithms',
    'cs.GR': 'Graphics',
    'cs.GT': 'Computer Science and Game Theory',
    'cs.HC': 'Human-Computer Interaction',
    'cs.IR': 'Information Retrieval',
    'cs.IT': 'Information Theory',
    'cs.LG': 'Machine Learning',
    'cs.LO': 'Logic in Computer Science',
    'cs.MA': 'Multiagent Systems',
    'cs.MS': 'Mathematical Software',
    'cs.NE': 'Neural and Evolutionary Computing',
    'cs.NI': 'Networking and Internet Architecture',
    'cs.OH': 'Other Computer Science',
    'cs.OS': 'Operating Systems',
    'cs.PF': 'Performance',
    'cs.PL': 'Programming Languages',
    'cs.RO': 'Robotics',
    'cs.SC': 'Symbolic Computation',
    'cs.SE': 'Software Engineering',
    'cs.SY': 'Systems and Control',  # 注意：你的 DB 里没有 cs.SY，但 JSON 可能有
    'cs.GEN': 'General Computer Science',

    # === 新增：根据 arXiv 官方分类补充缺失项 ===
    'cs.CC': 'Computational Complexity',
    'cs.DM': 'Discrete Mathematics',
    'cs.ET': 'Emerging Technologies',
    'cs.FL': 'Formal Languages and Automata Theory',
    'cs.GL': 'General Literature',
    'cs.MM': 'Multimedia',
    'cs.SD': 'Sound',
    'cs.SI': 'Social and Information Networks',
}

STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'could', 'should', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
    'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'also', 'can', 'may', 'as',
    'from', 'into', 'up', 'out', 'over', 'under', 'such', 'than', 'then', 'there', 'their',
    'which', 'what', 'how', 'when', 'where', 'why', 'all', 'any', 'some', 'no', 'not', 'only'
}


def tokenize(text):
    """提取长度≥3的英文单词，转小写，过滤停用词"""
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return [w for w in words if w not in STOP_WORDS]


def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='4252210zxc',
        database='paper_sys',
        autocommit=False
    )


def get_or_create_category_id(cur, code):
    cur.execute("SELECT category_id FROM categories WHERE code = %s", (code,))
    row = cur.fetchone()
    if row:
        return row[0]
    name = ARXIV_CATEGORY_NAMES.get(code, f"Unknown Category: {code}")
    cur.execute("INSERT INTO categories (code, name) VALUES (%s, %s)", (code, name))
    return cur.lastrowid


def extract_top_keywords(abstract, top_n=5):
    """基于单篇摘要的词频提取 top_n 关键词（去停用词后）"""
    tokens = tokenize(abstract)
    if not tokens:
        return []
    freq = Counter(tokens)
    # 返回频率最高的 top_n 个词（按频率降序，同频按字母升序）
    most_common = freq.most_common(top_n)
    return [word for word, _ in most_common]


# ======================
# 主函数
# ======================

def process_json(json_path):
    skipped_duplicate = 0
    print("正在加载 JSON 数据...")
    with open(json_path, 'r', encoding='utf-8') as f:
        records = json.load(f)
    print(f"✅ 成功加载 {len(records)} 条论文记录")

    conn = get_connection()
    cur = conn.cursor()

    success = 0
    for i, rec in enumerate(records, 1):
        try:
            title = rec.get('title', '').strip()
            arxiv_id = rec.get('arxiv_id', '').strip()
            doi = rec.get('doi', '').strip() or None
            pdf_url = rec.get('link', '').strip()
            abstract = rec.get('summary', rec.get('abstract', '')).strip()
            category_code = rec.get('category', 'cs.GEN').strip() or 'cs.GEN'

            if not (title and arxiv_id and pdf_url):
                print(f"⚠ 跳过 {i}: 缺少必要字段")
                continue
            
            # >>>>>>>>>> 关键：查重 <<<<<<<<<<
            cur.execute("SELECT paper_id FROM papers WHERE arxiv_id = %s", (arxiv_id,))
            if cur.fetchone():
                skipped_duplicate += 1
                continue   # 跳过，不插入

            # 获取或创建分类
            category_id = get_or_create_category_id(cur, category_code)

            # 插入论文
            cur.execute("""
                INSERT INTO papers (title, arxiv_id, doi, category_id, abstract, pdf_url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (title, arxiv_id, doi, category_id, abstract, pdf_url))
            conn.commit()
            paper_id = cur.lastrowid

            # 提取关键词（仅基于本篇摘要）
            keywords = extract_top_keywords(abstract, top_n=5) if abstract else []

            for word in keywords:
                # 获取或创建 keyword
                cur.execute("SELECT keyword_id FROM keywords WHERE word = %s", (word,))
                row = cur.fetchone()
                if row:
                    kw_id = row[0]
                else:
                    cur.execute("INSERT INTO keywords (word) VALUES (%s)", (word,))
                    kw_id = cur.lastrowid
                    conn.commit()

                # 关联（防重复）
                cur.execute("""
                    INSERT IGNORE INTO paper_keywords (paper_id, keyword_id)
                    VALUES (%s, %s)
                """, (paper_id, kw_id))

            conn.commit()
            # print(f"✅ [{i}/{len(records)}] '{title[:50]}...' | 分类: {category_code} | 关键词: {len(keywords)}")
            success += 1

        except Exception as e:
            # print(f"❌ 记录 {i} 失败 | category='{category_code}' | arxiv_id='{arxiv_id}' | 错误: {e}")
            conn.rollback()

    print(f"\n🎉 导入完成！成功: {success}/{len(records)}")
    cur.close()
    conn.close()


# ======================s
# 入口
# ======================

if __name__ == '__main__':
    json_file = 'papers.json'  # 固定使用当前目录下的 papers.json
    try:
        process_json(json_file)
    except FileNotFoundError:
        print(f"❌ 错误: 找不到文件 '{json_file}'，请确保它在当前目录下。")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        sys.exit(1)