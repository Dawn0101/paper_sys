<<<<<<< Updated upstream
# user/views.py
import re
from datetime import datetime  
from flask import Blueprint, render_template, request, jsonify, current_app
from .models import User, Role
from .repositories import get_college_by_id, username_exists, create_user , get_user_by_username, get_all_colleges, UserTaskRepository, get_user_by_id, update_username as change_username, update_password as change_password

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

# ===== 修改用户名 API =====
@blueprint.route("/api/update-username", methods=["PUT"])
def update_username_api():
    data = request.get_json()
    if not data:
        return jsonify({
            "code": 400,
            "message": "请求体必须是 JSON"
        }), 400

    user_id = data.get("user_id")
    new_username = data.get("new_username", "").strip()

    if not user_id or not isinstance(user_id, int):
        return jsonify({
            "code": 400,
            "message": "缺少有效的 user_id"
        }), 400

    if not new_username:
        return jsonify({
            "code": 400,
            "message": "新用户名不能为空"
        }), 400

    success, msg = change_username(user_id, new_username)

    if success:
        # 返回更新后的用户信息（可选）
        user = get_user_by_id(user_id)
        return jsonify({
            "code": 200,
            "message": msg,
            "data": {
                "user_id": user.user_id,
                "username": user.username,
                "real_name": user.real_name,
                "role": user.role.value,
                "college_id": user.college_id
            }
        }), 200
    else:
        return jsonify({
            "code": 400,
            "message": msg
        }), 400

# ===== 修改密码 API =====
@blueprint.route("/api/change-password", methods=["PUT"])
def change_password_api():
    data = request.get_json()
    if not data:
        return jsonify({
            "code": 400,
            "message": "请求体必须是 JSON"
        }), 400

    user_id = data.get("user_id")
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not user_id or not isinstance(user_id, int):
        return jsonify({
            "code": 400,
            "message": "缺少有效的 user_id"
        }), 400

    if not old_password or not new_password:
        return jsonify({
            "code": 400,
            "message": "当前密码和新密码均不能为空"
        }), 400

    success, msg = change_password(user_id, old_password, new_password)

    if success:
        return jsonify({
            "code": 200,
            "message": msg
        }), 200
    else:
        return jsonify({
            "code": 400,
            "message": msg
        }), 400
=======
# user/views.py
import re
from datetime import datetime  
from flask import Blueprint, render_template, request, jsonify, current_app
from .models import User, Role
from .repositories import get_college_by_id, username_exists, create_user , get_user_by_username, get_all_colleges, UserTaskRepository, get_user_by_id, update_username as change_username, update_password as change_password

#****新增代码*******
from .repositories import search_papers_by_params, get_paper_with_authors
from .models import College, db, Paper,db, PaperClick
from datetime import timedelta

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

# ===== 修改用户名 API =====
@blueprint.route("/api/update-username", methods=["PUT"])
def update_username_api():
    data = request.get_json()
    if not data:
        return jsonify({
            "code": 400,
            "message": "请求体必须是 JSON"
        }), 400

    user_id = data.get("user_id")
    new_username = data.get("new_username", "").strip()

    if not user_id or not isinstance(user_id, int):
        return jsonify({
            "code": 400,
            "message": "缺少有效的 user_id"
        }), 400

    if not new_username:
        return jsonify({
            "code": 400,
            "message": "新用户名不能为空"
        }), 400

    success, msg = change_username(user_id, new_username)

    if success:
        # 返回更新后的用户信息（可选）
        user = get_user_by_id(user_id)
        return jsonify({
            "code": 200,
            "message": msg,
            "data": {
                "user_id": user.user_id,
                "username": user.username,
                "real_name": user.real_name,
                "role": user.role.value,
                "college_id": user.college_id
            }
        }), 200
    else:
        return jsonify({
            "code": 400,
            "message": msg
        }), 400

# ===== 修改密码 API =====
@blueprint.route("/api/change-password", methods=["PUT"])
def change_password_api():
    data = request.get_json()
    if not data:
        return jsonify({
            "code": 400,
            "message": "请求体必须是 JSON"
        }), 400

    user_id = data.get("user_id")
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not user_id or not isinstance(user_id, int):
        return jsonify({
            "code": 400,
            "message": "缺少有效的 user_id"
        }), 400

    if not old_password or not new_password:
        return jsonify({
            "code": 400,
            "message": "当前密码和新密码均不能为空"
        }), 400

    success, msg = change_password(user_id, old_password, new_password)

    if success:
        return jsonify({
            "code": 200,
            "message": msg
        }), 200
    else:
        return jsonify({
            "code": 400,
            "message": msg
        }), 400





