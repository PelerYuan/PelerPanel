"""
认证服务测试脚本
测试 AuthService 的所有功能
"""

import sys
import os
import time

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.auth_service import AuthService, init_auth_service, get_auth_service


class MockSession:
    """模拟Flask session，用于测试"""

    def __init__(self):
        self.data = {}
        self.permanent = False

    def get(self, key, default=None):
        return self.data.get(key, default)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def pop(self, key, default=None):
        return self.data.pop(key, default)

    def clear(self):
        self.data.clear()


def test_auth_service():
    """测试认证服务的各项功能"""
    print("=" * 60)
    print("开始测试 AuthService 功能")
    print("=" * 60)

    # 创建模拟session
    mock_session = MockSession()

    # 手动模拟Flask session
    import app.services.auth_service as auth_module
    auth_module.session = mock_session

    # 初始化认证服务
    test_password = "admin123"
    auth_service = AuthService(test_password)

    print(f"测试密码: {test_password}")

    # 测试1: 初始状态检查
    print("\n1. 检查初始认证状态")
    print("-" * 30)
    is_auth = auth_service.is_authenticated()
    print(f"   初始认证状态: {is_auth}")

    auth_info = auth_service.get_auth_info()
    print(f"   认证信息: {auth_info}")

    # 测试2: 正确密码认证
    print("\n2. 测试正确密码认证")
    print("-" * 30)
    success, message, extra_info = auth_service.authenticate(test_password, "192.168.1.100")
    print(f"   认证结果: {success}")
    print(f"   消息: {message}")
    print(f"   额外信息: {extra_info}")

    # 检查认证后状态
    is_auth = auth_service.is_authenticated()
    print(f"   认证后状态: {is_auth}")

    # 测试3: 认证信息获取
    print("\n3. 获取认证信息")
    print("-" * 30)
    auth_info = auth_service.get_auth_info()
    for key, value in auth_info.items():
        print(f"   {key}: {value}")

    # 测试4: 退出登录
    print("\n4. 测试退出登录")
    print("-" * 30)
    success, message = auth_service.logout()
    print(f"   退出结果: {success}")
    print(f"   消息: {message}")

    is_auth = auth_service.is_authenticated()
    print(f"   退出后状态: {is_auth}")

    # 测试5: 错误密码认证
    print("\n5. 测试错误密码认证")
    print("-" * 30)
    wrong_passwords = ["wrong123", "admin", "password", ""]
    test_ip = "192.168.1.101"

    for i, wrong_pwd in enumerate(wrong_passwords, 1):
        success, message, extra_info = auth_service.authenticate(wrong_pwd, test_ip)
        print(f"   尝试 {i} ('{wrong_pwd}'): {message}")
        if 'attempts_left' in extra_info:
            print(f"   剩余尝试次数: {extra_info['attempts_left']}")

    # 测试6: 获取安全信息
    print("\n6. 获取安全信息")
    print("-" * 30)
    security_info = auth_service.get_security_info(test_ip)
    for key, value in security_info.items():
        print(f"   {key}: {value}")

    # 测试7: 继续错误尝试（触发锁定）
    print("\n7. 继续错误尝试（触发锁定）")
    print("-" * 30)
    success, message, extra_info = auth_service.authenticate("still_wrong", test_ip)
    print(f"   第5次错误尝试: {message}")
    if 'locked' in extra_info:
        print(f"   是否被锁定: {extra_info['locked']}")

    # 测试8: 锁定状态下的正确密码尝试
    print("\n8. 锁定状态下的正确密码尝试")
    print("-" * 30)
    success, message, extra_info = auth_service.authenticate(test_password, test_ip)
    print(f"   锁定状态下认证: {message}")
    if 'remaining_time' in extra_info:
        print(f"   剩余锁定时间: {extra_info['remaining_time']} 秒")

    # 测试9: 不同IP的认证
    print("\n9. 测试不同IP的认证")
    print("-" * 30)
    different_ip = "192.168.1.102"
    success, message, extra_info = auth_service.authenticate(test_password, different_ip)
    print(f"   不同IP认证: {success} - {message}")

    # 测试10: 清理过期尝试
    print("\n10. 清理过期尝试")
    print("-" * 30)
    cleaned_count = auth_service.cleanup_old_attempts()
    print(f"   清理了 {cleaned_count} 个过期记录")

    print("\n" + "=" * 60)
    print("AuthService 功能测试完成！")
    print("=" * 60)


