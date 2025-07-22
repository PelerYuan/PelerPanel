"""
卡片管理API接口
处理卡片的增删改查操作
"""

from flask import jsonify, request
from . import api_bp, get_card_service, get_auth_service
from .utils import (
    success_response,
    error_response,
    validate_json_request,
    validate_query_params,
    handle_api_errors,
    require_json,
    paginate_data
)
from app.services import require_admin_auth


@api_bp.route('/cards', methods=['GET'])
@handle_api_errors
def get_cards():
    """
    获取卡片列表

    GET /api/cards?search=关键词&page=1&per_page=20

    Returns:
        JSON: 卡片列表和分页信息
    """
    card_service = get_card_service()
    if not card_service:
        return jsonify(error_response("卡片服务未初始化", "service_error")[0]), 500

    # 验证查询参数
    try:
        params = validate_query_params({
            'search': {
                'type': str,
                'required': False,
                'default': None
            },
            'page': {
                'type': int,
                'required': False,
                'default': 1
            },
            'per_page': {
                'type': int,
                'required': False,
                'default': 20
            }
        })
    except ValueError as e:
        return jsonify(error_response(str(e), "validation_error")[0]), 400

    # 验证分页参数
    if params['page'] < 1:
        return jsonify(error_response("页码必须大于0", "validation_error")[0]), 400

    if params['per_page'] < 1 or params['per_page'] > 100:
        return jsonify(error_response("每页数量必须在1-100之间", "validation_error")[0]), 400

    # 获取卡片列表
    cards = card_service.get_all_cards(search_query=params['search'])

    # 转换为字典格式
    cards_data = [card.to_dict() for card in cards]

    # 分页处理
    if params['per_page'] and len(cards_data) > params['per_page']:
        paginated_data = paginate_data(cards_data, params['page'], params['per_page'])
        return jsonify(success_response(
            data=paginated_data,
            message=f"获取卡片列表成功，共{len(cards_data)}张卡片"
        ))

    else:
        # 不分页，返回所有数据
        return jsonify(success_response(
            data={
                'items': cards_data,
                'total': len(cards_data)
            },
            message=f"获取卡片列表成功，共{len(cards_data)}张卡片"
        ))


@api_bp.route('/cards', methods=['POST'])
@handle_api_errors
@require_json
@require_admin_auth
def create_card():
    """
    创建新卡片

    POST /api/cards
    {
        "name": "卡片名称",
        "icon": "bi-server",
        "url": "http://example.com",
        "description": "描述信息"
    }

    Returns:
        JSON: 创建的卡片信息
    """
    card_service = get_card_service()
    if not card_service:
        return jsonify(error_response("卡片服务未初始化", "service_error")[0]), 500

    # 验证请求数据
    data = validate_json_request(
        required_fields=['name', 'icon', 'url'],
        optional_fields=['description']
    )

    # 设置默认值
    description = data.get('description', '')

    # 创建卡片
    success, message, new_card = card_service.create_card(
        name=data['name'],
        icon=data['icon'],
        url=data['url'],
        description=description
    )

    if success:
        return jsonify(success_response(
            data=new_card.to_dict(),
            message=message
        )), 201  # Created
    else:
        # 根据错误类型返回不同状态码
        if "已存在" in message:
            error_code = "name_already_exists"
            status_code = 409  # Conflict
        else:
            error_code = "creation_failed"
            status_code = 400  # Bad Request

        return jsonify(error_response(message, error_code)[0]), status_code


@api_bp.route('/cards/<card_id>', methods=['GET'])
@handle_api_errors
def get_card(card_id):
    """
    获取单个卡片

    GET /api/cards/<card_id>

    Returns:
        JSON: 卡片信息
    """
    card_service = get_card_service()
    if not card_service:
        return jsonify(error_response("卡片服务未初始化", "service_error")[0]), 500

    # 获取卡片
    card = card_service.get_card_by_id(card_id)

    if card:
        return jsonify(success_response(
            data=card.to_dict(),
            message="卡片获取成功"
        ))
    else:
        return jsonify(error_response("卡片不存在", "not_found")[0]), 404