#****新增代码*******
# ===== 搜索API =====
@blueprint.route("/api/search", methods=["GET"])
def search_api():
    """
    搜索论文API
    支持参数：
    - title: 论文标题
    - author: 作者姓名
    - category: 分类代码或名称
    - doi: DOI标识符
    - date_after: 发布日期之后 (YYYY-MM-DD)
    """
    try:
        # 获取搜索参数
        search_params = {
            'title': request.args.get('title', '').strip(),
            #'author': request.args.get('author', '').strip(),
            'category': request.args.get('category', '').strip(),
            'doi': request.args.get('doi', '').strip(),
            #'date_after': request.args.get('date_after', '').strip(),
        }
        
        # 移除空值参数
        search_params = {k: v for k, v in search_params.items() if v}
        
        # 如果没有搜索条件，返回空结果
        if not search_params:
            return jsonify([])
        
        # 执行搜索
        papers = search_papers_by_params(search_params)
        
        # 转换为字典格式
        papers_data = [paper.to_dict() for paper in papers]
        
        # 直接返回数组
        return jsonify(papers_data)
        
    except Exception as e:
        current_app.logger.error(f"搜索失败: {e}")
        # 错误时返回空数组，避免前端出错
        return jsonify([])



# ===== 详细搜索API =====
@blueprint.route("/api/search/detailed", methods=["GET"])
def search_detailed_api():
    """
    详细搜索API
    """
    try:
        # 获取搜索参数
        search_params = {
            'title': request.args.get('title', '').strip(),
            'author': request.args.get('author', '').strip(),
            'category': request.args.get('category', '').strip(),
            'doi': request.args.get('doi', '').strip(),
            'date_after': request.args.get('date_after', '').strip(),
        }
        
        # 移除空值参数
        search_params = {k: v for k, v in search_params.items() if v}
        
        # 如果没有搜索条件，返回空结果
        if not search_params:
            return jsonify([])
        
        # 执行搜索
        papers = search_papers_by_params(search_params)
        
        # 为每篇论文添加作者信息
        papers_data = []
        for paper in papers:
            paper_detail = get_paper_with_authors(paper.paper_id)
            if paper_detail:
                papers_data.append(paper_detail)
        
        # 直接返回数组
        return jsonify(papers_data)
        
    except Exception as e:
        current_app.logger.error(f"详细搜索失败: {e}")
        # 错误时返回空数组
        return jsonify([])

# ===== 获取论文详情API =====
@blueprint.route("/api/paper/<int:paper_id>", methods=["GET"])
def get_paper_detail(paper_id):
    """
    获取论文详细信息（包含作者）
    """
    try:
        paper_detail = get_paper_with_authors(paper_id)
        
        if not paper_detail:
            return jsonify({"error": "论文不存在"}), 404
        
        # 直接返回论文对象
        return jsonify(paper_detail)
        
    except Exception as e:
        current_app.logger.error(f"获取论文详情失败: {e}")
        return jsonify({"error": "获取论文详情失败"}), 500




@blueprint.route("/api/record-paper-click", methods=["POST"])
def record_paper_click():
    """
    记录用户点击论文的行为 - 完全避免时区问题的版本
    """
    try:
        data = request.get_json()
        
        # 基本参数验证
        if not data:
            return jsonify({"success": False, "message": "请求数据不能为空"}), 400
        
        user_id = data.get('user_id')
        paper_id = data.get('paper_id')
        college_id = data.get('college_id')
        
        if not all([user_id, paper_id, college_id]):
            return jsonify({"success": False, "message": "user_id、paper_id 和 college_id 为必填参数"}), 400
        
        # 验证数据存在性
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "message": "用户不存在"}), 404
        
        paper = Paper.query.get(paper_id)
        if not paper:
            return jsonify({"success": False, "message": "论文不存在"}), 404
        
        college = College.query.get(college_id)
        if not college:
            return jsonify({"success": False, "message": "学院不存在"}), 404
        
        if user.college_id != college_id:
            return jsonify({"success": False, "message": "用户不属于指定的学院"}), 400
        
        # 完全忽略前端发送的时间，始终使用服务器当前时间
        current_time = datetime.utcnow()
        
        # 简单的重复检查：2分钟内同一用户对同一论文的点击算作一次
        time_threshold = current_time - timedelta(minutes=1)
        
        existing_click = PaperClick.query.filter(
            PaperClick.user_id == user_id,
            PaperClick.paper_id == paper_id,
            PaperClick.college_id == college_id,
            PaperClick.click_time >= time_threshold
        ).order_by(PaperClick.click_time.desc()).first()
        
        if existing_click:
            return jsonify({
                "success": True,
                "message": "点击已记录（避免重复点击）",
                "data": {
                    "click_id": existing_click.click_id,
                    "user_id": user_id,
                    "paper_id": paper_id,
                    "college_id": college_id,
                    "click_time": existing_click.click_time.isoformat() + 'Z'
                }
            }), 200
        
        # 创建新的点击记录
        click_record = PaperClick(
            user_id=user_id,
            paper_id=paper_id,
            college_id=college_id,
            click_time=current_time
        )
        
        db.session.add(click_record)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "点击记录保存成功",
            "data": {
                "click_id": click_record.click_id,
                "user_id": user_id,
                "paper_id": paper_id,
                "college_id": college_id,
                "click_time": current_time.isoformat() + 'Z'
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"记录点击行为错误: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        
        return jsonify({
            "success": False,
            "message": "服务器内部错误，请稍后重试"
        }), 500
 
>>>>>>> Stashed changes
