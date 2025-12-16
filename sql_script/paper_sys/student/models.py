# student/models.py
from user.models import db
from datetime import datetime


class PaperClick(db.Model):
    __tablename__ = 'paper_clicks'

    click_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    paper_id = db.Column(db.Integer, db.ForeignKey('papers.paper_id'), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.college_id'), nullable=False)
    click_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 关联论文信息
    paper = db.relationship('Paper', backref='clicks')

    def to_dict(self):
        return {
            'click_id': self.click_id,
            'user_id': self.user_id,
            'paper_id': self.paper_id,
            'paper_title': self.paper.title if self.paper else None,
            'click_time': self.click_time.strftime('%Y-%m-%d %H:%M:%S'),
            'pdf_url': self.paper.pdf_url if self.paper else None
        }


class Paper(db.Model):
    __tablename__ = 'papers'

    paper_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(500), nullable=False)
    arxiv_id = db.Column(db.String(50), unique=True, nullable=False)
    doi = db.Column(db.String(100), unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    abstract = db.Column(db.Text)
    pdf_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联分类
    category = db.relationship('Category', backref='papers')

    def to_dict(self):
        return {
            'paper_id': self.paper_id,
            'title': self.title,
            'arxiv_id': self.arxiv_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'created_at': self.created_at.strftime('%Y') if self.created_at else None
        }


class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'category_id': self.category_id,
            'code': self.code,
            'name': self.name
        }