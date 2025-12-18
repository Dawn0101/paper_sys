<<<<<<< Updated upstream
# user/repositories.py
from datetime import date
from .models import User, Role, College, UserTask, db

class UserTaskRepository:
    @staticmethod
    def get_all_tasks(user_id: int):
        return UserTask.query.filter_by(user_id=user_id).order_by(UserTask.created_at.desc()).all()

    @staticmethod
    def create_task(user_id: int, data: dict):
        task = UserTask(
            user_id=user_id,
            scheduled_date=data['scheduled_date'],
            title=data['title'],
            # description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'pending')
        )
        db.session.add(task)
        db.session.commit()
        # Flask-SQLAlchemy 不支持 refresh()，但插入后 ID 已自动赋值
        return task

    @staticmethod
    def update_task(task_id: int, data: dict):
        task = UserTask.query.get(task_id)
        if not task:
            return None
        for key, value in data.items():
            if hasattr(task, key):
                setattr(task, key, value)
        # 自动更新 updated_at（如果模型中用了 default + onupdate）
        db.session.commit()
        return task

    @staticmethod
    def complete_task(task_id: int):
        task = UserTask.query.get(task_id)
        if not task:
            return None
        task.status = 'completed'
        db.session.commit()
        return task

    @staticmethod
    def delete_task(task_id: int):
        task = UserTask.query.get(task_id)
        if not task:
            return False
        db.session.delete(task)
        db.session.commit()
        return True

    @staticmethod
    def get_calendar_events(user_id: int, start_date: date, end_date: date):
        return UserTask.query.filter(
            UserTask.user_id == user_id,
            UserTask.scheduled_date >= start_date,
            UserTask.scheduled_date <= end_date
        ).all()
    
    @staticmethod
    def get_task_by_id(task_id: int, user_id: int) -> UserTask | None:
        """
        根据任务 ID 和用户 ID 获取单个任务（确保权限隔离）
        """
        return UserTask.query.filter_by(
            task_id=task_id,
            user_id=user_id
        ).first()


def get_user_by_username(username: str) -> User | None:
    return User.query.filter_by(username=username).first()

def get_all_colleges():
    colleges = College.query.all()
    return [c.to_dict() for c in colleges]

def get_college_by_id(college_id: int) -> College | None:
    return College.query.get(college_id)

def username_exists(username: str) -> bool:
    return User.query.filter_by(username=username).first() is not None

def create_user(username: str, password: str, real_name: str, role: str, college_id: int) -> int:
    """创建用户并返回 user_id"""
    if username_exists(username):
        raise ValueError("用户名已存在")
    
    college = get_college_by_id(college_id)
    if not college:
        raise ValueError("学院不存在")

    user = User(
        username=username,
        real_name=real_name,
        role=Role(role.upper()),
        college_id=college_id
    )
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
        return user.user_id
    except Exception as e:
        db.session.rollback()
        raise e

def get_user_by_id(user_id):
    return User.query.get(user_id)

def update_username(user_id, new_username):
    """更新用户名，返回 (success: bool, message: str)"""
    user = User.query.get(user_id)
    if not user:
        return False, "用户不存在"

    # 检查新用户名是否已被他人使用
    existing = User.query.filter(User.username == new_username, User.user_id != user_id).first()
    if existing:
        return False, "用户名已存在"

    try:
        user.username = new_username
        db.session.commit()
        return True, "用户名修改成功"
    except Exception as e:
        db.session.rollback()
        return False, "数据库更新失败"

def update_password(user_id, old_password, new_password):
    """更新密码，返回 (success: bool, message: str)"""
    user = User.query.get(user_id)
    if not user:
        return False, "用户不存在"

    if not user.check_password(old_password):
        return False, "当前密码错误"

    try:
        user.set_password(new_password)
        db.session.commit()
        return True, "密码修改成功"
    except Exception as e:
        db.session.rollback()
        return False, "数据库更新失败"
=======
# user/repositories.py
from datetime import date
from .models import User, Role, College, UserTask, db

#**********新增代码********
from .models import Paper, Category
from sqlalchemy import and_, or_, func



