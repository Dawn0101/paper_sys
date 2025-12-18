# student/repositories.py
from user.models import db, PaperClick, Paper, Category

from sqlalchemy import func


def get_student_click_history(user_id):
    """获取学生的论文浏览记录"""
    return PaperClick.query.filter_by(user_id=user_id).order_by(PaperClick.click_time.desc()).all()


def delete_click_record(click_id, user_id):
    """删除学生的特定浏览记录"""
    click = PaperClick.query.filter_by(click_id=click_id, user_id=user_id).first()
    if click:
        db.session.delete(click)
        db.session.commit()
        return True
    return False


def get_paper_category_stats():
    """获取论文分类统计数据（适配前端图表格式）"""
    result = db.session.query(
        Category.name,
        func.count(Paper.paper_id).label('count')
    ).join(Paper, Category.category_id == Paper.category_id
           ).group_by(Category.category_id).all()

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
    result = db.session.query(
        # 关键修复：替换 strftime 为 MySQL 的 YEAR 函数
        func.YEAR(Paper.created_at).label('year'),
        func.count(Paper.paper_id).label('count')
    ).group_by('year').order_by('year').all()

    # 适配前端的返回格式
    years = [int(item.year) for item in result]
    counts = [item.count for item in result]
    return {
        "years": years,
        "counts": counts
    }