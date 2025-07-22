"""
API 蓝图模块
统一管理所有API接口
"""

from flask import Blueprint
from app.services import CardService, AuthService

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# 全局服务实例
card_service = None
auth_service = None


def init_api_services(data_path: str, auth_svc: AuthService):
    """
    初始化API服务

    Args:
        data_path: 数据文件路径
        auth_svc: 认证服务实例
    """
    global card_service, auth_service

    card_service = CardService(data_path)
    auth_service = auth_svc


def get_card_service() -> CardService:
    """获取卡片服务实例"""
    return card_service


def get_auth_service() -> AuthService:
    """获取认证服务实例"""
    return auth_service


# 导入所有API路由模块
from . import cards
from . import auth
from . import utils_routes  # 修正文件名
from . import docs