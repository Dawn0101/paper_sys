# student/repositories.py
from .models import db, PaperClick, Paper, Category从。模型导入db， PaperClick, Paper, Category
from sqlalchemy import func


def get_student_click_history(user_id):
    """获取学生的论文浏览记录"""
    return PaperClick.query.filter_by(user_id=user_id).order_by(PaperClick.click_time.desc()).all()返回PaperClick.query   查询.filter_by (user_id = user_id) .order_by (PaperClick.click_time.desc())所有()


def delete_click_record(click_id, user_id):Def delete_click_record(click_id, user_id)：
    """删除学生的特定浏览记录"""
    click = PaperClick.query.filter_by(click_id=click_id, user_id=user_id).first()click = PaperClick.query   查询.filter_by(click_id=click_id, user_id=user_id).first（）
    if click:   如果点击:
        db.session.delete(click)   db.session   会话.delete   删除(点击)
        db.session.commit()
        return True   还真
    return False   返回假


def get_paper_category_stats():
    """获取论文分类统计数据（适配前端图表格式）"""
    result = db.session.query(Result = db.session   会话.query   查询(
        Category.name,
        func.count(Paper.paper_id).label('count')func.count   数 (Paper.paper_id) .label   标签(“计数”)
    ).join(Paper, Category.category_id == Paper.category_id)。join(Paper, Category.category_id   category_id添加 == Paper.category_id   category_id添加
           ).group_by(Category.category_id).all()) .group_by (Category.category_id   category_id添加) ()

    # ========== 核心修改：调整返回格式 ==========
    # 从 [{'category': 'xxx', 'count': xxx}] 改为 {categories: [], counts: []}
    categories = [item.name for item in result]  # 分类名称列表
    counts = [item.count for item in result]     # 对应数量列表
    return {
        "categories": categories,
        "counts": counts
    }


def get_paper_year_stats():
    """获取论文年份分布统计（适配MySQL）"""
    result = db.session.query(Result = db.session   会话.query   查询(
        # 关键修复：替换 strftime 为 MySQL 的 YEAR 函数
        func.YEAR(Paper.created_at).label('year'),
        func.count(Paper.paper_id).label('count')func.count   数 (Paper.paper_id) .label   标签(“计数”)
    ).group_by('year').order_by('year').all()

    # 适配前端的返回格式
    years = [int(item.year) for item in result]
    counts = [item.count for item in result]
    return {
        "years": years,
        "counts": counts
    }Return [{'year'：项。年份，` count `：物品。Count} for item in result]
