"""
卡片服务测试脚本
测试 CardService 的所有功能
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.card_service import CardService


def test_card_service():
    """测试卡片服务的各项功能"""
    print("=" * 60)
    print("开始测试 CardService 功能")
    print("=" * 60)

    # 初始化服务
    card_service = CardService()

    # 测试1: 获取所有卡片（应该有之前创建的示例数据）
    print("\n1. 获取所有卡片")
    print("-" * 30)
    cards = card_service.get_all_cards()
    print(f"   找到 {len(cards)} 张卡片")
    for i, card in enumerate(cards, 1):
        print(f"   {i}. {card.name} ({card.icon}) - Order: {card.order}")

    # 测试2: 搜索功能
    print("\n2. 测试搜索功能")
    print("-" * 30)
    search_results = card_service.get_all_cards(search_query="监控")
    print(f"   搜索'监控'找到 {len(search_results)} 张卡片")
    for card in search_results:
        print(f"   - {card.name}: {card.description}")

    # 测试3: 根据ID获取卡片
    print("\n3. 根据ID获取卡片")
    print("-" * 30)
    if cards:
        first_card = cards[0]
        found_card = card_service.get_card_by_id(first_card.id)
        if found_card:
            print(f"   成功找到卡片: {found_card.name}")
        else:
            print("   未找到卡片")
    else:
        print("   没有卡片可测试")

    # 测试4: 创建新卡片
    print("\n4. 创建新卡片")
    print("-" * 30)
    success, message, new_card = card_service.create_card(
        name="测试服务",
        icon="bi-gear",
        url="http://localhost:8888/test",
        description="这是一个测试创建的服务卡片"
    )
    print(f"   创建结果: {message}")
    if success and new_card:
        print(f"   新卡片ID: {new_card.id}")
        print(f"   排序号: {new_card.order}")

    # 测试5: 名称重复检查
    print("\n5. 测试名称重复检查")
    print("-" * 30)
    success, message, _ = card_service.create_card(
        name="测试服务",  # 重复的名称
        icon="bi-gear",
        url="http://localhost:8889/test",
        description="尝试创建重复名称的卡片"
    )
    print(f"   重复名称创建结果: {message}")

    # 测试6: 名称验证
    print("\n6. 测试名称验证")
    print("-" * 30)
    valid, msg = card_service.validate_name("新服务名称")
    print(f"   验证'新服务名称': {msg}")

    valid, msg = card_service.validate_name("测试服务")  # 已存在的名称
    print(f"   验证'测试服务': {msg}")

    valid, msg = card_service.validate_name("")  # 空名称
    print(f"   验证空名称: {msg}")

    # 测试7: 更新卡片
    print("\n7. 测试更新卡片")
    print("-" * 30)
    if new_card:
        success, message, updated_card = card_service.update_card(
            card_id=new_card.id,
            name="更新后的测试服务",
            description="这是更新后的描述信息"
        )
        print(f"   更新结果: {message}")
        if success and updated_card:
            print(f"   更新后名称: {updated_card.name}")
            print(f"   更新后描述: {updated_card.description}")

    # 测试8: 获取更新后的卡片列表
    print("\n8. 获取更新后的卡片列表")
    print("-" * 30)
    updated_cards = card_service.get_all_cards()
    print(f"   现在共有 {len(updated_cards)} 张卡片")
    for i, card in enumerate(updated_cards, 1):
        print(f"   {i}. {card.name} - Order: {card.order}")

    # 测试9: 重新排序
    print("\n9. 测试重新排序")
    print("-" * 30)
    if len(updated_cards) >= 2:
        # 准备排序数据（颠倒前两张卡片的顺序）
        reorder_data = []
        for i, card in enumerate(updated_cards):
            if i == 0:
                reorder_data.append({"id": card.id, "order": 2})
            elif i == 1:
                reorder_data.append({"id": card.id, "order": 1})
            else:
                reorder_data.append({"id": card.id, "order": card.order})

        success, message = card_service.reorder_cards(reorder_data)
        print(f"   排序结果: {message}")

        if success:
            print("   重新排序后的卡片:")
            sorted_cards = card_service.get_all_cards()
            for i, card in enumerate(sorted_cards, 1):
                print(f"   {i}. {card.name} - Order: {card.order}")

    # 测试10: 输入验证
    print("\n10. 测试输入验证")
    print("-" * 30)

    # 测试无效输入
    test_cases = [
        ("", "bi-gear", "http://test.com", "描述", "空名称"),
        ("测试", "", "http://test.com", "描述", "空图标"),
        ("测试", "bi-gear", "", "描述", "空URL"),
        ("测试", "bi-gear", "invalid-url", "描述", "无效URL"),
        ("A" * 60, "bi-gear", "http://test.com", "描述", "名称过长"),
    ]

    for name, icon, url, desc, test_desc in test_cases:
        success, message, _ = card_service.create_card(name, icon, url, desc)
        print(f"   {test_desc}: {message}")

    # 测试11: 删除卡片
    print("\n11. 测试删除卡片")
    print("-" * 30)
    if new_card:
        success, message = card_service.delete_card(new_card.id)
        print(f"   删除结果: {message}")

        # 确认删除
        deleted_card = card_service.get_card_by_id(new_card.id)
        if deleted_card is None:
            print("   确认: 卡片已成功删除")
        else:
            print("   警告: 卡片仍然存在")

    # 测试12: 获取服务统计信息
    print("\n12. 获取服务统计信息")
    print("-" * 30)
    stats = card_service.get_service_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n" + "=" * 60)
    print("CardService 功能测试完成！")
    print("=" * 60)


def test_edge_cases():
    """测试边界情况"""
    print("\n" + "=" * 60)
    print("测试边界情况")
    print("=" * 60)

    card_service = CardService()

    # 测试不存在的卡片ID
    print("\n1. 测试操作不存在的卡片")
    print("-" * 30)

    fake_id = "non-existent-id"

    # 获取不存在的卡片
    card = card_service.get_card_by_id(fake_id)
    print(f"   获取不存在的卡片: {'None' if card is None else card}")

    # 更新不存在的卡片
    success, message, _ = card_service.update_card(fake_id, name="新名称")
    print(f"   更新不存在的卡片: {message}")

    # 删除不存在的卡片
    success, message = card_service.delete_card(fake_id)
    print(f"   删除不存在的卡片: {message}")

    # 测试空的重排序
    print("\n2. 测试空的重排序")
    print("-" * 30)
    success, message = card_service.reorder_cards([])
    print(f"   空重排序: {message}")

    print("\n边界情况测试完成！")


def main():
    """主函数"""
    print("CardService 测试工具")
    print("=" * 60)

    choice = input("请选择测试类型:\n1. 基础功能测试\n2. 边界情况测试\n3. 完整测试\n请输入选择 (1/2/3): ").strip()

    if choice == "1":
        test_card_service()
    elif choice == "2":
        test_edge_cases()
    elif choice == "3":
        test_card_service()
        test_edge_cases()
    else:
        print("无效的选择！")
        return

    print("\n测试完成！你可以查看 data/cards.json 文件确认数据变化。")


if __name__ == "__main__":
    main()