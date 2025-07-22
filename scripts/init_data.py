"""
初始化数据脚本
用于创建示例数据和测试数据层功能
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.models import DataManager
from app.models.card import Card


def create_sample_cards():
    """创建示例卡片数据"""
    sample_cards = [
        {
            "name": "服务器监控",
            "icon": "bi-activity",
            "url": "http://localhost:3000/grafana",
            "description": "Grafana 服务器性能监控面板",
            "order": 1
        },
        {
            "name": "文件管理",
            "icon": "bi-folder",
            "url": "http://localhost:8080/filemanager",
            "description": "Web文件管理器，支持上传下载",
            "order": 2
        },
        {
            "name": "数据库管理",
            "icon": "bi-database",
            "url": "http://localhost:8081/phpmyadmin",
            "description": "MySQL数据库管理工具",
            "order": 3
        },
        {
            "name": "代码仓库",
            "icon": "bi-github",
            "url": "http://localhost:3001/gitea",
            "description": "私有Git代码仓库服务",
            "order": 4
        },
        {
            "name": "容器管理",
            "icon": "bi-box",
            "url": "http://localhost:9000/portainer",
            "description": "Docker容器可视化管理",
            "order": 5
        },
        {
            "name": "网络存储",
            "icon": "bi-cloud",
            "url": "http://localhost:8082/nextcloud",
            "description": "私有云存储和协作平台",
            "order": 6
        }
    ]

    cards = []
    for card_data in sample_cards:
        card = Card.create(**card_data)
        cards.append(card)

    return cards


def test_data_operations():
    """测试数据层的各种操作"""
    print("=" * 50)
    print("开始测试数据层功能")
    print("=" * 50)

    # 初始化数据管理器
    data_manager = DataManager()

    # 测试1: 创建示例数据
    print("\n1. 创建示例卡片...")
    sample_cards = create_sample_cards()

    for i, card in enumerate(sample_cards, 1):
        print(f"   {i}. {card.name} - {card.icon}")

    # 测试2: 保存数据
    print("\n2. 保存卡片到JSON文件...")
    success = data_manager.save_cards(sample_cards)
    print(f"   保存结果: {'成功' if success else '失败'}")

    # 测试3: 加载数据
    print("\n3. 从JSON文件加载卡片...")
    loaded_cards = data_manager.load_cards()
    print(f"   加载了 {len(loaded_cards)} 张卡片")

    # 测试4: 根据ID查找卡片
    print("\n4. 根据ID查找卡片...")
    if loaded_cards:
        first_card = loaded_cards[0]
        found_card = data_manager.get_card_by_id(first_card.id)
        print(f"   查找卡片 '{first_card.name}': {'找到' if found_card else '未找到'}")

    # 测试5: 检查名称重复
    print("\n5. 检查名称重复...")
    exists = data_manager.card_name_exists("服务器监控")
    print(f"   '服务器监控' 是否存在: {exists}")

    exists = data_manager.card_name_exists("不存在的服务")
    print(f"   '不存在的服务' 是否存在: {exists}")

    # 测试6: 获取下一个排序号
    print("\n6. 获取下一个排序号...")
    next_order = data_manager.get_next_order()
    print(f"   下一个排序号: {next_order}")

    # 测试7: 更新卡片
    print("\n7. 测试卡片更新...")
    if loaded_cards:
        original_card = loaded_cards[0]
        updated_card = original_card.update(
            description="更新后的描述信息",
            icon="bi-gear"
        )
        print(f"   原描述: {original_card.description}")
        print(f"   新描述: {updated_card.description}")
        print(f"   原图标: {original_card.icon}")
        print(f"   新图标: {updated_card.icon}")

    # 测试8: 获取统计信息
    print("\n8. 获取数据统计信息...")
    stats = data_manager.get_stats()
    print(f"   总卡片数: {stats['total_cards']}")
    print(f"   最后更新: {stats['last_updated']}")
    print(f"   数据版本: {stats['version']}")
    print(f"   文件大小: {stats['data_file_size']} 字节")

    print("\n" + "=" * 50)
    print("数据层功能测试完成！")
    print("=" * 50)

    return True


def main():
    """主函数"""
    print("Peler Panel 数据层初始化工具")
    print("=" * 50)

    choice = input("请选择操作:\n1. 创建示例数据\n2. 运行功能测试\n3. 两者都执行\n请输入选择 (1/2/3): ").strip()

    if choice == "1":
        # 只创建示例数据
        data_manager = DataManager()
        sample_cards = create_sample_cards()
        success = data_manager.save_cards(sample_cards)
        print(f"\n示例数据创建{'成功' if success else '失败'}！")

    elif choice == "2":
        # 只运行测试
        test_data_operations()

    elif choice == "3":
        # 创建数据并测试
        data_manager = DataManager()
        sample_cards = create_sample_cards()
        data_manager.save_cards(sample_cards)
        test_data_operations()

    else:
        print("无效的选择！")
        return

    print(f"\n数据文件位置: {os.path.abspath('./data/cards.json')}")
    print("你可以查看该文件确认数据是否正确创建。")


if __name__ == "__main__":
    main()