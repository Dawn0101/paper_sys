# student/views.py
from flask import Blueprint, request, jsonify, current_app
from .repositories import (
    get_student_click_history,
    delete_click_record,
    get_paper_category_stats,
    get_paper_year_stats
)

blueprint = Blueprint("student", __name__, url_prefix="/student")


@blueprint.route("/api/click-history", methods=["GET"])
def get_click_history():
    """获取学生的浏览记录"""
    try:
        # 从请求参数获取用户ID
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                "code": 400,
                "message": "缺少用户ID参数"
            }), 400

        # 验证用户ID是数字
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
        # 从请求参数获取用户ID
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                "code": 400,
                "message": "缺少用户ID参数"
            }), 400

        # 验证用户ID是数字
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