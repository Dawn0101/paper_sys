# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'none'

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.environ.get('MYSQL_USER', 'root')}:"
        f"{os.environ.get('MYSQL_PASSWORD', '4252210zxc')}@"
        f"{os.environ.get('MYSQL_HOST', 'localhost')}/"
        f"{os.environ.get('MYSQL_DB', 'paper_sys')}?charset=utf8mb4"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False