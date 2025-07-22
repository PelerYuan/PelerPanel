"""
应用配置文件
管理应用的所有配置参数
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """基础配置类"""

    # Flask 基础配置
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key-change-in-production'

    # 管理员认证配置
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'

    # 数据文件配置
    DATA_PATH = os.environ.get('DATA_PATH') or './data/cards.json'

    # 安全配置
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', '5'))
    LOCKOUT_DURATION = int(os.environ.get('LOCKOUT_DURATION', '300'))  # 5分钟

    # 应用配置
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = True

    @staticmethod
    def validate_config():
        """验证配置的有效性"""
        errors = []

        if not Config.SECRET_KEY or Config.SECRET_KEY == 'dev-secret-key-change-in-production':
            if os.environ.get('FLASK_ENV') == 'production':
                errors.append("生产环境必须设置 FLASK_SECRET_KEY")

        if not Config.ADMIN_PASSWORD:
            errors.append("必须设置 ADMIN_PASSWORD")
        elif len(Config.ADMIN_PASSWORD) < 6:
            errors.append("ADMIN_PASSWORD 长度至少为6位")

        if Config.MAX_LOGIN_ATTEMPTS < 1:
            errors.append("MAX_LOGIN_ATTEMPTS 必须大于0")

        if Config.LOCKOUT_DURATION < 60:
            errors.append("LOCKOUT_DURATION 不能少于60秒")

        return errors


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    FLASK_ENV = 'development'

    # 开发环境可以使用较短的锁定时间
    LOCKOUT_DURATION = int(os.environ.get('LOCKOUT_DURATION', '60'))  # 1分钟


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    FLASK_ENV = 'production'

    # 生产环境使用更严格的安全设置
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', '3'))
    LOCKOUT_DURATION = int(os.environ.get('LOCKOUT_DURATION', '600'))  # 10分钟


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    FLASK_ENV = 'testing'

    # 测试环境使用内存数据
    DATA_PATH = ':memory:'

    # 测试环境不锁定
    MAX_LOGIN_ATTEMPTS = 999
    LOCKOUT_DURATION = 1


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    获取配置类

    Args:
        config_name: 配置名称，如果为None则从环境变量获取

    Returns:
        Config: 配置类
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    return config.get(config_name, config['default'])


def print_config_info(config_class=None):
    """
    打印配置信息（用于调试）

    Args:
        config_class: 配置类，如果为None则获取默认配置
    """
    if config_class is None:
        config_class = get_config()

    print("=" * 50)
    print("应用配置信息")
    print("=" * 50)

    # 安全相关配置（不显示敏感信息）
    print(f"环境: {getattr(config_class, 'FLASK_ENV', 'unknown')}")
    print(f"调试模式: {getattr(config_class, 'DEBUG', False)}")
    print(f"数据文件路径: {config_class.DATA_PATH}")
    print(f"最大登录尝试次数: {config_class.MAX_LOGIN_ATTEMPTS}")
    print(f"锁定时长: {config_class.LOCKOUT_DURATION}秒")

    # 密码强度检查（不显示密码）
    password_length = len(config_class.ADMIN_PASSWORD) if config_class.ADMIN_PASSWORD else 0
    print(f"管理员密码长度: {password_length}位")

    # 验证配置
    errors = config_class.validate_config()
    if errors:
        print("\n⚠️  配置警告:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("\n✅ 配置验证通过")

    print("=" * 50)