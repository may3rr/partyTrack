import os
import logging
from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_login import LoginManager
from config import Config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mongo = PyMongo()
login = LoginManager()
login.login_view = 'main.login'
login.login_message = '请登录以访问此页面。'

def create_app(config_class=Config):
    try:
        app = Flask(__name__)
        app.config.from_object(config_class)
        
        # 初始化扩展
        mongo.init_app(app)
        login.init_app(app)
        
        # 注册蓝图
        try:
            from app.main import bp as main_bp
            app.register_blueprint(main_bp)
        except Exception as e:
            logger.error(f"Failed to register blueprint: {str(e)}")
            raise
        
        @app.route('/health')
        def health_check():
            try:
                # 测试MongoDB连接
                mongo.db.command('ping')
                return jsonify({"status": "healthy", "database": "connected"})
            except Exception as e:
                logger.error(f"Database connection failed: {str(e)}")
                return jsonify({"status": "unhealthy", "database": "disconnected", "error": str(e)}), 500
        
        return app
        
    except Exception as e:
        logger.error(f"Application creation failed: {str(e)}")
        raise 