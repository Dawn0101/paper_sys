from flask import Flask,Blueprint, request, jsonify, current_app
import base64
import json
from .repositories import (
    get_student_click_history,
    delete_click_record,
    get_paper_category_stats,
    get_paper_year_stats,
    get_click_stats_by_college,
    get_students_by_college,
    reset_password_for_students,
    delete_student_user,
    get_student_by_id,
    create_student,
    update_student,
    get_papers,
    get_paper_by_id,
    create_paper,
    update_paper,
    delete_paper,
    get_all_categories,
    get_dashboard_stats
)
import json

app = Flask(__name__)

blueprint = Blueprint("college_admin", __name__, url_prefix="/college_admin")

# 原有的无需登录的API保持不变
@blueprint.route("/api/click-history", methods=["GET"])
def get_click_history():
    """获取学生的浏览记录"""
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

@blueprint.route("/api/stats/click_history/<int:college_id>", methods=["GET"])
def get_click_stats(college_id):
    """获取特定学院的学生点击统计（排行）"""
    try:
        # 调用统计函数
        stats = get_click_stats_by_college(college_id)
        return jsonify({
            "code": 200,
            "message": "获取点击统计成功",
            "data": stats
        }), 200
    except Exception as e:
        current_app.logger.error(f"接口返回学院点击统计失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"获取点击统计失败: {str(e)}"
        }), 500

@blueprint.route("/api/students", methods=["GET"])
def get_students():
    """获取学生列表（按学院筛选，支持分页+搜索）"""
    try:
        # ========== 1. 必传参数校验 ==========
        # （关键）获取管理员所属学院ID（需根据实际登录机制调整，比如从token/session获取）
        # 示例：假设前端请求头传递college_id，或从管理员登录信息中获取
        college_id = request.args.get('college_id')  # 或从token解析：current_user.college_id
        if not college_id:
            return jsonify({
                "code": 400,
                "message": "缺少学院ID参数（college_id）"
            }), 400
        try:
            college_id = int(college_id)
        except ValueError:
            return jsonify({
                "code": 400,
                "message": "学院ID必须为整数"
            }), 400

        # ========== 2. 分页/搜索参数 ==========
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '').strip()

        # ========== 3. 调用真实查询函数 ==========
        try:
            # 调用get_students_by_college执行数据库查询
            result = get_students_by_college(
                college_id=college_id,
                page=page,
                per_page=per_page,
                search=search
            )
        except Exception as e:
            logger.error(f"查询学院[{college_id}]学生失败: {str(e)}")
            return jsonify({
                "code": 500,
                "message": f"数据库查询失败: {str(e)}"
            }), 500

        # ========== 4. 序列化结果（关键：SQLAlchemy对象转字典） ==========
        # 将User对象转换为前端可解析的字典（需确保User模型有to_dict方法）
        students_list = [student.to_dict() for student in result["students"]]

        # ========== 5. 构造返回格式 ==========
        return jsonify({
            "code": 200,
            "message": "获取学生列表成功",
            "data": {
                "students": students_list,       # 序列化后的学生列表
                "stats": result["stats"],        # 统计信息（今日活跃/总浏览数）
                "pages": result["pages"],        # 总页数
                "total": result["total"],        # 总学生数
                "page": result["page"],          # 当前页
                "per_page": result["per_page"]   # 每页条数
            }
        }), 200

    except Exception as e:
        logger.error(f"获取学生列表接口异常: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}"
        }), 500

@blueprint.route("/api/students", methods=["POST"])
def add_student():
    """添加新学生"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['username', 'real_name', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "code": 400,
                    "message": f"缺少必填字段: {field}"
                }), 400
        
        # 创建学生（移除学院ID关联）
        student, error = create_student(
            username=data['username'],
            real_name=data['real_name'],
            password=data['password'],
            college_id=data.get('college_id', 0)  # 改为手动传入或默认值
        )
        
        if error:
            return jsonify({
                "code": 400,
                "message": error
            }), 400
        
        return jsonify({
            "code": 200,
            "message": "学生添加成功",
            "data": student.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"添加学生失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"添加学生失败: {str(e)}"
        }), 500

@blueprint.route("/api/students/<int:user_id>", methods=["PUT"])
def update_student_info(user_id):
    """更新学生信息"""
    try:
        data = request.get_json()
        
        # 检查学生是否存在（移除学院ID校验）
        student = get_student_by_id(user_id)
        if not student:
            return jsonify({
                "code": 404,
                "message": "学生不存在"
            }), 404
        
        # 更新学生信息（移除学院ID关联）
        success, error = update_student(
            student_id=user_id,
            real_name=data.get('real_name'),
            password=data.get('password')
        )
        
        if error:
            return jsonify({
                "code": 400,
                "message": error
            }), 400
        
        return jsonify({
            "code": 200,
            "message": "学生信息更新成功",
            "data": student.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"更新学生信息失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"更新学生信息失败: {str(e)}"
        }), 500

@blueprint.route("/api/reset_password/<int:user_id>", methods=["PUT"])
def reset_student_password(user_id):
    """重置学生密码"""
    try:
        success, error = reset_password_for_students(user_id)
        if error:
            return jsonify({
                "code": 400,
                "message": error
            }), 400
            
        if success:
            return jsonify({
                "code": 200,
                "message": "密码重置成功"
            }), 200
        return jsonify({
            "code": 404,
            "message": "操作失败"
        }), 404
    except Exception as e:
        current_app.logger.error(f"密码重置失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"密码重置失败: {str(e)}"
        }), 500

@blueprint.route("/api/delete_student/<int:user_id>", methods=["DELETE"])
def delete_student(user_id):
    """删除学生用户"""
    try:
        success, error = delete_student_user(user_id)
        if error:
            return jsonify({
                "code": 400,
                "message": error
            }), 400
            
        if success:
            return jsonify({
                "code": 200,
                "message": "学生用户删除成功"
            }), 200
        return jsonify({
            "code": 404,
            "message": "操作失败"
        }), 404
    except Exception as e:
        current_app.logger.error(f"删除学生用户失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"删除学生用户失败: {str(e)}"
        }), 500

# 论文管理相关API
@blueprint.route("/api/papers", methods=["GET"])
def get_papers_list():
    """获取论文列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        category_id = request.args.get('category_id', type=int)
        
        # 获取论文数据
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
        # 检查论文是否存在
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

# 分类管理API
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

# 仪表板统计API
@blueprint.route("/api/stats/dashboard", methods=["GET"])
def get_dashboard_statistics():
    """获取仪表板统计数据"""
    try:
        # 移除学院ID关联，如需按学院查询可通过参数传入
        stats = get_dashboard_stats()
        return jsonify({
            "code": 200,
            "message": "获取统计数据成功",
            "data": stats
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取统计数据失败: {e}")
        return jsonify({
            "code": 500,
            "message": f"获取统计数据失败: {str(e)}"
        }), 500
