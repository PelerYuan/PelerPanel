"""
认证服务
处理管理员认证和权限管理
"""

import hashlib
import secrets
import time
from typing import Dict, Any, Optional, Tuple
from functools import wraps
from flask import session, request, jsonify


class AuthService:
    """认证服务类"""

    def __init__(self, admin_password: str):
        """
        初始化认证服务

        Args:
            admin_password: 管理员密码
        """
        self.admin_password = admin_password
        self.failed_attempts = {}  # 记录失败尝试次数 {ip: {'count': int, 'last_attempt': timestamp}}
        self.max_attempts = 5  # 最大尝试次数
        self.lockout_duration = 300  # 锁定时间（秒）- 5分钟
        self.session_key = 'admin_authenticated'
        self.session_time_key = 'auth_time'

    def authenticate(self, password: str, client_ip: str = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        验证管理员密码

        Args:
            password: 输入的密码
            client_ip: 客户端IP地址（可选，用于防暴力破解）

        Returns:
            Tuple[bool, str, Dict]: (是否成功, 消息, 额外信息)
        """
        try:
            # 检查是否被锁定
            if client_ip and self._is_locked_out(client_ip):
                remaining_time = self._get_lockout_remaining_time(client_ip)
                return False, f"尝试次数过多，请在 {remaining_time} 秒后重试", {
                    'locked': True,
                    'remaining_time': remaining_time
                }

            # 验证密码
            if self._verify_password(password):
                # 密码正确，清除失败记录
                if client_ip:
                    self._clear_failed_attempts(client_ip)

                # 设置session
                self._set_authenticated_session()

                return True, "认证成功", {
                    'authenticated': True,
                    'session_expires': 'browser_close'
                }
            else:
                # 密码错误，记录失败尝试
                if client_ip:
                    self._record_failed_attempt(client_ip)
                    attempts_left = self.max_attempts - self.failed_attempts.get(client_ip, {}).get('count', 0)

                    if attempts_left > 0:
                        return False, f"密码错误，还有 {attempts_left} 次尝试机会", {
                            'attempts_left': attempts_left
                        }
                    else:
                        return False, f"密码错误次数过多，已锁定 {self.lockout_duration // 60} 分钟", {
                            'locked': True,
                            'lockout_duration': self.lockout_duration
                        }
                else:
                    return False, "密码错误", {}

        except Exception as e:
            error_msg = f"认证过程发生错误: {e}"
            print(error_msg)
            return False, "认证服务异常", {'error': str(e)}

    def is_authenticated(self) -> bool:
        """
        检查当前是否已认证

        Returns:
            bool: 是否已认证
        """
        try:
            return session.get(self.session_key, False) is True
        except Exception:
            return False

    def logout(self) -> Tuple[bool, str]:
        """
        退出登录

        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            if session.get(self.session_key):
                session.pop(self.session_key, None)
                session.pop(self.session_time_key, None)
                return True, "退出登录成功"
            else:
                return False, "未登录状态"
        except Exception as e:
            error_msg = f"退出登录失败: {e}"
            print(error_msg)
            return False, error_msg

    def get_auth_info(self) -> Dict[str, Any]:
        """
        获取认证信息

        Returns:
            Dict[str, Any]: 认证状态信息
        """
        try:
            if self.is_authenticated():
                auth_time = session.get(self.session_time_key)
                return {
                    'authenticated': True,
                    'auth_time': auth_time,
                    'session_type': 'browser_session',
                    'expires': 'browser_close'
                }
            else:
                return {
                    'authenticated': False,
                    'auth_time': None,
                    'session_type': None,
                    'expires': None
                }
        except Exception as e:
            return {
                'authenticated': False,
                'error': str(e)
            }

    def get_security_info(self, client_ip: str = None) -> Dict[str, Any]:
        """
        获取安全信息（失败尝试次数等）

        Args:
            client_ip: 客户端IP地址

        Returns:
            Dict[str, Any]: 安全信息
        """
        try:
            info = {
                'max_attempts': self.max_attempts,
                'lockout_duration': self.lockout_duration,
            }

            if client_ip and client_ip in self.failed_attempts:
                attempt_data = self.failed_attempts[client_ip]
                info.update({
                    'failed_attempts': attempt_data['count'],
                    'is_locked': self._is_locked_out(client_ip),
                    'last_attempt': attempt_data['last_attempt']
                })

                if self._is_locked_out(client_ip):
                    info['remaining_lockout'] = self._get_lockout_remaining_time(client_ip)
            else:
                info.update({
                    'failed_attempts': 0,
                    'is_locked': False,
                    'last_attempt': None
                })

            return info

        except Exception as e:
            return {'error': str(e)}

    def require_auth(self, f):
        """
        装饰器：要求认证
        用于保护需要管理员权限的路由

        Args:
            f: 被装饰的函数

        Returns:
            装饰后的函数
        """

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.is_authenticated():
                return jsonify({
                    'success': False,
                    'message': '需要管理员认证',
                    'error': 'authentication_required'
                }), 401
            return f(*args, **kwargs)

        return decorated_function

    def _verify_password(self, password: str) -> bool:
        """
        验证密码

        Args:
            password: 待验证的密码

        Returns:
            bool: 密码是否正确
        """
        if not password or not self.admin_password:
            return False

        # 简单的明文密码比较（在生产环境中应该使用哈希）
        return password == self.admin_password

    def _set_authenticated_session(self):
        """设置认证session"""
        session[self.session_key] = True
        session[self.session_time_key] = time.time()
        session.permanent = False  # 浏览器关闭时过期

    def _record_failed_attempt(self, client_ip: str):
        """
        记录失败的认证尝试

        Args:
            client_ip: 客户端IP地址
        """
        current_time = time.time()

        if client_ip not in self.failed_attempts:
            self.failed_attempts[client_ip] = {
                'count': 0,
                'last_attempt': current_time
            }

        # 如果距离上次尝试超过锁定时间，重置计数
        if current_time - self.failed_attempts[client_ip]['last_attempt'] > self.lockout_duration:
            self.failed_attempts[client_ip]['count'] = 0

        self.failed_attempts[client_ip]['count'] += 1
        self.failed_attempts[client_ip]['last_attempt'] = current_time

    def _clear_failed_attempts(self, client_ip: str):
        """
        清除失败尝试记录

        Args:
            client_ip: 客户端IP地址
        """
        if client_ip in self.failed_attempts:
            del self.failed_attempts[client_ip]

    def _is_locked_out(self, client_ip: str) -> bool:
        """
        检查IP是否被锁定

        Args:
            client_ip: 客户端IP地址

        Returns:
            bool: 是否被锁定
        """
        if client_ip not in self.failed_attempts:
            return False

        attempt_data = self.failed_attempts[client_ip]

        # 如果尝试次数未达到上限，没有锁定
        if attempt_data['count'] < self.max_attempts:
            return False

        # 检查锁定时间是否已过
        current_time = time.time()
        time_since_last_attempt = current_time - attempt_data['last_attempt']

        if time_since_last_attempt > self.lockout_duration:
            # 锁定时间已过，清除记录
            self._clear_failed_attempts(client_ip)
            return False

        return True

    def _get_lockout_remaining_time(self, client_ip: str) -> int:
        """
        获取锁定剩余时间

        Args:
            client_ip: 客户端IP地址

        Returns:
            int: 剩余锁定时间（秒）
        """
        if client_ip not in self.failed_attempts:
            return 0

        attempt_data = self.failed_attempts[client_ip]
        current_time = time.time()
        elapsed_time = current_time - attempt_data['last_attempt']
        remaining_time = max(0, self.lockout_duration - int(elapsed_time))

        return remaining_time

    def cleanup_old_attempts(self):
        """
        清理过期的失败尝试记录
        建议定期调用此方法
        """
        current_time = time.time()
        expired_ips = []

        for client_ip, attempt_data in self.failed_attempts.items():
            if current_time - attempt_data['last_attempt'] > self.lockout_duration * 2:
                expired_ips.append(client_ip)

        for ip in expired_ips:
            del self.failed_attempts[ip]

        return len(expired_ips)


# 全局认证服务实例（将在应用初始化时设置）
auth_service: Optional[AuthService] = None


def init_auth_service(admin_password: str) -> AuthService:
    """
    初始化全局认证服务

    Args:
        admin_password: 管理员密码

    Returns:
        AuthService: 认证服务实例
    """
    global auth_service
    auth_service = AuthService(admin_password)
    return auth_service


def get_auth_service() -> Optional[AuthService]:
    """
    获取全局认证服务实例

    Returns:
        Optional[AuthService]: 认证服务实例或None
    """
    return auth_service


def require_admin_auth(f):
    """
    装饰器：要求管理员认证
    这是一个便捷的装饰器，使用全局认证服务

    Args:
        f: 被装饰的函数

    Returns:
        装饰后的函数
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_service:
            return jsonify({
                'success': False,
                'message': '认证服务未初始化',
                'error': 'auth_service_not_initialized'
            }), 500

        if not auth_service.is_authenticated():
            return jsonify({
                'success': False,
                'message': '需要管理员认证',
                'error': 'authentication_required'
            }), 401

        return f(*args, **kwargs)

    return decorated_function