@api_bp.route('/cards/<card_id>', methods=['PUT'])
@handle_api_errors
@require_json
@require_admin_auth
def update_card(card_id):
    """
    更新卡片

    PUT /api/cards/<card_id>
    {
        "name": "新名称",
        "icon": "bi-new-icon",
        "url": "http://new-url.com",
        "description": "新描述"
    }

    Returns:
        JSON: 更新后的卡片信息
    """
    card_service = get_card_service()
    if not card_service:
        return jsonify(error_response("卡片服务未初始化", "service_error")[0]), 500

    # 验证请求数据
    data = validate_json_request(
        optional_fields=['name', 'icon', 'url', 'description']
    )

    if not data:
        return jsonify(error_response("没有要更新的内容", "validation_error")[0]), 400

    # 更新卡片
    success, message, updated_card = card_service.update_card(
        card_id=card_id,
        **data
    )

    if success:
        return jsonify(success_response(
            data=updated_card.to_dict(),
            message=message
        ))
    else:
        # 根据错误类型返回不同状态码
        if "不存在" in message:
            status_code = 404  # Not Found
        elif "已存在" in message:
            status_code = 409  # Conflict
        else:
            status_code = 400  # Bad Request

        return jsonify(error_response(message, "update_failed")[0]), status_code


@api_bp.route('/cards/<card_id>', methods=['DELETE'])
@handle_api_errors
@require_admin_auth
def delete_card(card_id):
    """
    删除卡片

    DELETE /api/cards/<card_id>

    Returns:
        JSON: 删除结果
    """
    card_service = get_card_service()
    if not card_service:
        return jsonify(error_response("卡片服务未初始化", "service_error")[0]), 500

    # 删除卡片
    success, message = card_service.delete_card(card_id)

    if success:
        return jsonify(success_response(message=message))
    else:
        # 根据错误类型返回不同状态码
        if "不存在" in message:
            status_code = 404  # Not Found
        else:
            status_code = 400  # Bad Request

        return jsonify(error_response(message, "delete_failed")[0]), status_code


@api_bp.route('/cards/reorder', methods=['POST'])
@handle_api_errors
@require_json
@require_admin_auth
def reorder_cards():
    """
    重新排序卡片

    POST /api/cards/reorder
    {
        "orders": [
            {"id": "card_id_1", "order": 1},
            {"id": "card_id_2", "order": 2}
        ]
    }

    Returns:
        JSON: 排序结果
    """
    card_service = get_card_service()
    if not card_service:
        return jsonify(error_response("卡片服务未初始化", "service_error")[0]), 500

    # 验证请求数据
    data = validate_json_request(required_fields=['orders'])

    orders = data['orders']

    # 验证orders数据格式
    if not isinstance(orders, list):
        return jsonify(error_response("orders必须是数组格式", "validation_error")[0]), 400

    if not orders:
        return jsonify(error_response("orders不能为空", "validation_error")[0]), 400

    # 验证每个排序项的格式
    for i, item in enumerate(orders):
        if not isinstance(item, dict):
            return jsonify(error_response(f"orders[{i}]必须是对象格式", "validation_error")[0]), 400

        if 'id' not in item or 'order' not in item:
            return jsonify(error_response(f"orders[{i}]必须包含id和order字段", "validation_error")[0]), 400

        if not isinstance(item['order'], int) or item['order'] < 1:
            return jsonify(error_response(f"orders[{i}].order必须是大于0的整数", "validation_error")[0]), 400

    # 重新排序
    success, message = card_service.reorder_cards(orders)

    if success:
        return jsonify(success_response(message=message))
    else:
        return jsonify(error_response(message, "reorder_failed")[0]), 400