def test_global_auth_service():
    """测试全局认证服务"""
    print("\n" + "=" * 60)
    print("测试全局认证服务")
    print("=" * 60)

    # 测试初始化
    print("\n1. 初始化全局认证服务")
    print("-" * 30)
    test_password = "global_admin123"
    global_auth = init_auth_service(test_password)
    print(f"   全局认证服务初始化: {'成功' if global_auth else '失败'}")

    # 测试获取全局服务
    print("\n2. 获取全局认证服务")
    print("-" * 30)
    retrieved_auth = get_auth_service()
    print(f"   获取全局服务: {'成功' if retrieved_auth else '失败'}")
    print(f"   服务实例相同: {global_auth is retrieved_auth}")


def test_decorator_simulation():
    """模拟测试装饰器功能"""
    print("\n" + "=" * 60)
    print("模拟测试装饰器功能")
    print("=" * 60)

    # 创建测试用的认证服务
    auth_service = AuthService("decorator_test")

    # 模拟session
    mock_session = MockSession()
    import app.services.auth_service as auth_module
    auth_module.session = mock_session

    print("\n1. 未认证状态测试")
    print("-" * 30)
    print(f"   未认证时 require_auth 检查: {not auth_service.is_authenticated()}")

    print("\n2. 认证后测试")
    print("-" * 30)
    # 先进行认证
    auth_service.authenticate("decorator_test")
    print(f"   认证后 require_auth 检查: {auth_service.is_authenticated()}")


def test_security_features():
    """测试安全特性"""
    print("\n" + "=" * 60)
    print("测试安全特性")
    print("=" * 60)

    auth_service = AuthService("security_test")

    # 模拟session
    mock_session = MockSession()
    import app.services.auth_service as auth_module
    auth_module.session = mock_session

    # 测试1: 空密码和空管理员密码
    print("\n1. 测试空密码处理")
    print("-" * 30)

    empty_auth_service = AuthService("")
    success, message, _ = empty_auth_service.authenticate("any_password")
    print(f"   空管理员密码认证: {success} - {message}")

    success, message, _ = auth_service.authenticate("")
    print(f"   空输入密码认证: {success} - {message}")

    # 测试2: 极长密码
    print("\n2. 测试极长密码")
    print("-" * 30)
    long_password = "a" * 1000
    success, message, _ = auth_service.authenticate(long_password)
    print(f"   极长密码认证: {success} - {message[:50]}...")

    # 测试3: 特殊字符密码
    print("\n3. 测试特殊字符")
    print("-" * 30)
    special_chars = "!@#$%^&*()_+-=[]{}|;:'\",.<>?/`~"
    success, message, _ = auth_service.authenticate(special_chars)
    print(f"   特殊字符认证: {success} - {message}")

    print("\n安全特性测试完成！")


def main():
    """主函数"""
    print("AuthService 测试工具")
    print("=" * 60)

    choice = input(
        "请选择测试类型:\n"
        "1. 基础功能测试\n"
        "2. 全局服务测试\n"
        "3. 装饰器模拟测试\n"
        "4. 安全特性测试\n"
        "5. 完整测试\n"
        "请输入选择 (1-5): "
    ).strip()

    if choice == "1":
        test_auth_service()
    elif choice == "2":
        test_global_auth_service()
    elif choice == "3":
        test_decorator_simulation()
    elif choice == "4":
        test_security_features()
    elif choice == "5":
        test_auth_service()
        test_global_auth_service()
        test_decorator_simulation()
        test_security_features()
    else:
        print("无效的选择！")
        return

    print("\n测试完成！")
    print("注意: 这些测试使用模拟的session，实际使用时需要Flask应用上下文。")


if __name__ == "__main__":
    main()