class UserTaskRepository:
    @staticmethod
    def get_all_tasks(user_id: int):
        return UserTask.query.filter_by(user_id=user_id).order_by(UserTask.created_at.desc()).all()

    @staticmethod
    def create_task(user_id: int, data: dict):
        task = UserTask(
            user_id=user_id,
            scheduled_date=data['scheduled_date'],
            title=data['title'],
            # description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'pending')
        )
        db.session.add(task)
        db.session.commit()
        # Flask-SQLAlchemy 不支持 refresh()，但插入后 ID 已自动赋值
        return task

    @staticmethod
    def update_task(task_id: int, data: dict):
        task = UserTask.query.get(task_id)
        if not task:
            return None
        for key, value in data.items():
            if hasattr(task, key):
                setattr(task, key, value)
        # 自动更新 updated_at（如果模型中用了 default + onupdate）
        db.session.commit()
        return task

    @staticmethod
    def complete_task(task_id: int):
        task = UserTask.query.get(task_id)
        if not task:
            return None
        task.status = 'completed'
        db.session.commit()
        return task

    @staticmethod
    def delete_task(task_id: int):
        task = UserTask.query.get(task_id)
        if not task:
            return False
        db.session.delete(task)
        db.session.commit()
        return True

    @staticmethod
    def get_calendar_events(user_id: int, start_date: date, end_date: date):
        return UserTask.query.filter(
            UserTask.user_id == user_id,
            UserTask.scheduled_date >= start_date,
            UserTask.scheduled_date <= end_date
        ).all()
    
    @staticmethod
    def get_task_by_id(task_id: int, user_id: int) -> UserTask | None:
        """
        根据任务 ID 和用户 ID 获取单个任务（确保权限隔离）
        """
        return UserTask.query.filter_by(
            task_id=task_id,
            user_id=user_id
        ).first()


def get_user_by_username(username: str) -> User | None:
    return User.query.filter_by(username=username).first()

def get_all_colleges():
    colleges = College.query.all()
    return [c.to_dict() for c in colleges]

def get_college_by_id(college_id: int) -> College | None:
    return College.query.get(college_id)

def username_exists(username: str) -> bool:
    return User.query.filter_by(username=username).first() is not None

def create_user(username: str, password: str, real_name: str, role: str, college_id: int) -> int:
    """创建用户并返回 user_id"""
    if username_exists(username):
        raise ValueError("用户名已存在")
    
    college = get_college_by_id(college_id)
    if not college:
        raise ValueError("学院不存在")

    user = User(
        username=username,
        real_name=real_name,
        role=Role(role.upper()),
        college_id=college_id
    )
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
        return user.user_id
    except Exception as e:
        db.session.rollback()
        raise e

def get_user_by_id(user_id):
    return User.query.get(user_id)

def update_username(user_id, new_username):
    """更新用户名，返回 (success: bool, message: str)"""
    user = User.query.get(user_id)
    if not user:
        return False, "用户不存在"

    # 检查新用户名是否已被他人使用
    existing = User.query.filter(User.username == new_username, User.user_id != user_id).first()
    if existing:
        return False, "用户名已存在"

    try:
        user.username = new_username
        db.session.commit()
        return True, "用户名修改成功"
    except Exception as e:
        db.session.rollback()
        return False, "数据库更新失败"

def update_password(user_id, old_password, new_password):
    """更新密码，返回 (success: bool, message: str)"""
    user = User.query.get(user_id)
    if not user:
        return False, "用户不存在"

    if not user.check_password(old_password):
        return False, "当前密码错误"

    try:
        user.set_password(new_password)
        db.session.commit()
        return True, "密码修改成功"
    except Exception as e:
        db.session.rollback()
        return False, "数据库更新失败"
    




#**********新增代码********
# ===== 论文搜索相关函数 =====
def search_papers_by_params(search_params):
    """
    根据搜索参数查询论文
    """
    # 基础查询
    query = db.session.query(Paper).distinct()
    
    # 关联必要的表
    query = query.join(Paper.category)
    
    # 构建过滤条件
    filters = []
    
    if 'title' in search_params:
        filters.append(Paper.title.ilike(f"%{search_params['title']}%"))
    
    if 'doi' in search_params:
        filters.append(Paper.doi.ilike(f"%{search_params['doi']}%"))
    
    if 'category' in search_params:
        category_filter = or_(
            Category.code.ilike(f"%{search_params['category']}%"),
            Category.name.ilike(f"%{search_params['category']}%")
        )
        filters.append(category_filter)

    
    # 应用所有过滤条件
    if filters:
        query = query.filter(and_(*filters))
    
    query = query.order_by( Paper.paper_id.desc())
    
    # 执行查询
    papers = query.all()
    return papers

def get_paper_with_authors(paper_id):
    """
    获取论文及其作者信息
    """
    paper = Paper.query.get(paper_id)
    if not paper:
        return None

    
    paper_dict = paper.to_dict()
    # paper_dict['authors'] = author_data
    return paper_dict
>>>>>>> Stashed changes
