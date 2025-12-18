# university_admin/repositories.py
from user.models import db, User, Role, College, PaperClick, Paper, Category
from datetime import datetime, date
from sqlalchemy import func, distinct, and_, or_
import logging

logger = logging.getLogger(__name__)

# ========== 用户管理相关函数 ==========
def get_all_users(page=1, per_page=20, search='', role=None, college_id=None):
    """获取所有用户（支持分页、搜索、角色筛选、学院筛选）"""
    try:
        query = User.query
        
        # 角色筛选
        if role:
            query = query.filter_by(role=Role[role])
        
        # 学院筛选
        if college_id:
            query = query.filter_by(college_id=college_id)
        
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
        
        return {
            "users": pagination.items,
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
            "pages": pagination.pages
        }
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        raise e

def get_user_by_id(user_id):
    """根据ID获取用户信息"""
    return User.query.get(user_id)

def update_user(user_id, username=None, real_name=None, password=None, role=None, college_id=None):
    """更新用户信息"""
    try:
        user = get_user_by_id(user_id)
        if not user:
            return False, "用户不存在"
        
        # 检查用户名是否重复
        if username and username != user.username:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and existing_user.user_id != user_id:
                return False, "用户名已存在"
        
        # 更新字段
        if username is not None:
            user.username = username
        if real_name is not None:
            user.real_name = real_name
        if password is not None:
            # 验证密码长度
            if len(password) < 6:
                return False, "密码长度不能小于6位"
            user.set_password(password)
        if role is not None:
            user.role = Role[role]
        if college_id is not None:
            # 检查学院是否存在
            college = College.query.get(college_id)
            if not college:
                return False, "学院不存在"
            user.college_id = college_id
        
        db.session.commit()
        return True, None
    except Exception as e:
        logger.error(f"更新用户信息失败: {e}")
        db.session.rollback()
        return False, f"更新用户信息失败: {str(e)}"

def delete_user(user_id):
    """删除用户"""
    try:
        user = get_user_by_id(user_id)
        if not user:
            return False, "用户不存在"
        
        # 删除用户的浏览记录
        PaperClick.query.filter_by(user_id=user_id).delete()
        
        # 删除用户
        db.session.delete(user)
        db.session.commit()
        return True, None
    except Exception as e:
        logger.error(f"删除用户失败: {e}")
        db.session.rollback()
        return False, f"删除用户失败: {str(e)}"

# ========== 学院点击量统计 ==========
def get_college_click_stats():
    """统计每个学院的总点击量并排行"""
    try:
        # 统计每个学院的总点击量
        college_stats = db.session.query(
            College.college_id,
            College.college_name,
            func.count(PaperClick.click_id).label('total_clicks')
        ).outerjoin(
            User, College.college_id == User.college_id
        ).outerjoin(
            PaperClick, User.user_id == PaperClick.user_id
        ).group_by(
            College.college_id,
            College.college_name
        ).order_by(
            func.count(PaperClick.click_id).desc()
        ).all()
        
        # 构造返回数据
        ranking = [
            {
                "college_id": item.college_id,
                "college_name": item.college_name,
                "total_clicks": item.total_clicks or 0
            }
            for item in college_stats
        ]
        
        return ranking
    except Exception as e:
        logger.error(f"统计学院点击量失败: {e}")
        raise e

# ========== 复用 college_admin 的函数 ==========
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

def get_all_colleges():
    """获取所有学院"""
    return College.query.all()

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
    """获取某学院学生的论文点击次数排行"""
    try:
        student_click_stats = db.session.query(
            User.user_id,
            User.username,
            User.real_name,
            func.count(PaperClick.click_id).label('click_count')
        ).join(
            User, PaperClick.user_id == User.user_id
        ).filter(
            User.college_id == college_id,
            User.role == Role.STUDENT
        ).group_by(
            User.user_id
        ).order_by(
            func.count(PaperClick.click_id).desc()
        ).all()

        ranking = [
            {
                "user_id": item.user_id,
                "username": item.username,
                "real_name": item.real_name or f"学生{item.user_id}",
                "click_count": item.click_count
            }
            for item in student_click_stats
        ]

        stats = {
            "ranking": ranking,
            "total_clicks": sum(item.click_count for item in student_click_stats),
            "total_students_with_clicks": len(ranking)
        }

        return stats
    except Exception as e:
        logger.error(f"统计学院[{college_id}]学生点击数据失败: {str(e)}")
        raise Exception(f"统计点击数据失败：{str(e)}")

