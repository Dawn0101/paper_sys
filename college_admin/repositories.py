# college_admin/repositories.py
from user.models import db, User, Role, College

# user.models和student.models中模型冲突，优先选择
from user.models import PaperClick, Paper, Category

from datetime import datetime, date
from sqlalchemy import func, distinct, and_, or_
import logging
from functools import wraps
from flask import request, jsonify, current_app
import json

logger = logging.getLogger(__name__)

# ========== 新增：从请求头获取用户信息的函数 ==========
def get_user_from_request():
    """从请求头获取用户信息"""
    try:
        # 从请求头获取用户信息
        user_info_str = request.headers.get('X-User-Info')
        if not user_info_str:
            return None
        
        # 解析用户信息
        user_info = json.loads(user_info_str)
        
        # 从数据库获取用户
        user = User.query.filter_by(
            user_id=user_info.get('user_id'),
            role=user_info.get('role')
        ).first()
        
        return user
    except Exception as e:
        logger.error(f"从请求头获取用户信息失败: {e}")
        return None

def get_current_user():
    """获取当前用户（兼容多种方式）"""
    # 首先尝试从请求头获取
    user = get_user_from_request()
    if user:
        return user
    
    # 如果没有从请求头获取到，尝试从Flask-Login获取
    try:
        from flask_login import current_user
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            return current_user
    except Exception as e:
        logger.debug(f"无法从Flask-Login获取用户: {e}")
    
    return None

