"""
API 接口测试脚本
测试所有API接口的功能
"""

import sys
import os
import requests
import json
import time

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class APITester:
    """API测试器"""

    def __init__(self, base_url='http://localhost:5000'):
        """
        初始化API测试器

        Args:
            base_url: API基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.test_results = []

    def log_test(self, test_name, success, message, details=None):
        """记录测试结果"""
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   详情: {details}")

        self.test_results.append({
            'name': test_name,
            'success': success,
            'message': message,
            'details': details
        })

    def make_request(self, method, endpoint, **kwargs):
        """
        发送API请求

        Args:
            method: HTTP方法
            endpoint: 接口端点
            **kwargs: requests参数

        Returns:
            tuple: (是否成功, 响应对象, 错误消息)
        """
        url = f"{self.api_url}{endpoint}"

        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            return True, response, None
        except requests.exceptions.RequestException as e:
            return False, None, str(e)

    def test_health_check(self):
        """测试健康检查接口"""
        success, response, error = self.make_request('GET', '/health')

        if not success:
            self.log_test("健康检查", False, f"请求失败: {error}")
            return False

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    self.log_test("健康检查", True, "服务健康状态正常")
                    return True
                else:
                    self.log_test("健康检查", False, "服务状态异常", data.get('message'))
            except ValueError:
                self.log_test("健康检查", False, "响应格式错误")
        else:
            self.log_test("健康检查", False, f"HTTP状态码: {response.status_code}")

        return False

    def test_get_docs(self):
        """测试获取API文档"""
        success, response, error = self.make_request('GET', '/docs')

        if not success:
            self.log_test("API文档", False, f"请求失败: {error}")
            return False

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success') and 'endpoints' in data.get('data', {}):
                    endpoint_count = len(data['data']['endpoints'])
                    self.log_test("API文档", True, f"文档获取成功，包含{endpoint_count}个分类")
                    return True
                else:
                    self.log_test("API文档", False, "文档格式不正确")
            except ValueError:
                self.log_test("API文档", False, "响应格式错误")
        else:
            self.log_test("API文档", False, f"HTTP状态码: {response.status_code}")

        return False

    def test_get_cards(self):
        """测试获取卡片列表"""
        success, response, error = self.make_request('GET', '/cards')

        if not success:
            self.log_test("获取卡片列表", False, f"请求失败: {error}")
            return False

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    total = data.get('data', {}).get('total', 0)
                    self.log_test("获取卡片列表", True, f"获取成功，共{total}张卡片")
                    return True
                else:
                    self.log_test("获取卡片列表", False, data.get('message'))
            except ValueError:
                self.log_test("获取卡片列表", False, "响应格式错误")
        else:
            self.log_test("获取卡片列表", False, f"HTTP状态码: {response.status_code}")

        return False

    def test_search_cards(self):
        """测试搜索卡片"""
        success, response, error = self.make_request('GET', '/cards', params={'search': '监控'})

        if not success:
            self.log_test("搜索卡片", False, f"请求失败: {error}")
            return False

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    total = data.get('data', {}).get('total', 0)
                    self.log_test("搜索卡片", True, f"搜索成功，找到{total}张卡片")
                    return True
                else:
                    self.log_test("搜索卡片", False, data.get('message'))
            except ValueError:
                self.log_test("搜索卡片", False, "响应格式错误")
        else:
            self.log_test("搜索卡片", False, f"HTTP状态码: {response.status_code}")

        return False

    def test_auth_status(self):
        """测试认证状态"""
        success, response, error = self.make_request('GET', '/auth/status')

        if not success:
            self.log_test("认证状态", False, f"请求失败: {error}")
            return False

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    is_auth = data.get('data', {}).get('authenticated', False)
                    self.log_test("认证状态", True, f"状态获取成功，认证状态: {'已认证' if is_auth else '未认证'}")
                    return True
                else:
                    self.log_test("认证状态", False, data.get('message'))
            except ValueError:
                self.log_test("认证状态", False, "响应格式错误")
        else:
            self.log_test("认证状态", False, f"HTTP状态码: {response.status_code}")

        return False

    def test_login(self, password="admin123"):
        """测试登录"""
        login_data = {"password": password}

        success, response, error = self.make_request(
            'POST', '/auth',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )

        if not success:
            self.log_test("管理员登录", False, f"请求失败: {error}")
            return False

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    self.log_test("管理员登录", True, "登录成功")
                    return True
                else:
                    self.log_test("管理员登录", False, data.get('message'))
            except ValueError:
                self.log_test("管理员登录", False, "响应格式错误")
        elif response.status_code == 401:
            try:
                data = response.json()
                self.log_test("管理员登录", False, f"认证失败: {data.get('message')}")
            except ValueError:
                self.log_test("管理员登录", False, "认证失败，响应格式错误")
        else:
            self.log_test("管理员登录", False, f"HTTP状态码: {response.status_code}")

        return False

    def test_create_card(self):
        """测试创建卡片（需要先登录）"""
        card_data = {
            "name": "API测试卡片",
            "icon": "bi-gear",
            "url": "http://localhost:9999/test",
            "description": "这是API测试创建的卡片"
        }

        success, response, error = self.make_request(
            'POST', '/cards',
            json=card_data,
            headers={'Content-Type': 'application/json'}
        )

        if not success:
            self.log_test("创建卡片", False, f"请求失败: {error}")
            return False, None

        if response.status_code == 201:
            try:
                data = response.json()
                if data.get('success'):
                    card_id = data.get('data', {}).get('id')
                    self.log_test("创建卡片", True, f"创建成功，ID: {card_id}")
                    return True, card_id
                else:
                    self.log_test("创建卡片", False, data.get('message'))
            except ValueError:
                self.log_test("创建卡片", False, "响应格式错误")
        elif response.status_code == 401:
            self.log_test("创建卡片", False, "需要管理员认证")
        elif response.status_code == 409:
            try:
                data = response.json()
                self.log_test("创建卡片", False, f"名称冲突: {data.get('message')}")
            except ValueError:
                self.log_test("创建卡片", False, "名称冲突")
        else:
            self.log_test("创建卡片", False, f"HTTP状态码: {response.status_code}")

        return False, None

    def test_update_card(self, card_id):
        """测试更新卡片"""
        if not card_id:
            self.log_test("更新卡片", False, "缺少卡片ID")
            return False

        update_data = {
            "description": "API测试更新后的描述"
        }

        success, response, error = self.make_request(
            'PUT', f'/cards/{card_id}',
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )

        if not success:
            self.log_test("更新卡片", False, f"请求失败: {error}")
            return False

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    self.log_test("更新卡片", True, "更新成功")
                    return True
                else:
                    self.log_test("更新卡片", False, data.get('message'))
            except ValueError:
                self.log_test("更新卡片", False, "响应格式错误")
        elif response.status_code == 404:
            self.log_test("更新卡片", False, "卡片不存在")
        elif response.status_code == 401:
            self.log_test("更新卡片", False, "需要管理员认证")
        else:
            self.log_test("更新卡片", False, f"HTTP状态码: {response.status_code}")

        return False

    def test_delete_card(self, card_id):
        """测试删除卡片"""
        if not card_id:
            self.log_test("删除卡片", False, "缺少卡片ID")
            return False

        success, response, error = self.make_request('DELETE', f'/cards/{card_id}')

        if not success:
            self.log_test("删除卡片", False, f"请求失败: {error}")
            return False

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    self.log_test("删除卡片", True, "删除成功")
                    return True
                else:
                    self.log_test("删除卡片", False, data.get('message'))
            except ValueError:
                self.log_test("删除卡片", False, "响应格式错误")
        elif response.status_code == 404:
            self.log_test("删除卡片", False, "卡片不存在")
        elif response.status_code == 401:
            self.log_test("删除卡片", False, "需要管理员认证")
        else:
            self.log_test("删除卡片", False, f"HTTP状态码: {response.status_code}")

        return False

    def test_get_icons(self):
        """测试获取图标列表"""
        success, response, error = self.make_request('GET', '/icons')

        if not success:
            self.log_test("获取图标列表", False, f"请求失败: {error}")
            return False

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    total = data.get('data', {}).get('total_count', 0)
                    self.log_test("获取图标列表", True, f"获取成功，共{total}个图标")
                    return True
                else:
                    self.log_test("获取图标列表", False, data.get('message'))
            except ValueError:
                self.log_test("获取图标列表", False, "响应格式错误")
        else:
            self.log_test("获取图标列表", False, f"HTTP状态码: {response.status_code}")

        return False

    def test_validate_name(self):
        """测试名称验证"""
        validate_data = {"name": "测试名称验证"}

        success, response, error = self.make_request(
            'POST', '/validate-name',
            json=validate_data,
            headers={'Content-Type': 'application/json'}
        )

        if not success:
            self.log_test("名称验证", False, f"请求失败: {error}")
            return False

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    is_valid = data.get('data', {}).get('is_valid', False)
                    message = data.get('data', {}).get('message', '')
                    self.log_test("名称验证", True, f"验证完成: {message}")
                    return True
                else:
                    self.log_test("名称验证", False, data.get('message'))
            except ValueError:
                self.log_test("名称验证", False, "响应格式错误")
        else:
            self.log_test("名称验证", False, f"HTTP状态码: {response.status_code}")

        return False

    def test_get_stats(self):
        """测试获取统计信息"""
        success, response, error = self.make_request('GET', '/stats')

        if not success:
            self.log_test("获取统计信息", False, f"请求失败: {error}")
            return False

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    service_stats = data.get('data', {}).get('service', {})
                    total_cards = service_stats.get('total_cards', 0)
                    self.log_test("获取统计信息", True, f"获取成功，系统共有{total_cards}张卡片")
                    return True
                else:
                    self.log_test("获取统计信息", False, data.get('message'))
            except ValueError:
                self.log_test("获取统计信息", False, "响应格式错误")
        else:
            self.log_test("获取统计信息", False, f"HTTP状态码: {response.status_code}")

        return False

    def test_logout(self):
        """测试退出登录"""
        success, response, error = self.make_request('POST', '/logout')

        if not success:
            self.log_test("退出登录", False, f"请求失败: {error}")
            return False

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    self.log_test("退出登录", True, "退出成功")
                    return True
                else:
                    self.log_test("退出登录", False, data.get('message'))
            except ValueError:
                self.log_test("退出登录", False, "响应格式错误")
        else:
            self.log_test("退出登录", False, f"HTTP状态码: {response.status_code}")

        return False

    def run_basic_tests(self):
        """运行基础测试（不需要认证）"""
        print("\n" + "="*60)
        print("运行基础API测试（无需认证）")
        print("="*60)

        tests = [
            self.test_health_check,
            self.test_get_docs,
            self.test_get_cards,
            self.test_search_cards,
            self.test_auth_status,
            self.test_get_icons,
            self.test_validate_name,
            self.test_get_stats
        ]

        for test in tests:
            test()
            time.sleep(0.5)  # 避免请求过快

    def run_admin_tests(self, admin_password="admin123"):
        """运行管理员测试（需要认证）"""
        print("\n" + "="*60)
        print("运行管理员API测试（需要认证）")
        print("="*60)

        # 先登录
        if not self.test_login(admin_password):
            print("⚠️  管理员登录失败，跳过需要认证的测试")
            return

        time.sleep(1)

        # 测试创建、更新、删除卡片
        success, card_id = self.test_create_card()

        if success and card_id:
            time.sleep(0.5)
            self.test_update_card(card_id)
            time.sleep(0.5)
            self.test_delete_card(card_id)

        time.sleep(0.5)

        # 最后退出登录
        self.test_logout()

    def run_all_tests(self, admin_password="admin123"):
        """运行所有测试"""
        print("🚀 开始API接口测试")
        print(f"   目标服务器: {self.base_url}")
        print(f"   API基础路径: {self.api_url}")

        self.run_basic_tests()
        self.run_admin_tests(admin_password)

        self.print_summary()

    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("API测试结果摘要")
        print("="*60)

        total = len(self.test_results)
        passed = sum(1 for result in self.test_results if result['success'])
        failed = total - passed

        print(f"总测试数: {total}")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        print(f"通过率: {(passed/total*100):.1f}%")

        if failed > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['name']}: {result['message']}")

        print("\n" + "="*60)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='Peler Panel API测试工具')
    parser.add_argument('--url', default='http://localhost:5000',
                       help='API服务器URL (默认: http://localhost:5000)')
    parser.add_argument('--password', default='admin123',
                       help='管理员密码 (默认: admin123)')
    parser.add_argument('--basic-only', action='store_true',
                       help='只运行基础测试，跳过需要认证的测试')

    args = parser.parse_args()

    # 创建测试器
    tester = APITester(args.url)

    try:
        if args.basic_only:
            tester.run_basic_tests()
        else:
            tester.run_all_tests(args.password)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        tester.print_summary()
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")


if __name__ == "__main__":
    main()