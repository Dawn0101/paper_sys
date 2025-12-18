# university_admin/views.py
from flask import Blueprint, request, jsonify, current_app
from .repositories import (
    get_all_users,
    get_user_by_id,
    update_user,
    delete_user,
    get_college_click_stats,
    get_student_click_history,
    delete_click_record,
    get_papers,
    get_paper_by_id,
    create_paper,
    update_paper,
    delete_paper,
    get_all_categories,
    get_all_colleges,
    get_paper_category_stats,
    get_paper_year_stats,
    get_click_stats_by_college
)

blueprint = Blueprint("university_admin", __name__, url_prefix="/university_admin")

# ========== 浏览记录相关API ==========
@blueprint.route("/api/click-history", methods=["GET"])
def get_click_history():
    """获取用户的浏览记录"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                "code": 400,
                "message": "缺少用户ID参数"
            }), 400

        try:
            user_id_int = int(user_id)
        except ValueError:
            return jsonify({
                "code": 400,
                "message": "用户ID格式错误"
            }), 400

        history = get_student_click_history(user_id_int)
        return jsonify({
            "code": 200,
            "message": "获取浏览记录成功",
            "data": [item.to_dict() for item in history]
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取浏览记录失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"获取浏览记录失败: {str(e)}"
        }), 500

@blueprint.route("/api/click-history/<int:click_id>", methods=["DELETE"])
def delete_history(click_id):
    """删除特定浏览记录"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                "code": 400,
                "message": "缺少用户ID参数"
            }), 400

        try:
            user_id_int = int(user_id)
        except ValueError:
            return jsonify({
                "code": 400,
                "message": "用户ID格式错误"
            }), 400

        success = delete_click_record(click_id, user_id_int)
        if success:
            return jsonify({
                "code": 200,
                "message": "删除记录成功"
            }), 200
        return jsonify({
            "code": 404,
            "message": "记录不存在或无权限删除"
        }), 404
    except Exception as e:
        current_app.logger.error(f"删除记录失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"删除记录失败: {str(e)}"
        }), 500

