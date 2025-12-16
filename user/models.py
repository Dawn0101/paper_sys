# user/models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import enum
from flask_login import UserMixin

db = SQLAlchemy()

class Role(str, enum.Enum):
    UNIVERSITY_ADMIN = "UNIVERSITY_ADMIN"
    COLLEGE_ADMIN = "COLLEGE_ADMIN"
    STUDENT = "STUDENT"

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

    def __repr__(self):
        return f"<College(name='{self.college_name}', code='{self.code}')>"

class User(db.Model , UserMixin):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.college_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # 关联学院
    college = db.relationship("College", backref="users")

    def set_password(self, password):
        # self.password_hash = generate_password_hash(password)
        self.password_hash = password

    def check_password(self, password):
        # return check_password_hash(self.password_hash, password)
        return self.password_hash == password

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

class UserTask(db.Model):
    __tablename__ = 'user_tasks'

    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)  # 可加外键：db.ForeignKey('users.user_id')
    scheduled_date = db.Column(db.Date, nullable=False)  
    title = db.Column(db.String(200), nullable=False)
    # description = db.Column(db.Text, nullable=True)  # 补充缺失的 description 字段
    priority = db.Column(db.String(10), nullable=False, default='medium')
    status = db.Column(db.String(15), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    def to_dict(self):
        return {
            'task_id': self.task_id,
            'user_id': self.user_id,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'title': self.title,
            # 'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }