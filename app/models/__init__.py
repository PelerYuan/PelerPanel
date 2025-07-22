"""
数据管理器
处理JSON文件的读写操作和数据持久化
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from .card import Card, validate_card_data
import shutil


class DataManager:
    """数据管理器，负责JSON文件的读写操作"""

    def __init__(self, data_path: str = './data/cards.json'):
        """
        初始化数据管理器

        Args:
            data_path: 数据文件路径
        """
        self.data_path = data_path
        self.backup_dir = os.path.join(os.path.dirname(data_path), 'backup')
        self._ensure_directories()
        self._init_data_file()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        # 创建数据目录
        data_dir = os.path.dirname(self.data_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # 创建备份目录
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def _init_data_file(self):
        """初始化数据文件"""
        if not os.path.exists(self.data_path):
            initial_data = {
                "cards": [],
                "config": {
                    "last_updated": datetime.now().isoformat(),
                    "total_cards": 0,
                    "version": "1.0"
                }
            }
            self._write_json(initial_data)

    def _read_json(self) -> Dict[str, Any]:
        """
        读取JSON数据文件

        Returns:
            Dict: JSON数据

        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON格式错误
        """
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"数据文件不存在: {self.data_path}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"JSON格式错误: {e}")

    def _write_json(self, data: Dict[str, Any]) -> bool:
        """
        写入JSON数据到文件

        Args:
            data: 要写入的数据

        Returns:
            bool: 是否写入成功
        """
        try:
            # 更新配置信息
            data['config']['last_updated'] = datetime.now().isoformat()
            data['config']['total_cards'] = len(data.get('cards', []))

            # 写入文件
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"写入数据失败: {e}")
            return False

    def backup_data(self) -> bool:
        """
        备份当前数据文件

        Returns:
            bool: 备份是否成功
        """
        if not os.path.exists(self.data_path):
            return False

        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"cards_backup_{timestamp}.json"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            shutil.copy2(self.data_path, backup_path)
            print(f"数据已备份到: {backup_path}")
            return True
        except Exception as e:
            print(f"备份失败: {e}")
            return False

    def load_cards(self) -> List[Card]:
        """
        加载所有卡片

        Returns:
            List[Card]: 卡片列表
        """
        try:
            data = self._read_json()
            cards = []

            for card_data in data.get('cards', []):
                if validate_card_data(card_data):
                    cards.append(Card.from_dict(card_data))
                else:
                    print(f"跳过无效的卡片数据: {card_data}")

            # 按order字段排序
            cards.sort(key=lambda x: x.order)
            return cards

        except Exception as e:
            print(f"加载卡片失败: {e}")
            return []

    def save_cards(self, cards: List[Card]) -> bool:
        """
        保存卡片列表

        Args:
            cards: 卡片列表

        Returns:
            bool: 是否保存成功
        """
        try:
            # 备份现有数据
            self.backup_data()

            # 读取现有配置
            try:
                data = self._read_json()
            except:
                data = {"config": {"version": "1.0"}}

            # 更新卡片数据
            data['cards'] = [card.to_dict() for card in cards]

            return self._write_json(data)

        except Exception as e:
            print(f"保存卡片失败: {e}")
            return False

    def get_card_by_id(self, card_id: str) -> Optional[Card]:
        """
        根据ID获取卡片

        Args:
            card_id: 卡片ID

        Returns:
            Optional[Card]: 找到的卡片或None
        """
        cards = self.load_cards()
        for card in cards:
            if card.id == card_id:
                return card
        return None

    def card_name_exists(self, name: str, exclude_id: str = None) -> bool:
        """
        检查卡片名称是否已存在

        Args:
            name: 要检查的名称
            exclude_id: 排除的卡片ID（用于更新时检查）

        Returns:
            bool: 名称是否已存在
        """
        cards = self.load_cards()
        for card in cards:
            if card.name == name and card.id != exclude_id:
                return True
        return False

    def get_next_order(self) -> int:
        """
        获取下一个排序号

        Returns:
            int: 下一个可用的排序号
        """
        cards = self.load_cards()
        if not cards:
            return 1
        return max(card.order for card in cards) + 1

    def get_stats(self) -> Dict[str, Any]:
        """
        获取数据统计信息

        Returns:
            Dict: 统计信息
        """
        try:
            data = self._read_json()
            cards = self.load_cards()

            return {
                "total_cards": len(cards),
                "last_updated": data.get('config', {}).get('last_updated'),
                "version": data.get('config', {}).get('version', '1.0'),
                "data_file_size": os.path.getsize(self.data_path) if os.path.exists(self.data_path) else 0
            }
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {
                "total_cards": 0,
                "last_updated": None,
                "version": "1.0",
                "data_file_size": 0
            }