"""
API 工具函数
统一的响应格式和验证工具
"""

from typing import Any, Dict, Optional, Tuple
from flask import jsonify, request
from functools import wraps
import json


def success_response(data: Any = None, message: str = "操作成功", **kwargs) -> Dict[str, Any]:
    """
    成功响应格式

    Args:
        data: 返回的数据
        message: 成功消息
        **kwargs: 额外的响应字段

    Returns:
        Dict: 标准成功响应格式
    """
    response = {
        'success': True,
        'message': message,
    }

    if data is not None:
        response['data'] = data

    # 添加额外字段
    response.update(kwargs)

    return response


def error_response(message: str, error_code: str = "error", details: Any = None,
                   status_code: int = 400, **kwargs) -> Tuple[Dict[str, Any], int]:
    """
    错误响应格式

    Args:
        message: 错误消息
        error_code: 错误代码
        details: 详细错误信息
        status_code: HTTP状态码
        **kwargs: 额外的响应字段

    Returns:
        Tuple[Dict, int]: (错误响应字典, HTTP状态码)
    """
    response = {
        'success': False,
        'error': error_code,
        'message': message,
    }

    if details is not None:
        response['details'] = details

    # 添加额外字段
    response.update(kwargs)

    return response, status_code


def validate_json_request(required_fields: list = None, optional_fields: list = None) -> Dict[str, Any]:
    """
    验证JSON请求数据

    Args:
        required_fields: 必填字段列表
        optional_fields: 可选字段列表

    Returns:
        Dict: 验证后的数据

    Raises:
        ValueError: 验证失败时抛出异常
    """
    if not request.is_json:
        raise ValueError("请求必须是JSON格式")

    try:
        data = request.get_json()
    except Exception as e:
        raise ValueError(f"JSON格式错误: {str(e)}")

    if data is None:
        raise ValueError("请求数据为空")

    if not isinstance(data, dict):
        raise ValueError("请求数据必须是对象格式")

    # 检查必填字段
    if required_fields:
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(f"缺少必填字段: {', '.join(missing_fields)}")

    # 过滤允许的字段
    allowed_fields = set()
    if required_fields:
        allowed_fields.update(required_fields)
    if optional_fields:
        allowed_fields.update(optional_fields)

    if allowed_fields:
        filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
        return filtered_data

    return data


def validate_query_params(params_config: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    验证查询参数

    Args:
        params_config: 参数配置字典
            格式: {
                'param_name': {
                    'required': bool,
                    'type': type,
                    'default': any,
                    'choices': list
                }
            }

    Returns:
        Dict: 验证后的参数字典

    Raises:
        ValueError: 验证失败时抛出异常
    """
    result = {}

    for param_name, config in params_config.items():
        value = request.args.get(param_name)

        # 检查必填参数
        if config.get('required', False) and value is None:
            raise ValueError(f"缺少必填参数: {param_name}")

        # 使用默认值
        if value is None and 'default' in config:
            result[param_name] = config['default']
            continue

        if value is None:
            continue

        # 类型转换
        param_type = config.get('type', str)
        try:
            if param_type == bool:
                # 布尔值特殊处理
                value = value.lower() in ('true', '1', 'yes', 'on')
            elif param_type == int:
                value = int(value)
            elif param_type == float:
                value = float(value)
            elif param_type == str:
                value = str(value).strip()
            else:
                value = param_type(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"参数 {param_name} 类型错误: {str(e)}")

        # 检查选择范围
        if 'choices' in config and value not in config['choices']:
            raise ValueError(f"参数 {param_name} 的值必须是以下之一: {config['choices']}")

        result[param_name] = value

    return result


def require_json(f):
    """
    装饰器：要求请求为JSON格式

    Args:
        f: 被装饰的函数

    Returns:
        装饰后的函数
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify(error_response("请求必须是JSON格式", "invalid_content_type")[0]), 400
        return f(*args, **kwargs)

    return decorated_function


def handle_api_errors(f):
    """
    装饰器：统一处理API错误

    Args:
        f: 被装饰的函数

    Returns:
        装饰后的函数
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            # 输入验证错误
            return jsonify(error_response(str(e), "validation_error")[0]), 400
        except KeyError as e:
            # 缺少必要参数
            return jsonify(error_response(f"缺少参数: {str(e)}", "missing_parameter")[0]), 400
        except FileNotFoundError as e:
            # 文件不存在
            return jsonify(error_response("数据文件不存在", "file_not_found", str(e))[0]), 500
        except json.JSONDecodeError as e:
            # JSON解析错误
            return jsonify(error_response("数据格式错误", "json_decode_error", str(e))[0]), 500
        except Exception as e:
            # 其他未预期的错误
            error_message = "发生未知错误"
            error_details = str(e) if request.environ.get('FLASK_DEBUG') else None

            return jsonify(error_response(error_message, "unexpected_error", error_details)[0]), 500

    return decorated_function


def get_client_ip() -> str:
    """
    获取客户端IP地址

    Returns:
        str: 客户端IP地址
    """
    # 尝试从代理头获取真实IP
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr or '127.0.0.1'


def paginate_data(data: list, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
    """
    分页处理数据

    Args:
        data: 要分页的数据列表
        page: 页码（从1开始）
        per_page: 每页数量

    Returns:
        Dict: 分页信息和数据
    """
    total = len(data)

    # 计算分页信息
    total_pages = (total + per_page - 1) // per_page
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    # 获取当前页数据
    page_data = data[start_index:end_index]

    return {
        'items': page_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }
    }


def filter_sensitive_data(data: Dict[str, Any], sensitive_keys: list = None) -> Dict[str, Any]:
    """
    过滤敏感数据

    Args:
        data: 原始数据
        sensitive_keys: 敏感字段列表

    Returns:
        Dict: 过滤后的数据
    """
    if sensitive_keys is None:
        sensitive_keys = ['password', 'secret', 'token', 'key']

    if not isinstance(data, dict):
        return data

    filtered = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            filtered[key] = '***'
        elif isinstance(value, dict):
            filtered[key] = filter_sensitive_data(value, sensitive_keys)
        elif isinstance(value, list):
            filtered[key] = [
                filter_sensitive_data(item, sensitive_keys) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            filtered[key] = value

    return filtered