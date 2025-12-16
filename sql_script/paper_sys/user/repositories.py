# user/repositories.py
from .models import User,Role, College, db

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