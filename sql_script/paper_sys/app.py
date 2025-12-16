from flask import Flask, send_from_directory
from flask_login import LoginManager  # 新增：导入Flask-Login核心类
from user.views import blueprint
from student.views import blueprint as student_blueprint
from config import Config
from user.models import db, User  # 新增：导入User模型（用于用户加载）

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ========== 核心修复：初始化Flask-Login ==========
    login_manager = LoginManager()
    login_manager.init_app(app)  # 绑定到app
    login_manager.login_view = 'login_page'  # 未登录时跳转的登录页面（对应@app.route('/')）
    login_manager.session_protection = 'strong'  # 增强session保护

    # 实现用户加载回调（Flask-Login必需）
    @login_manager.user_loader
    def load_user(user_id):
        """根据user_id加载用户，必须返回User对象"""
        return User.query.get(int(user_id))

    # ========== 数据库初始化 ==========
    db.init_app(app)
    # ========== 注册蓝图 ==========
    app.register_blueprint(blueprint)
    app.register_blueprint(student_blueprint)

    # ========== 路由配置 ==========
    # 1. 公共界面路由跳转
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

    # 2. 学生界面路由跳转
    @app.route('/student/home')
    def student_home():
        return send_from_directory('static', 'HomeView.html')

    @app.route('/student/console')
    def student_console():
        return send_from_directory('static', 'student/console.html')

    @app.route('/student/overview')
    def student_overview():
        return send_from_directory('static', 'student/overview.html')

    # 3. 管理员界面路由跳转
    @app.route('/college_admin/home')
    @app.route('/university_admin/home')
    def admin_home():
        return send_from_directory('static', 'college_admin/HomeView.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)