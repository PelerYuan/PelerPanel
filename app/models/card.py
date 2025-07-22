"""
卡片数据模型
定义卡片的数据结构和基础操作
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any
import uuid


@dataclass
class Card:
    """卡片数据模型"""
    id: str
    name: str
    icon: str
    url: str
    description: str
    order: int
    created_time: str

    @classmethod
    def create(cls, name: str, icon: str, url: str, description: str, order: int = 0) -> 'Card':
        """
        创建新的卡片实例

        Args:
            name: 卡片名称
            icon: 图标类名 (如: bi-server)
            url: 链接地址
            description: 描述信息
            order: 排序位置，默认为0

        Returns:
            Card: 新创建的卡片实例
        """
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            icon=icon,
            url=url,
            description=description,
            order=order,
            created_time=datetime.now().isoformat()
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        将卡片对象转换为字典

        Returns:
            Dict: 卡片数据字典
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Card':
        """
        从字典创建卡片对象

        Args:
            data: 卡片数据字典

        Returns:
            Card: 卡片实例
        """
        return cls(**data)

    def update(self, **kwargs) -> 'Card':
        """
        更新卡片信息

        Args:
            **kwargs: 要更新的字段

        Returns:
            Card: 更新后的卡片实例
        """
        # 创建当前实例的副本
        data = self.to_dict()

        # 更新指定字段
        for key, value in kwargs.items():
            if hasattr(self, key):
                data[key] = value

        return self.from_dict(data)

    def __str__(self) -> str:
        """字符串表示"""
        return f"Card(name='{self.name}', url='{self.url}')"

    def __repr__(self) -> str:
        """调试用字符串表示"""
        return (f"Card(id='{self.id}', name='{self.name}', "
                f"icon='{self.icon}', url='{self.url}')")


# 用于验证的辅助函数
def validate_card_data(data: Dict[str, Any]) -> bool:
    """
    验证卡片数据的完整性

    Args:
        data: 要验证的数据字典

    Returns:
        bool: 数据是否有效
    """
    required_fields = ['id', 'name', 'icon', 'url', 'description', 'order', 'created_time']

    # 检查必需字段
    for field in required_fields:
        if field not in data:
            return False

    # 检查字段类型
    if not isinstance(data['name'], str) or not data['name'].strip():
        return False

    if not isinstance(data['icon'], str) or not data['icon'].strip():
        return False

    if not isinstance(data['url'], str) or not data['url'].strip():
        return False

    if not isinstance(data['description'], str):
        return False

    if not isinstance(data['order'], int):
        return False

    return True