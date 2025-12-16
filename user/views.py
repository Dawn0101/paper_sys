# user/views.py
import re
from datetime import datetime  
from flask import Blueprint, render_template, request, jsonify, current_app
from .models import User, Role
from .repositories import get_college_by_id, username_exists, create_user , get_user_by_username, get_all_colleges, UserTaskRepository

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

        # 统一跳转到 HomeView 由前端处理具体页面
        redirect_path = "/user/HomeView" 

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
            "redirect": redirect_path
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
    role_str = data.get('role', 'student').strip().upper()  # 转为大写
    college_id = data.get('college_id')

    # 验证字段
    if not all([username, password, real_name, college_id]):
        return jsonify({"error": "所有字段都是必填的"}), 400

    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return jsonify({"error": "用户名只能包含字母、数字、下划线，长度 3-20"}), 400

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



# ===== 1. 获取用户所有任务（表格用）=====
@blueprint.route("/api/tasks", methods=["GET"])
def get_user_tasks():
    user_id = request.args.get('user_id')  # 前端传 user_id，或从 token 解析
    if not user_id:
        return jsonify({'code': 400, 'message': '缺少 user_id'}), 400

    tasks = UserTaskRepository.get_all_tasks(user_id)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': [task.to_dict() for task in tasks]
    })

# ===== 获取单个任务详情 =====
@blueprint.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task_detail(task_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'code': 400, 'message': '缺少 user_id'}), 400

    task = UserTaskRepository.get_task_by_id(task_id, user_id)
    if not task:
        return jsonify({'code': 404, 'message': '任务不存在或无权访问'}), 404

    return jsonify({
        'code': 200,
        'data': task.to_dict()
    })
# ===== 2. 创建新任务 =====
@blueprint.route("/api/tasks/create", methods=["POST"])
def create_task():
    data = request.get_json()
    required_fields = ['user_id', 'scheduled_date', 'title']
    for field in required_fields:
        if field not in data:
            return jsonify({'code': 400, 'message': f'缺少必填字段: {field}'}), 400

    try:
        scheduled_date = datetime.fromisoformat(data['scheduled_date']).date()
    except Exception:
        return jsonify({'code': 400, 'message': '日期格式错误'}), 400

    task = UserTaskRepository.create_task(
        user_id=data['user_id'],
        data={
            'scheduled_date': scheduled_date,
            'title': data['title'],
            # 'description': data.get('description', ''),
            'priority': data.get('priority', 'medium'),
            'status': data.get('status', 'pending')
        }
    )

    return jsonify({
        'code': 201,
        'message': '创建成功',
        'data': task.to_dict()
    })

# ===== 3. 更新任务 =====
@blueprint.route("/api/tasks/<int:task_id>/update", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    task = UserTaskRepository.update_task(task_id, data)
    if not task:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': task.to_dict()
    })

# ===== 4. 完成任务 =====
@blueprint.route("/api/tasks/<int:task_id>/complete", methods=["PUT"])
def complete_task(task_id):
    task = UserTaskRepository.complete_task(task_id)
    if not task:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404
    return jsonify({
        'code': 200,
        'message': '任务已完成',
        'data': task.to_dict()
    })

# ===== 5. 删除任务 =====
@blueprint.route("/api/tasks/<int:task_id>/delete", methods=["DELETE"])
def delete_task(task_id):
    success = UserTaskRepository.delete_task(task_id)
    if not success:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })

# ===== 6. 日历事件接口 =====
@blueprint.route("/api/tasks/calendar/", methods=["GET"])
def get_calendar_events():
    user_id = request.args.get('user_id')
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    if not user_id or not start_str or not end_str:
        return jsonify({'code': 400, 'message': '缺少参数'}), 400

    try:
        start_date = datetime.fromisoformat(start_str.replace('Z', '+00:00')).date()
        end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00')).date()
    except Exception:
        return jsonify({'code': 400, 'message': '日期格式错误'}), 400

    tasks = UserTaskRepository.get_calendar_events(user_id, start_date, end_date)

    events = []
    for task in tasks:
        events.append({
            'id': str(task.task_id),
            'title': task.title,
            'start': task.scheduled_date.isoformat(),
            'backgroundColor': get_priority_color(task.priority),
            'borderColor': get_priority_color(task.priority),
            'extendedProps': {
                'priority': task.priority,
                'status': task.status,
                # 'description': task.description or ''
            }
        })

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': events
    })

def get_priority_color(priority):
    color_map = {
        'high': '#f56c6c',
        'medium': '#e6a23c',
        'low': '#67c23a'
    }
    return color_map.get(priority, '#409EFF')
