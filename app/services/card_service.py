"""
卡片管理服务
处理卡片的业务逻辑操作
"""

from typing import List, Optional, Dict, Any, Tuple
from app.models import DataManager
from app.models.card import Card, validate_card_data


class CardService:
    """卡片管理服务类"""

    def __init__(self, data_path: str = './data/cards.json'):
        """
        初始化卡片服务

        Args:
            data_path: 数据文件路径
        """
        self.data_manager = DataManager(data_path)

    def get_all_cards(self, search_query: str = None) -> List[Card]:
        """
        获取所有卡片，支持搜索

        Args:
            search_query: 搜索关键词，搜索名称和描述

        Returns:
            List[Card]: 卡片列表，按order排序
        """
        try:
            cards = self.data_manager.load_cards()

            # 如果有搜索查询，进行过滤
            if search_query:
                search_query = search_query.strip().lower()
                filtered_cards = []

                for card in cards:
                    # 搜索名称和描述
                    if (search_query in card.name.lower() or
                            search_query in card.description.lower()):
                        filtered_cards.append(card)

                return filtered_cards

            return cards

        except Exception as e:
            print(f"获取卡片列表失败: {e}")
            return []

    def get_card_by_id(self, card_id: str) -> Optional[Card]:
        """
        根据ID获取单个卡片

        Args:
            card_id: 卡片ID

        Returns:
            Optional[Card]: 找到的卡片或None
        """
        try:
            return self.data_manager.get_card_by_id(card_id)
        except Exception as e:
            print(f"根据ID获取卡片失败: {e}")
            return None

    def create_card(self, name: str, icon: str, url: str, description: str) -> Tuple[bool, str, Optional[Card]]:
        """
        创建新卡片

        Args:
            name: 卡片名称
            icon: 图标类名
            url: 链接地址
            description: 描述信息

        Returns:
            Tuple[bool, str, Optional[Card]]: (是否成功, 消息, 创建的卡片)
        """
        try:
            # 验证输入数据
            validation_result, validation_message = self._validate_card_input(
                name, icon, url, description
            )
            if not validation_result:
                return False, validation_message, None

            # 检查名称是否重复
            if self.data_manager.card_name_exists(name):
                return False, f"卡片名称 '{name}' 已存在", None

            # 获取下一个排序号
            next_order = self.data_manager.get_next_order()

            # 创建卡片
            new_card = Card.create(
                name=name.strip(),
                icon=icon.strip(),
                url=url.strip(),
                description=description.strip(),
                order=next_order
            )

            # 保存到数据库
            cards = self.data_manager.load_cards()
            cards.append(new_card)

            success = self.data_manager.save_cards(cards)

            if success:
                return True, "卡片创建成功", new_card
            else:
                return False, "保存卡片失败", None

        except Exception as e:
            error_msg = f"创建卡片时发生错误: {e}"
            print(error_msg)
            return False, error_msg, None

    def update_card(self, card_id: str, name: str = None, icon: str = None,
                    url: str = None, description: str = None) -> Tuple[bool, str, Optional[Card]]:
        """
        更新卡片信息

        Args:
            card_id: 卡片ID
            name: 新的名称（可选）
            icon: 新的图标（可选）
            url: 新的链接（可选）
            description: 新的描述（可选）

        Returns:
            Tuple[bool, str, Optional[Card]]: (是否成功, 消息, 更新后的卡片)
        """
        try:
            # 查找要更新的卡片
            existing_card = self.data_manager.get_card_by_id(card_id)
            if not existing_card:
                return False, "卡片不存在", None

            # 准备更新数据
            update_data = {}

            # 处理需要更新的字段
            if name is not None:
                name = name.strip()
                if not name:
                    return False, "卡片名称不能为空", None

                # 检查名称重复（排除当前卡片）
                if self.data_manager.card_name_exists(name, exclude_id=card_id):
                    return False, f"卡片名称 '{name}' 已存在", None

                update_data['name'] = name

            if icon is not None:
                icon = icon.strip()
                if not icon:
                    return False, "图标不能为空", None
                update_data['icon'] = icon

            if url is not None:
                url = url.strip()
                if not url:
                    return False, "链接不能为空", None
                update_data['url'] = url

            if description is not None:
                update_data['description'] = description.strip()

            # 如果没有要更新的内容
            if not update_data:
                return False, "没有要更新的内容", existing_card

            # 创建更新后的卡片
            updated_card = existing_card.update(**update_data)

            # 更新卡片列表
            cards = self.data_manager.load_cards()
            for i, card in enumerate(cards):
                if card.id == card_id:
                    cards[i] = updated_card
                    break

            # 保存更新
            success = self.data_manager.save_cards(cards)

            if success:
                return True, "卡片更新成功", updated_card
            else:
                return False, "保存更新失败", None

        except Exception as e:
            error_msg = f"更新卡片时发生错误: {e}"
            print(error_msg)
            return False, error_msg, None

    def delete_card(self, card_id: str) -> Tuple[bool, str]:
        """
        删除卡片

        Args:
            card_id: 要删除的卡片ID

        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 检查卡片是否存在
            existing_card = self.data_manager.get_card_by_id(card_id)
            if not existing_card:
                return False, "卡片不存在"

            # 获取所有卡片并移除指定卡片
            cards = self.data_manager.load_cards()
            original_count = len(cards)

            cards = [card for card in cards if card.id != card_id]

            if len(cards) == original_count:
                return False, "未找到要删除的卡片"

            # 重新调整排序号
            for i, card in enumerate(cards):
                if card.order != i + 1:
                    cards[i] = card.update(order=i + 1)

            # 保存更新后的卡片列表
            success = self.data_manager.save_cards(cards)

            if success:
                return True, f"卡片 '{existing_card.name}' 删除成功"
            else:
                return False, "保存删除结果失败"

        except Exception as e:
            error_msg = f"删除卡片时发生错误: {e}"
            print(error_msg)
            return False, error_msg

    def reorder_cards(self, card_orders: List[Dict[str, int]]) -> Tuple[bool, str]:
        """
        重新排序卡片

        Args:
            card_orders: 卡片排序列表，格式: [{'id': 'card_id', 'order': 1}, ...]

        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            if not card_orders:
                return False, "排序数据为空"

            # 加载现有卡片
            cards = self.data_manager.load_cards()

            # 创建ID到卡片的映射
            card_map = {card.id: card for card in cards}

            # 验证所有ID都存在
            for item in card_orders:
                if 'id' not in item or 'order' not in item:
                    return False, "排序数据格式错误"

                card_id = item['id']
                if card_id not in card_map:
                    return False, f"卡片ID {card_id} 不存在"

            # 更新排序
            updated_cards = []
            for item in card_orders:
                card_id = item['id']
                new_order = item['order']

                original_card = card_map[card_id]
                updated_card = original_card.update(order=new_order)
                updated_cards.append(updated_card)

            # 按order排序
            updated_cards.sort(key=lambda x: x.order)

            # 保存更新
            success = self.data_manager.save_cards(updated_cards)

            if success:
                return True, "卡片排序更新成功"
            else:
                return False, "保存排序结果失败"

        except Exception as e:
            error_msg = f"重排序卡片时发生错误: {e}"
            print(error_msg)
            return False, error_msg

    def validate_name(self, name: str, exclude_id: str = None) -> Tuple[bool, str]:
        """
        验证卡片名称是否可用

        Args:
            name: 要验证的名称
            exclude_id: 排除的卡片ID（用于更新时验证）

        Returns:
            Tuple[bool, str]: (是否可用, 消息)
        """
        try:
            if not name or not name.strip():
                return False, "卡片名称不能为空"

            name = name.strip()

            if len(name) > 50:  # 设置名称长度限制
                return False, "卡片名称不能超过50个字符"

            if self.data_manager.card_name_exists(name, exclude_id):
                return False, f"卡片名称 '{name}' 已存在"

            return True, "名称可用"

        except Exception as e:
            error_msg = f"验证名称时发生错误: {e}"
            print(error_msg)
            return False, error_msg

    def get_service_stats(self) -> Dict[str, Any]:
        """
        获取服务统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            stats = self.data_manager.get_stats()

            # 添加额外的统计信息
            cards = self.data_manager.load_cards()

            if cards:
                stats['oldest_card'] = min(cards, key=lambda x: x.created_time).name
                stats['newest_card'] = max(cards, key=lambda x: x.created_time).name
                stats['max_order'] = max(card.order for card in cards)
            else:
                stats['oldest_card'] = None
                stats['newest_card'] = None
                stats['max_order'] = 0

            return stats

        except Exception as e:
            print(f"获取服务统计信息失败: {e}")
            return {"error": str(e)}

    def _validate_card_input(self, name: str, icon: str, url: str, description: str) -> Tuple[bool, str]:
        """
        验证卡片输入数据

        Args:
            name: 卡片名称
            icon: 图标类名
            url: 链接地址
            description: 描述信息

        Returns:
            Tuple[bool, str]: (是否有效, 错误消息)
        """
        # 检查必填字段
        if not name or not name.strip():
            return False, "卡片名称不能为空"

        if not icon or not icon.strip():
            return False, "图标不能为空"

        if not url or not url.strip():
            return False, "链接不能为空"

        # 检查长度限制
        if len(name.strip()) > 50:
            return False, "卡片名称不能超过50个字符"

        if len(description.strip()) > 200:
            return False, "描述信息不能超过200个字符"

        # 基本的URL格式检查
        url = url.strip()
        if not (url.startswith('http://') or url.startswith('https://')):
            return False, "链接必须以 http:// 或 https:// 开头"

        return True, "验证通过"