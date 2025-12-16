# user/models.py
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()

class Role(str, enum.Enum):
    university_admin = "university_admin"
    college_admin = "college_admin"
    student = "student"

class College(db.Model):
    __tablename__ = 'colleges'
    college_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    college_name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False, unique=True)

    def to_dict(self):
        return {
            "college_id": self.college_id,
            "college_name": self.college_name,
            "code": self.code
        }

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键是user_id
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.college_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    college = db.relationship("College", backref="users")

    # ========== 核心修复：重写get_id方法 ==========
    def get_id(self):
        """返回用户唯一标识（必须是字符串）"""
        return str(self.user_id)  # 用user_id替代默认的id

    def set_password(self, password):
        self.password_hash = password  # 生产环境改为generate_password_hash(password)

    def check_password(self, password):
        return self.password_hash == password  # 生产环境改为check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "real_name": self.real_name,
            "role": self.role.value,
            "college_id": self.college_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "college": self.college.to_dict() if self.college else None
        }