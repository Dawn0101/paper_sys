# app.py
from flask import Flask, send_from_directory
from user.views import blueprint  # ← 改成 blueprint
from student.views import blueprint as student_blueprint  # 新增：导入学生蓝图
from config import Config
from user.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # 注册蓝图
    app.register_blueprint(blueprint)  # ← 这里也用 blueprint
    app.register_blueprint(student_blueprint)   #新增学生蓝图注册

    # 1.公共界面路由跳转
    @app.route('/')
    @app.route('/user/login')
    def login_page():
        return send_from_directory('static', 'LoginView.html')
    
    @app.route('/user/HomeView')
    def home_view():
        return send_from_directory('static', 'HomeView.html')
    
    @app.route('/user/search')
    def search_view():
        return send_from_directory('static', 'SearchView.html')

    @app.route('/user/settings')
    def settings_view():
        return send_from_directory('static', 'SettingsView.html')
    

    # 2.学生界面路由跳转(其余admin用户同理)
    @app.route('/student/home')
    def student_home():
        return send_from_directory('static', 'student/HomeView.html')

    @app.route('/student/console')
    def student_console():
        return send_from_directory('static', 'student/console.html')

    @app.route('/student/overview')
    def student_overview():
        return send_from_directory('static', 'student/overview.html')


    @app.route('/college_admin/home')
    @app.route('/university_admin/home')
    def admin_home():
        return send_from_directory('static', 'college_admin/HomeView.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)