# ========== 用户管理相关API ==========
@blueprint.route("/api/users", methods=["GET"])
def get_users():
    """获取所有用户列表（支持分页、搜索、角色筛选、学院筛选）"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        search = request.args.get('search', '').strip()
        role = request.args.get('role')  # STUDENT, COLLEGE_ADMIN, UNIVERSITY_ADMIN
        college_id = request.args.get('college_id', type=int)
        
        result = get_all_users(
            page=page,
            per_page=per_page,
            search=search,
            role=role,
            college_id=college_id
        )
        
        # 处理用户数据，添加学院名称
        users_data = []
        for user in result["users"]:
            user_dict = user.to_dict()
            # 添加学院名称
            if user_dict.get("college") and isinstance(user_dict["college"], dict):
                user_dict["college_name"] = user_dict["college"].get("college_name", "")
            elif user.college:
                user_dict["college_name"] = user.college.college_name
            else:
                user_dict["college_name"] = ""
            users_data.append(user_dict)
        
        return jsonify({
            "code": 200,
            "message": "获取用户列表成功",
            "data": {
                "users": users_data,
                "total": result["total"],
                "page": result["page"],
                "per_page": result["per_page"],
                "pages": result["pages"]
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取用户列表失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"获取用户列表失败: {str(e)}"
        }), 500

@blueprint.route("/api/users/<int:user_id>", methods=["GET"])
def get_user_info(user_id):
    """获取单个用户信息"""
    try:
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({
                "code": 404,
                "message": "用户不存在"
            }), 404
        
        return jsonify({
            "code": 200,
            "message": "获取用户信息成功",
            "data": user.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取用户信息失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"获取用户信息失败: {str(e)}"
        }), 500

@blueprint.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user_info(user_id):
    """更新用户信息（包括用户名、真实姓名、密码、角色、学院）"""
    try:
        data = request.get_json()
        
        # 检查用户是否存在
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({
                "code": 404,
                "message": "用户不存在"
            }), 404
        
        # 验证密码长度（如果提供了密码）
        password = data.get('password')
        if password and len(password) < 6:
            return jsonify({
                "code": 400,
                "message": "密码长度不能小于6位"
            }), 400
        
        # 更新用户信息
        success, error = update_user(
            user_id=user_id,
            username=data.get('username'),
            real_name=data.get('real_name'),
            password=password,
            role=data.get('role'),
            college_id=data.get('college_id')
        )
        
        if error:
            return jsonify({
                "code": 400,
                "message": error
            }), 400
        
        # 重新获取更新后的用户信息
        updated_user = get_user_by_id(user_id)
        return jsonify({
            "code": 200,
            "message": "用户信息更新成功",
            "data": updated_user.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"更新用户信息失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"更新用户信息失败: {str(e)}"
        }), 500

@blueprint.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user_by_id(user_id):
    """删除用户"""
    try:
        success, error = delete_user(user_id)
        if error:
            return jsonify({
                "code": 400,
                "message": error
            }), 400
        
        if success:
            return jsonify({
                "code": 200,
                "message": "用户删除成功"
            }), 200
        return jsonify({
            "code": 404,
            "message": "操作失败"
        }), 404
    except Exception as e:
        current_app.logger.error(f"删除用户失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"删除用户失败: {str(e)}"
        }), 500

# ========== 论文管理相关API ==========
@blueprint.route("/api/papers", methods=["GET"])
def get_papers_list():
    """获取论文列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        category_id = request.args.get('category_id', type=int)
        
        result = get_papers(
            page=page,
            per_page=per_page,
            search=search,
            category_id=category_id
        )
        
        return jsonify({
            "code": 200,
            "message": "获取论文列表成功",
            "data": {
                "papers": result["papers"],
                "total": result["total"],
                "page": result["page"],
                "per_page": result["per_page"],
                "pages": result["pages"],
                "stats": result["stats"]
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取论文列表失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"获取论文列表失败: {str(e)}"
        }), 500

@blueprint.route("/api/papers", methods=["POST"])
def add_paper():
    """添加新论文"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['title', 'arxiv_id', 'category_id', 'pdf_url']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "code": 400,
                    "message": f"缺少必填字段: {field}"
                }), 400
        
        # 创建论文
        paper, error = create_paper(
            title=data['title'],
            arxiv_id=data['arxiv_id'],
            category_id=data['category_id'],
            pdf_url=data['pdf_url'],
            doi=data.get('doi'),
            abstract=data.get('abstract')
        )
        
        if error:
            return jsonify({
                "code": 400,
                "message": error
            }), 400
        
        return jsonify({
            "code": 200,
            "message": "论文添加成功",
            "data": paper.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"添加论文失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"添加论文失败: {str(e)}"
        }), 500

@blueprint.route("/api/papers/<int:paper_id>", methods=["PUT"])
def update_paper_info(paper_id):
    """更新论文信息"""
    try:
        data = request.get_json()
        
        # 检查论文是否存在
        paper = get_paper_by_id(paper_id)
        if not paper:
            return jsonify({
                "code": 404,
                "message": "论文不存在"
            }), 404
        
        # 更新论文信息
        success, error = update_paper(paper_id, **data)
        
        if error:
            return jsonify({
                "code": 400,
                "message": error
            }), 400
        
        return jsonify({
            "code": 200,
            "message": "论文更新成功",
            "data": paper.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"更新论文失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"更新论文失败: {str(e)}"
        }), 500

@blueprint.route("/api/papers/<int:paper_id>", methods=["DELETE"])
def delete_paper_by_id(paper_id):
    """删除论文"""
    try:
        paper = get_paper_by_id(paper_id)
        if not paper:
            return jsonify({
                "code": 404,
                "message": "论文不存在"
            }), 404
        
        success = delete_paper(paper_id)
        if success:
            return jsonify({
                "code": 200,
                "message": "论文删除成功"
            }), 200
        return jsonify({
            "code": 500,
            "message": "论文删除失败"
        }), 500
    except Exception as e:
        current_app.logger.error(f"删除论文失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"删除论文失败: {str(e)}"
        }), 500

# ========== 分类和学院管理API ==========
@blueprint.route("/api/categories", methods=["GET"])
def get_categories_list():
    """获取所有分类"""
    try:
        categories = get_all_categories()
        return jsonify({
            "code": 200,
            "message": "获取分类成功",
            "data": [category.to_dict() for category in categories]
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取分类失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"获取分类失败: {str(e)}"
        }), 500

@blueprint.route("/api/colleges", methods=["GET"])
def get_colleges_list():
    """获取所有学院"""
    try:
        colleges = get_all_colleges()
        return jsonify({
            "code": 200,
            "message": "获取学院列表成功",
            "data": [college.to_dict() for college in colleges]
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取学院列表失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"获取学院列表失败: {str(e)}"
        }), 500

# ========== 统计相关API ==========
@blueprint.route("/api/stats/category", methods=["GET"])
def get_category_stats():
    """获取论文分类统计"""
    try:
        stats = get_paper_category_stats()
        return jsonify({
            "code": 200,
            "message": "获取分类统计成功",
            "data": stats
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取分类统计失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"获取分类统计失败: {str(e)}"
        }), 500

@blueprint.route("/api/stats/year", methods=["GET"])
def get_year_stats():
    """获取论文年份统计"""
    try:
        stats = get_paper_year_stats()
        return jsonify({
            "code": 200,
            "message": "获取年份统计成功",
            "data": stats
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取年份统计失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"获取年份统计失败: {str(e)}"
        }), 500

@blueprint.route("/api/stats/college-clicks", methods=["GET"])
def get_college_clicks_stats():
    """获取各学院总点击量排行"""
    try:
        ranking = get_college_click_stats()
        return jsonify({
            "code": 200,
            "message": "获取学院点击量统计成功",
            "data": ranking
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取学院点击量统计失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"获取学院点击量统计失败: {str(e)}"
        }), 500

@blueprint.route("/api/stats/click_history/<int:college_id>", methods=["GET"])
def get_click_stats(college_id):
    """获取特定学院的学生点击统计（排行）"""
    try:
        stats = get_click_stats_by_college(college_id)
        return jsonify({
            "code": 200,
            "message": "获取点击统计成功",
            "data": stats
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取点击统计失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"获取点击统计失败: {str(e)}"
        }), 500

