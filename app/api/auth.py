"""
认证相关API接口
处理管理员登录、退出等认证操作
"""

from flask import jsonify, request
from . import api_bp, get_auth_service
from .utils import (
    success_response,
    error_response,
    validate_json_request,
    handle_api_errors,
    require_json,
    get_client_ip
)


@api_bp.route('/auth', methods=['POST'])
@handle_api_errors
@require_json
def login():
    """
    管理员密码验证

    POST /api/auth
    {
        "password": "admin_password"
    }

    Returns:
        JSON: 认证结果
    """
    auth_service = get_auth_service()
    if not auth_service:
        return jsonify(error_response("认证服务未初始化", "service_error")[0]), 500

    # 验证请求数据
    data = validate_json_request(required_fields=['password'])
    password = data['password']

    # 获取客户端IP
    client_ip = get_client_ip()

    # 执行认证
    success, message, extra_info = auth_service.authenticate(password, client_ip)

    if success:
        # 认证成功
        response_data = {
            'authenticated': True,
            'session_type': extra_info.get('session_expires', 'browser_close')
        }
        return jsonify(success_response(response_data, message))

    else:
        # 认证失败
        error_code = "authentication_failed"

        # 根据失败原因返回不同的错误码和状态码
        if extra_info.get('locked', False):
            error_code = "account_locked"
            status_code = 429  # Too Many Requests
        else:
            status_code = 401  # Unauthorized

        return jsonify(error_response(
            message=message,
            error_code=error_code,
            details=extra_info
        )[0]), status_code


@api_bp.route('/logout', methods=['POST'])
@handle_api_errors
def logout():
    """
    退出登录

    POST /api/logout

    Returns:
        JSON: 退出结果
    """
    auth_service = get_auth_service()
    if not auth_service:
        return jsonify(error_response("认证服务未初始化", "service_error")[0]), 500

    # 执行退出
    success, message = auth_service.logout()

    if success:
        return jsonify(success_response(message=message))
    else:
        return jsonify(error_response(message, "logout_failed")[0]), 400


@api_bp.route('/auth/status', methods=['GET'])
@handle_api_errors
def auth_status():
    """
    获取认证状态

    GET /api/auth/status

    Returns:
        JSON: 认证状态信息
    """
    auth_service = get_auth_service()
    if not auth_service:
        return jsonify(error_response("认证服务未初始化", "service_error")[0]), 500

    # 获取认证信息
    auth_info = auth_service.get_auth_info()

    return jsonify(success_response(auth_info, "认证状态获取成功"))


@api_bp.route('/auth/security', methods=['GET'])
@handle_api_errors
def security_info():
    """
    获取安全信息（失败尝试次数等）

    GET /api/auth/security

    Returns:
        JSON: 安全状态信息
    """
    auth_service = get_auth_service()
    if not auth_service:
        return jsonify(error_response("认证服务未初始化", "service_error")[0]), 500

    # 获取客户端IP
    client_ip = get_client_ip()

    # 获取安全信息
    security_info = auth_service.get_security_info(client_ip)

    return jsonify(success_response(security_info, "安全信息获取成功"))