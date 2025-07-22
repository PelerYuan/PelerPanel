"""
工具API接口
提供图标列表、名称验证等辅助功能
"""

from flask import jsonify
from . import api_bp, get_card_service
from .utils import (
    success_response,
    error_response,
    validate_json_request,
    validate_query_params,
    handle_api_errors,
    require_json
)


@api_bp.route('/icons', methods=['GET'])
@handle_api_errors
def get_icons():
    """
    获取可用图标列表

    GET /api/icons?search=关键词&category=分类

    Returns:
        JSON: 图标列表
    """
    # 验证查询参数
    try:
        params = validate_query_params({
            'search': {
                'type': str,
                'required': False,
                'default': None
            },
            'category': {
                'type': str,
                'required': False,
                'default': None
            }
        })
    except ValueError as e:
        return jsonify(error_response(str(e), "validation_error")[0]), 400

    # Bootstrap Icons 常用图标列表
    # 这里提供一个预定义的图标列表，实际使用时可以从Bootstrap Icons CDN获取
    icons_data = {
        "system": [
            {"name": "bi-server", "description": "服务器"},
            {"name": "bi-database", "description": "数据库"},
            {"name": "bi-hdd", "description": "硬盘"},
            {"name": "bi-cpu", "description": "处理器"},
            {"name": "bi-memory", "description": "内存"},
            {"name": "bi-router", "description": "路由器"},
            {"name": "bi-wifi", "description": "无线网络"}
        ],
        "monitoring": [
            {"name": "bi-activity", "description": "活动监控"},
            {"name": "bi-graph-up", "description": "图表上升"},
            {"name": "bi-graph-down", "description": "图表下降"},
            {"name": "bi-speedometer", "description": "速度计"},
            {"name": "bi-bar-chart", "description": "柱状图"},
            {"name": "bi-pie-chart", "description": "饼图"},
            {"name": "bi-eye", "description": "监控眼"}
        ],
        "storage": [
            {"name": "bi-folder", "description": "文件夹"},
            {"name": "bi-file", "description": "文件"},
            {"name": "bi-cloud", "description": "云存储"},
            {"name": "bi-archive", "description": "归档"},
            {"name": "bi-box", "description": "容器"},
            {"name": "bi-collection", "description": "集合"}
        ],
        "development": [
            {"name": "bi-github", "description": "GitHub"},
            {"name": "bi-git", "description": "Git"},
            {"name": "bi-code", "description": "代码"},
            {"name": "bi-terminal", "description": "终端"},
            {"name": "bi-bug", "description": "调试"},
            {"name": "bi-tools", "description": "工具"}
        ],
        "network": [
            {"name": "bi-globe", "description": "全球网络"},
            {"name": "bi-share", "description": "共享"},
            {"name": "bi-link", "description": "链接"},
            {"name": "bi-ethernet", "description": "以太网"},
            {"name": "bi-proxy", "description": "代理"}
        ],
        "security": [
            {"name": "bi-shield", "description": "安全防护"},
            {"name": "bi-lock", "description": "锁定"},
            {"name": "bi-unlock", "description": "解锁"},
            {"name": "bi-key", "description": "密钥"},
            {"name": "bi-person-check", "description": "用户验证"}
        ],
        "media": [
            {"name": "bi-camera", "description": "摄像头"},
            {"name": "bi-film", "description": "视频"},
            {"name": "bi-music-note", "description": "音乐"},
            {"name": "bi-image", "description": "图片"},
            {"name": "bi-play", "description": "播放"},
            {"name": "bi-cast", "description": "投屏"}
        ],
        "communication": [
            {"name": "bi-chat", "description": "聊天"},
            {"name": "bi-envelope", "description": "邮件"},
            {"name": "bi-telephone", "description": "电话"},
            {"name": "bi-broadcast", "description": "广播"},
            {"name": "bi-megaphone", "description": "扩音器"}
        ],
        "general": [
            {"name": "bi-gear", "description": "设置"},
            {"name": "bi-house", "description": "主页"},
            {"name": "bi-star", "description": "收藏"},
            {"name": "bi-heart", "description": "喜爱"},
            {"name": "bi-bookmark", "description": "书签"},
            {"name": "bi-flag", "description": "标记"},
            {"name": "bi-lightning", "description": "闪电"},
            {"name": "bi-fire", "description": "火焰"}
        ]
    }

    # 处理搜索和分类过滤
    filtered_icons = {}

    for category, icons in icons_data.items():
        # 分类过滤
        if params['category'] and params['category'] != category:
            continue

        # 搜索过滤
        if params['search']:
            search_term = params['search'].lower()
            filtered_category_icons = [
                icon for icon in icons
                if (search_term in icon['name'].lower() or
                    search_term in icon['description'].lower())
            ]
        else:
            filtered_category_icons = icons

        if filtered_category_icons:
            filtered_icons[category] = filtered_category_icons

    # 统计图标数量
    total_count = sum(len(icons) for icons in filtered_icons.values())

    response_data = {
        "categories": filtered_icons,
        "total_count": total_count,
        "search_query": params['search'],
        "category_filter": params['category']
    }

    return jsonify(success_response(
        data=response_data,
        message=f"获取图标列表成功，共{total_count}个图标"
    ))


@api_bp.route('/validate-name', methods=['POST'])
@handle_api_errors
@require_json
def validate_name():
    """
    验证卡片名称唯一性

    POST /api/validate-name
    {
        "name": "要验证的名称",
        "exclude_id": "排除的卡片ID（可选）"
    }

    Returns:
        JSON: 验证结果
    """
    card_service = get_card_service()
    if not card_service:
        return jsonify(error_response("卡片服务未初始化", "service_error")[0]), 500

    # 验证请求数据
    data = validate_json_request(
        required_fields=['name'],
        optional_fields=['exclude_id']
    )

    name = data['name']
    exclude_id = data.get('exclude_id')

    # 验证名称
    is_valid, message = card_service.validate_name(name, exclude_id)

    response_data = {
        "name": name,
        "is_valid": is_valid,
        "message": message
    }

    if is_valid:
        return jsonify(success_response(
            data=response_data,
            message="名称验证通过"
        ))
    else:
        return jsonify(success_response(
            data=response_data,
            message="名称验证未通过"
        ))


@api_bp.route('/stats', methods=['GET'])
@handle_api_errors
def get_stats():
    """
    获取系统统计信息

    GET /api/stats

    Returns:
        JSON: 统计信息
    """
    card_service = get_card_service()
    if not card_service:
        return jsonify(error_response("卡片服务未初始化", "service_error")[0]), 500

    # 获取服务统计信息
    stats = card_service.get_service_stats()

    # 添加API相关统计
    api_stats = {
        "api_version": "1.0.0",
        "endpoints_count": 15,  # 当前API接口数量
        "supported_methods": ["GET", "POST", "PUT", "DELETE"]
    }

    response_data = {
        "service": stats,
        "api": api_stats
    }

    return jsonify(success_response(
        data=response_data,
        message="统计信息获取成功"
    ))