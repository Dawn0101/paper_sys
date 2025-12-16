import re
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, login_user  # 导入login_user
from user.models import User, Role
from user.repositories import get_college_by_id, username_exists, create_user , get_user_by_username, get_all_colleges

blueprint = Blueprint("user", __name__, url_prefix="/user")


# ===== 1.学院列表 API =====
@blueprint.route("/api/colleges", methods=["GET"])
def colleges_api():
    try:
        colleges = get_all_colleges()
        return jsonify({
            "code": 200,
            "message": "获取学院列表成功",
            "data": colleges
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取学院失败: {e}")
        return jsonify({
            "code": 500,
            "message": "获取学院列表失败"
        }), 500


# ===== 2.登录 API =====
@blueprint.route("/api/login", methods=["POST"])
def login_api():
    data = request.get_json()
    if not data:
        return jsonify({
            "code": 400,
            "message": "请求体必须是 JSON"
        }), 400

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({
            "code": 400,
            "message": "用户名和密码不能为空"
        }), 400

    user = get_user_by_username(username)
    if user and user.check_password(password):
        # ========== 核心修复1：执行login_user保存登录状态 ==========
        login_user(user, remember=True)  # remember=True 可选，记住登录

        # ========== 核心修复2：role_map键改为小写（匹配数据库/枚举） ==========
        role_map = {
            "student": "/student/home",  # 小写，匹配枚举值
            "college_admin": "/college_admin/home",
            "university_admin": "/university_admin/home"
        }
        # 动态获取跳转路径（删除手动写死的 /user/HomeView）
        redirect_path = role_map.get(user.role.value, "/home")

        return jsonify({
            "code": 200,
            "message": "登录成功",
            "data": {
                "user_id": user.user_id,
                "username": user.username,
                "real_name": user.real_name,
                "role": user.role.value,
                "college_id": user.college_id
            },
            "redirect": redirect_path  # 返回动态路径，而非固定 /user/HomeView
        }), 200
    else:
        return jsonify({
            "code": 401,
            "message": "用户名或密码错误"
        }), 401


# ===== 3.注册 API=====
@blueprint.route('/api/register', methods=['POST'])
def register_api():
    data = request.get_json()
    if not data:
        return jsonify({"error": "无效 JSON"}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    real_name = data.get('real_name', '').strip()
    # ========== 修复：注册时转小写（匹配数据库/枚举） ==========
    role_str = data.get('role', 'student').strip().lower()
    college_id = data.get('college_id')

    # 验证字段
    if not all([username, password, real_name, college_id]):
        return jsonify({"error": "所有字段都是必填的"}), 400

    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return jsonify({"error": "用户名只能包含字母、数字、下划线，长度 3-20"}), 400

    # 验证角色是否在枚举的小写值中
    if role_str not in [r.value for r in Role]:
        return jsonify({"error": f"角色无效，必须是: {[r.value for r in Role]}"}), 400

    # 校验学院和用户名
    try:
        if username_exists(username):
            return jsonify({"error": "用户名已存在"}), 400

        college = get_college_by_id(college_id)
        if not college:
            return jsonify({"error": "学院ID不存在"}), 400

        # 创建用户
        user_id = create_user(username, password, real_name, role_str, college_id)

        return jsonify({
            "code": 201,
            "message": "注册成功",
            "data": {
                "user_id": user_id,
                "username": username,
                "real_name": real_name,
                "role": role_str,
                "college_id": college_id
            }
        }), 201

    except Exception as e:
        current_app.logger.error(f"注册失败: {e}")
        return jsonify({"error": "注册失败，请稍后重试"}), 500