# ========== 新增：权限检查装饰器 ==========
def require_college_admin(f):
    """要求学院管理员权限的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取当前用户
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({
                "code": 401,
                "message": "用户未登录"
            }), 401
        
        # 检查用户角色
        if current_user.role != Role.COLLEGE_ADMIN:
            return jsonify({
                "code": 403,
                "message": "权限不足，需要学院管理员权限"
            }), 403
        
        # 将用户传递给视图函数
        return f(current_user, *args, **kwargs)
    
    return decorated_function

# ========== 修改原有函数，移除对current_user的直接依赖 ==========
def get_students_by_college(college_id, page=1, per_page=20, search=''):
    """获取某学院的所有学生用户（支持分页和搜索）"""
    try:
        query = User.query.filter_by(college_id=college_id, role=Role.STUDENT)
        
        # 搜索功能
        if search:
            query = query.filter(
                or_(
                    User.username.like(f'%{search}%'),
                    User.real_name.like(f'%{search}%')
                )
            )
        
        # 分页查询
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # 获取统计信息
        total_students = query.count()
        
        # 获取今日活跃学生数
        today = date.today()
        student_ids = [student.user_id for student in pagination.items]
        active_today = 0
        if student_ids:
            active_today = db.session.query(distinct(PaperClick.user_id)).filter(
                PaperClick.user_id.in_(student_ids),
                func.date(PaperClick.click_time) == today
            ).count()
        
        # 获取总浏览数
        total_clicks = 0
        if student_ids:
            total_clicks = PaperClick.query.filter(PaperClick.user_id.in_(student_ids)).count()
        
        return {
            "students": pagination.items,
            "total": total_students,
            "page": page,
            "per_page": per_page,
            "pages": pagination.pages,
            "stats": {
                "total_students": total_students,
                "active_today": active_today,
                "total_clicks": total_clicks
            }
        }
    except Exception as e:
        logger.error(f"获取学生列表失败: {e}")
        raise e

# 修改其他函数，添加用户参数
def get_student_by_id(student_id, college_id=None):
    """根据ID获取学生信息"""
    query = User.query.filter_by(user_id=student_id, role=Role.STUDENT)
    if college_id:
        query = query.filter_by(college_id=college_id)
    return query.first()

def create_student(username, real_name, password, college_id):
    """创建新学生"""
    try:
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return None, "用户名已存在"
        
        # 创建新学生
        new_student = User(
            username=username,
            real_name=real_name,
            role=Role.STUDENT,
            college_id=college_id
        )
        new_student.set_password(password)
        
        db.session.add(new_student)
        db.session.commit()
        return new_student, None
    except Exception as e:
        logger.error(f"创建学生失败: {e}")
        db.session.rollback()
        return None, f"创建学生失败: {str(e)}"

def update_student(student_id, real_name=None, password=None, college_id=None):
    """更新学生信息"""
    try:
        student = get_student_by_id(student_id, college_id)
        if not student:
            return False, "学生不存在"
        
        if real_name is not None:
            student.real_name = real_name
        
        if password is not None:
            student.set_password(password)
        
        db.session.commit()
        return True, None
    except Exception as e:
        logger.error(f"更新学生信息失败: {e}")
        db.session.rollback()
        return False, f"更新学生信息失败: {str(e)}"

def reset_password_for_students(user_id, current_user):
    """重置用户密码（需要管理员权限）"""
    # 检查当前用户是否有权限重置密码
    student = get_student_by_id(user_id, current_user.college_id)
    if not student:
        return False, "学生不存在或无权限"
    
    student.set_password("123456")  # 重置为默认密码
    db.session.commit()
    return True, None

def delete_student_user(user_id, current_user):
    """删除学生用户（需要管理员权限）"""
    try:
        student = get_student_by_id(user_id, current_user.college_id)
        if not student:
            return False, "学生不存在或无权限"
        
        # 删除学生的浏览记录
        PaperClick.query.filter_by(user_id=user_id).delete()
        
        # 删除学生用户
        db.session.delete(student)
        db.session.commit()
        return True, None
    except Exception as e:
        logger.error(f"删除学生用户失败: {e}")
        db.session.rollback()
        return False, f"删除学生用户失败: {str(e)}"

# 修改论文管理函数
def get_papers(page=1, per_page=20, search='', category_id=None):
    """获取论文列表（支持分页、搜索、筛选）"""
    try:
        query = Paper.query
        
        # 搜索功能
        if search:
            query = query.filter(
                or_(
                    Paper.title.like(f'%{search}%'),
                    Paper.arxiv_id.like(f'%{search}%')
                )
            )
        
        # 分类筛选
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        # 获取统计信息
        total_papers = query.count()
        
        today = date.today()
        today_papers = Paper.query.filter(
            func.date(Paper.created_at) == today
        ).count()
        
        category_count = Category.query.count()
        
        today_clicks = PaperClick.query.filter(
            func.date(PaperClick.click_time) == today
        ).count()
        
        # 分页查询
        pagination = query.order_by(Paper.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # 为每篇论文添加点击数和分类名称
        papers_with_stats = []
        for paper in pagination.items:
            paper_dict = paper.to_dict()
            paper_dict['click_count'] = PaperClick.query.filter_by(paper_id=paper.paper_id).count()
            paper_dict['category_name'] = paper.category.name if paper.category else None
            papers_with_stats.append(paper_dict)
        
        return {
            "papers": papers_with_stats,
            "total": total_papers,
            "page": page,
            "per_page": per_page,
            "pages": pagination.pages,
            "stats": {
                "total_papers": total_papers,
                "today_papers": today_papers,
                "category_count": category_count,
                "today_clicks": today_clicks
            }
        }
    except Exception as e:
        logger.error(f"获取论文列表失败: {e}")
        raise e

def get_paper_by_id(paper_id):
    """根据ID获取论文信息"""
    return Paper.query.get(paper_id)

def create_paper(title, arxiv_id, category_id, pdf_url, doi=None, abstract=None):
    """创建新论文"""
    try:
        # 检查arXiv ID是否已存在
        existing_paper = Paper.query.filter_by(arxiv_id=arxiv_id).first()
        if existing_paper:
            return None, "arXiv ID已存在"
        
        # 检查分类是否存在
        category = Category.query.get(category_id)
        if not category:
            return None, "分类不存在"
        
        # 创建新论文
        new_paper = Paper(
            title=title,
            arxiv_id=arxiv_id,
            doi=doi,
            category_id=category_id,
            abstract=abstract,
            pdf_url=pdf_url
        )
        
        db.session.add(new_paper)
        db.session.commit()
        return new_paper, None
    except Exception as e:
        logger.error(f"创建论文失败: {e}")
        db.session.rollback()
        return None, f"创建论文失败: {str(e)}"

def update_paper(paper_id, **kwargs):
    """更新论文信息"""
    try:
        paper = get_paper_by_id(paper_id)
        if not paper:
            return False, "论文不存在"
        
        # 检查arXiv ID是否重复
        if 'arxiv_id' in kwargs and kwargs['arxiv_id'] != paper.arxiv_id:
            existing_paper = Paper.query.filter_by(arxiv_id=kwargs['arxiv_id']).first()
            if existing_paper and existing_paper.paper_id != paper_id:
                return False, "arXiv ID已存在"
        
        # 检查分类是否存在
        if 'category_id' in kwargs:
            category = Category.query.get(kwargs['category_id'])
            if not category:
                return False, "分类不存在"
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(paper, key) and value is not None:
                setattr(paper, key, value)
        
        paper.updated_at = datetime.utcnow()
        db.session.commit()
        return True, None
    except Exception as e:
        logger.error(f"更新论文失败: {e}")
        db.session.rollback()
        return False, f"更新论文失败: {str(e)}"

def delete_paper(paper_id):
    """删除论文"""
    try:
        paper = get_paper_by_id(paper_id)
        if not paper:
            return False
        
        # 删除相关的浏览记录
        PaperClick.query.filter_by(paper_id=paper_id).delete()
        
        # 删除论文
        db.session.delete(paper)
        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"删除论文失败: {e}")
        db.session.rollback()
        return False

def get_all_categories():
    """获取所有分类"""
    return Category.query.all()

def get_dashboard_stats(college_id):
    """获取仪表板统计数据"""
    today = date.today()
    
    # 学院学生总数
    total_students = User.query.filter_by(
        role=Role.STUDENT,
        college_id=college_id
    ).count()
    
    # 今日活跃学生数
    student_ids = [u.user_id for u in User.query.filter_by(
        role=Role.STUDENT,
        college_id=college_id
    ).all()]
    
    active_today = 0
    if student_ids:
        active_today = db.session.query(distinct(PaperClick.user_id)).filter(
            PaperClick.user_id.in_(student_ids),
            func.date(PaperClick.click_time) == today
        ).count()
    
    # 学院总浏览数
    total_clicks = 0
    if student_ids:
        total_clicks = PaperClick.query.filter(PaperClick.user_id.in_(student_ids)).count()
    
    # 论文总数
    total_papers = Paper.query.count()
    
    # 今日新增论文
    today_papers = Paper.query.filter(
        func.date(Paper.created_at) == today
    ).count()
    
    # 分类数量
    category_count = Category.query.count()
    
    # 今日浏览数
    today_clicks = PaperClick.query.filter(
        func.date(PaperClick.click_time) == today
    ).count()
    
    return {
        "student_stats": {
            "total_students": total_students,
            "active_today": active_today,
            "total_clicks": total_clicks
        },
        "paper_stats": {
            "total_papers": total_papers,
            "today_papers": today_papers,
            "category_count": category_count,
            "today_clicks": today_clicks
        }
    }

# 原有的其他函数保持不变
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

    categories = [item.name for item in result]
    counts = [item.count for item in result]
    return {
        "categories": categories,
        "counts": counts
    }

def get_paper_year_stats():
    """获取论文年份分布统计（适配MySQL）"""
    result = db.session.query(
        func.YEAR(Paper.created_at).label('year'),
        func.count(Paper.paper_id).label('count')
    ).group_by('year').order_by('year').all()

    years = [int(item.year) for item in result]
    counts = [item.count for item in result]
    return {
        "years": years,
        "counts": counts
    }

def get_click_stats_by_college(college_id):
    """
    获取某学院学生的论文点击次数排行
    核心逻辑：
    1. 关联PaperClick（点击记录表）和User（用户表）
    2. 过滤条件：仅该学院 + 学生角色的用户
    3. 按user_id分组，统计每个学生的总点击次数
    4. 按点击次数降序排序，返回排行数据
    """
    try:
        # 核心SQL查询：统计学生点击次数
        student_click_stats = db.session.query(
            User.user_id,          # 学生ID
            User.username,         # 学生用户名
            User.real_name,        # 学生真实姓名
            func.count(PaperClick.click_id).label('click_count')  # 总点击次数
        ).join(
            # 关联点击表和用户表（通过user_id）
            User, PaperClick.user_id == User.user_id
        ).filter(
            # 过滤1：仅该学院的用户
            User.college_id == college_id,
            # 过滤2：仅学生角色（str枚举直接用Role.STUDENT，等价于"STUDENT"）
            User.role == Role.STUDENT
        ).group_by(
            # 按用户ID分组，合并同一学生的所有点击事件
            User.user_id
        ).order_by(
            # 按点击次数降序排序（排行核心）
            func.count(PaperClick.click_id).desc()
        ).all()

        # 构造前端需要的排行数据结构
        ranking = [
            {
                "user_id": item.user_id,
                "username": item.username,
                "real_name": item.real_name or f"学生{item.user_id}",  # 空值兜底
                "click_count": item.click_count
            }
            for item in student_click_stats
        ]

        # 构造完整统计数据（适配前端接收结构）
        stats = {
            "ranking": ranking,                  # 学生点击排行（核心）
            "total_clicks": sum(item.click_count for item in student_click_stats),  # 学院总点击数
            "total_students_with_clicks": len(ranking)  # 有点击记录的学生数
        }

        return stats

    except Exception as e:
        current_app.logger.error(f"统计学院[{college_id}]学生点击数据失败: {str(e)}")
        raise Exception(f"统计点击数据失败：{str(e)}")