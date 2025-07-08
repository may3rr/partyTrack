import os
import click
from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash

from config import Config

mongo = PyMongo()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = '请登录以访问此页面。'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化 MongoDB
    mongo.init_app(app)
    login_manager.init_app(app)

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.cli.command("create-admin")
    @click.argument("username")
    @click.argument("password")
    def create_admin(username, password):
        """Creates a new admin user."""
        with app.app_context():
            if mongo.db.users.find_one({"username": username}):
                print(f"Admin user {username} already exists.")
                return
            
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_admin = {
                "username": username,
                "password_hash": hashed_password,
                "is_admin": True
            }
            mongo.db.users.insert_one(new_admin)
            print(f"Admin user {username} created successfully.")

    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow()}

    return app 