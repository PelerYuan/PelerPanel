"""
Peler Panel Flask 主应用
服务器管理面板的核心应用
"""

import os
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

from config import get_config, print_config_info
from app.services import init_auth_service
from app.api import api_bp, init_api_services


def create_app(config_name=None):
    """
    应用工厂函数

    Args:
        config_name: 配置名称

    Returns:
        Flask: Flask应用实例
    """
    app = Flask(__name__)

    # 加载配置
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # 验证配置
    config_errors = config_class.validate_config()
    if config_errors:
        print("⚠️  配置错误:")
        for error in config_errors:
            print(f"   - {error}")
        if not app.config.get('DEBUG', False):
            raise RuntimeError("生产环境配置错误，应用启动失败")

    # 初始化服务
    init_services(app)

    # 注册蓝图
    register_blueprints(app)

    # 注册错误处理器
    register_error_handlers(app)

    # 注册请求处理器
    register_request_handlers(app)

    return app


def init_services(app):
    """初始化应用服务"""
    with app.app_context():
        # 初始化认证服务
        admin_password = app.config.get('ADMIN_PASSWORD')
        auth_service = init_auth_service(admin_password)

        # 初始化API服务
        data_path = app.config.get('DATA_PATH', './data/cards.json')
        init_api_services(data_path, auth_service)


def register_blueprints(app):
    """注册蓝图"""
    # 注册API蓝图
    app.register_blueprint(api_bp, url_prefix='/api')

    # 主页面路由
    @app.route('/')
    def index():
        return jsonify({
            'success': True,
            'message': 'Peler Panel API Server',
            'version': '1.0.0',
            'endpoints': {
                'cards': '/api/cards',
                'auth': '/api/auth',
                'icons': '/api/icons',
                'docs': '/api/docs'
            }
        })


def register_error_handlers(app):
    """注册错误处理器"""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'bad_request',
            'message': '请求参数错误',
            'details': str(error.description) if hasattr(error, 'description') else None
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 'unauthorized',
            'message': '需要认证',
            'details': str(error.description) if hasattr(error, 'description') else None
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 'forbidden',
            'message': '权限不足',
            'details': str(error.description) if hasattr(error, 'description') else None
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'not_found',
            'message': '资源不存在',
            'details': str(error.description) if hasattr(error, 'description') else None
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 'method_not_allowed',
            'message': '不支持的请求方法',
            'details': str(error.description) if hasattr(error, 'description') else None
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 'internal_server_error',
            'message': '服务器内部错误',
            'details': str(error.description) if hasattr(error, 'description') else None
        }), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """处理所有HTTP异常"""
        return jsonify({
            'success': False,
            'error': error.name.lower().replace(' ', '_'),
            'message': error.description,
            'status_code': error.code
        }), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """处理意外错误"""
        if app.config.get('DEBUG'):
            # 开发模式显示详细错误信息
            import traceback
            return jsonify({
                'success': False,
                'error': 'unexpected_error',
                'message': str(error),
                'traceback': traceback.format_exc()
            }), 500
        else:
            # 生产模式隐藏错误详情
            return jsonify({
                'success': False,
                'error': 'unexpected_error',
                'message': '发生意外错误'
            }), 500


def register_request_handlers(app):
    """注册请求处理器"""

    @app.before_request
    def before_request():
        """请求前处理"""
        # 记录请求信息（可选）
        if app.config.get('DEBUG'):
            print(f"[{request.method}] {request.url}")

    @app.after_request
    def after_request(response):
        """请求后处理"""
        # 添加CORS头（如果需要）
        if app.config.get('CORS_ENABLED', False):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

        # 确保JSON响应格式
        if response.mimetype == 'application/json':
            response.headers['Content-Type'] = 'application/json; charset=utf-8'

        return response


def main():
    """主函数，用于直接运行应用"""
    # 打印配置信息
    print_config_info()

    # 创建应用
    app = create_app()

    # 打印所有注册的路由（调试用）
    print("\n📋 已注册的路由:")
    for rule in app.url_map.iter_rules():
        print(f"   {rule.methods} {rule.rule}")

    # 获取运行配置
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = app.config.get('DEBUG', False)

    print(f"\n🚀 启动 Peler Panel 服务器...")
    print(f"   地址: http://{host}:{port}")
    print(f"   调试模式: {debug}")
    print(f"   数据文件: {app.config.get('DATA_PATH')}")
    print("=" * 50)

    # 运行应用
    app.run(host=host, port=port, debug=debug)


# 创建默认应用实例，供 Flask CLI 使用
app = create_app()

if __name__ == '__main__':
    main()