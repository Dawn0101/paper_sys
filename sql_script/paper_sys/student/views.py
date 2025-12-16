# student/views.py
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from .repositories import (
    get_student_click_history,
    delete_click_record,
    get_paper_category_stats,
    get_paper_year_stats
)

blueprint = Blueprint("student", __name__, url_prefix="/student")

@blueprint.route("/api/click-history", methods=["GET"])
@login_required
def get_click_history():
    """获取学生的浏览记录"""
    try:
        history = get_student_click_history(current_user.user_id)
        return jsonify({
            "code": 200,
            "message": "获取浏览记录成功",
            "data": [item.to_dict() for item in history]
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取浏览记录失败: {e}")
        return jsonify({
            "code": 500,
            "message": "获取浏览记录失败"
        }), 500

@blueprint.route("/api/click-history/<int:click_id>", methods=["DELETE"])
@login_required
def delete_history(click_id):
    """删除特定浏览记录"""
    try:
        success = delete_click_record(click_id, current_user.user_id)
        if success:
            return jsonify({
                "code": 200,
                "message": "删除记录成功"
            }), 200
        return jsonify({
            "code": 404,
            "message": "记录不存在"
        }), 404
    except Exception as e:
        current_app.logger.error(f"删除记录失败: {e}")
        return jsonify({
            "code": 500,
            "message": "删除记录失败"
        }), 500

@blueprint.route("/api/stats/category", methods=["GET"])
@login_required
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
            "message": "获取分类统计失败"
        }), 500

@blueprint.route("/api/stats/year", methods=["GET"])
@login_required
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
            "message": "获取年份统计失败"
        }), 500