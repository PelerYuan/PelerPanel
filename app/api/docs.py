"""
API 文档接口
提供API接口文档和状态信息
"""

from flask import jsonify
from . import api_bp
from .utils import success_response, handle_api_errors


@api_bp.route('/docs', methods=['GET'])
@handle_api_errors
def get_api_docs():
    """
    获取API文档

    Returns:
        JSON: API接口文档
    """
    docs = {
        "title": "Peler Panel API",
        "version": "1.0.0",
        "description": "服务器管理面板API接口文档",
        "base_url": "/api",
        "endpoints": {
            "authentication": {
                "POST /auth": {
                    "description": "管理员密码验证",
                    "parameters": {
                        "password": {
                            "type": "string",
                            "required": True,
                            "description": "管理员密码"
                        }
                    },
                    "responses": {
                        "200": "认证成功",
                        "400": "密码错误或参数无效",
                        "429": "尝试次数过多"
                    }
                },
                "POST /logout": {
                    "description": "退出登录",
                    "parameters": {},
                    "responses": {
                        "200": "退出成功",
                        "400": "未登录状态"
                    }
                },
                "GET /auth/status": {
                    "description": "获取认证状态",
                    "parameters": {},
                    "responses": {
                        "200": "返回认证状态信息"
                    }
                }
            },
            "cards": {
                "GET /cards": {
                    "description": "获取卡片列表",
                    "parameters": {
                        "search": {
                            "type": "string",
                            "required": False,
                            "description": "搜索关键词"
                        },
                        "page": {
                            "type": "integer",
                            "required": False,
                            "description": "页码"
                        },
                        "per_page": {
                            "type": "integer",
                            "required": False,
                            "description": "每页数量"
                        }
                    },
                    "responses": {
                        "200": "返回卡片列表"
                    }
                },
                "POST /cards": {
                    "description": "创建新卡片",
                    "authentication_required": True,
                    "parameters": {
                        "name": {
                            "type": "string",
                            "required": True,
                            "description": "卡片名称"
                        },
                        "icon": {
                            "type": "string",
                            "required": True,
                            "description": "图标类名"
                        },
                        "url": {
                            "type": "string",
                            "required": True,
                            "description": "链接地址"
                        },
                        "description": {
                            "type": "string",
                            "required": False,
                            "description": "描述信息"
                        }
                    },
                    "responses": {
                        "201": "创建成功",
                        "400": "参数错误或名称重复",
                        "401": "需要认证"
                    }
                },
                "GET /cards/<id>": {
                    "description": "获取单个卡片",
                    "parameters": {
                        "id": {
                            "type": "string",
                            "required": True,
                            "description": "卡片ID"
                        }
                    },
                    "responses": {
                        "200": "返回卡片信息",
                        "404": "卡片不存在"
                    }
                },
                "PUT /cards/<id>": {
                    "description": "更新卡片",
                    "authentication_required": True,
                    "parameters": {
                        "id": {
                            "type": "string",
                            "required": True,
                            "description": "卡片ID"
                        },
                        "name": {
                            "type": "string",
                            "required": False,
                            "description": "卡片名称"
                        },
                        "icon": {
                            "type": "string",
                            "required": False,
                            "description": "图标类名"
                        },
                        "url": {
                            "type": "string",
                            "required": False,
                            "description": "链接地址"
                        },
                        "description": {
                            "type": "string",
                            "required": False,
                            "description": "描述信息"
                        }
                    },
                    "responses": {
                        "200": "更新成功",
                        "400": "参数错误",
                        "401": "需要认证",
                        "404": "卡片不存在"
                    }
                },
                "DELETE /cards/<id>": {
                    "description": "删除卡片",
                    "authentication_required": True,
                    "parameters": {
                        "id": {
                            "type": "string",
                            "required": True,
                            "description": "卡片ID"
                        }
                    },
                    "responses": {
                        "200": "删除成功",
                        "401": "需要认证",
                        "404": "卡片不存在"
                    }
                },
                "POST /cards/reorder": {
                    "description": "重新排序卡片",
                    "authentication_required": True,
                    "parameters": {
                        "orders": {
                            "type": "array",
                            "required": True,
                            "description": "排序数据数组 [{'id': 'card_id', 'order': 1}]"
                        }
                    },
                    "responses": {
                        "200": "排序成功",
                        "400": "参数错误",
                        "401": "需要认证"
                    }
                }
            },
            "utils": {
                "GET /icons": {
                    "description": "获取可用图标列表",
                    "parameters": {
                        "search": {
                            "type": "string",
                            "required": False,
                            "description": "图标搜索关键词"
                        },
                        "category": {
                            "type": "string",
                            "required": False,
                            "description": "图标分类"
                        }
                    },
                    "responses": {
                        "200": "返回图标列表"
                    }
                },
                "POST /validate-name": {
                    "description": "验证卡片名称唯一性",
                    "parameters": {
                        "name": {
                            "type": "string",
                            "required": True,
                            "description": "要验证的名称"
                        },
                        "exclude_id": {
                            "type": "string",
                            "required": False,
                            "description": "排除的卡片ID（更新时使用）"
                        }
                    },
                    "responses": {
                        "200": "返回验证结果"
                    }
                },
                "GET /stats": {
                    "description": "获取系统统计信息",
                    "parameters": {},
                    "responses": {
                        "200": "返回统计信息"
                    }
                }
            },
            "system": {
                "GET /docs": {
                    "description": "获取API文档（当前接口）",
                    "parameters": {},
                    "responses": {
                        "200": "返回API文档"
                    }
                },
                "GET /health": {
                    "description": "健康检查",
                    "parameters": {},
                    "responses": {
                        "200": "服务正常"
                    }
                }
            }
        },
        "error_codes": {
            "validation_error": "输入验证错误",
            "missing_parameter": "缺少必要参数",
            "authentication_required": "需要认证",
            "unauthorized": "认证失败",
            "forbidden": "权限不足",
            "not_found": "资源不存在",
            "method_not_allowed": "不支持的请求方法",
            "file_not_found": "数据文件不存在",
            "json_decode_error": "JSON格式错误",
            "internal_server_error": "服务器内部错误",
            "unexpected_error": "发生未知错误"
        },
        "response_format": {
            "success": {
                "success": True,
                "message": "操作成功",
                "data": "返回的数据（可选）"
            },
            "error": {
                "success": False,
                "error": "错误代码",
                "message": "错误消息",
                "details": "详细错误信息（可选）"
            }
        }
    }

    return jsonify(success_response(docs, "API文档获取成功"))


@api_bp.route('/health', methods=['GET'])
@handle_api_errors
def health_check():
    """
    健康检查接口

    Returns:
        JSON: 服务状态信息
    """
    from . import get_card_service, get_auth_service
    import os
    from datetime import datetime

    # 检查服务状态
    card_svc = get_card_service()
    auth_svc = get_auth_service()

    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "card_service": "ok" if card_svc else "error",
            "auth_service": "ok" if auth_svc else "error"
        },
        "system": {
            "python_version": os.sys.version,
            "flask_env": os.environ.get('FLASK_ENV', 'development')
        }
    }

    # 检查数据文件
    if card_svc:
        try:
            stats = card_svc.get_service_stats()
            health_status["data"] = {
                "total_cards": stats.get('total_cards', 0),
                "last_updated": stats.get('last_updated'),
                "data_file_accessible": True
            }
        except Exception as e:
            health_status["data"] = {
                "data_file_accessible": False,
                "error": str(e)
            }
            health_status["status"] = "degraded"

    # 确定整体状态
    if not card_svc or not auth_svc:
        health_status["status"] = "error"

    status_code = 200 if health_status["status"] == "healthy" else 503

    return jsonify(success_response(
        health_status,
        f"服务状态: {health_status['status']}"
    )), status_code