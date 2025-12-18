# user/models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import enum
from flask_login import UserMixin
from datetime import datetime
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
    

class Category(db.Model):
    __tablename__ = 'categories'
    
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    
    def to_dict(self):
        return {
            "category_id": self.category_id,
            "code": self.code,
            "name": self.name
        }
    
class PaperClick(db.Model):
    __tablename__ = 'paper_clicks'
    
    click_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    paper_id = db.Column(db.Integer, db.ForeignKey('papers.paper_id'), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.college_id'), nullable=False)
    click_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # 关联关系
    user = db.relationship("User", backref="paper_clicks")
    paper = db.relationship("Paper", backref="paper_clicks")
    college = db.relationship("College", backref="paper_clicks")
    
    def to_dict(self):
        return {
            "click_id": self.click_id,
            "user_id": self.user_id,
            "paper_id": self.paper_id,
            "college_id": self.college_id,
            "click_time": self.click_time.isoformat() + 'Z' if self.click_time else None
        }

    def __repr__(self):
        return f"<PaperClick(user_id={self.user_id}, paper_id={self.paper_id}, time={self.click_time})>"
    



# ===== 新增：论文相关模型 =====
class Paper(db.Model):
    __tablename__ = 'papers'
    
    paper_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(500), nullable=False)
    arxiv_id = db.Column(db.String(50), unique=True, nullable=False)
    doi = db.Column(db.String(100), unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    # citation_count = db.Column(db.Integer, default=0)
    # publish_date = db.Column(db.Date)
    abstract = db.Column(db.Text)
    pdf_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联分类
    category = db.relationship("Category", backref="papers")
    
    def to_dict(self):

        
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "arxiv_id": self.arxiv_id,
            "doi": self.doi,
            "abstract": self.abstract,
            "pdf_url": self.pdf_url,
            "category": self.category.to_dict() if self.category else None,
        }