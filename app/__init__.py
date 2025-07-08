import os
import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash

from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = '请登录以访问此页面。'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Import models here to ensure they are registered with SQLAlchemy
    from app import models

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': models.User, 'Member': models.Member, 'Submission': models.Submission}

    @app.cli.command("create-admin")
    @click.argument("username")
    @click.argument("password")
    def create_admin(username, password):
        """Creates a new admin user."""
        with app.app_context():
            from app.models import User
            if User.query.filter_by(username=username).first():
                print(f"Admin user {username} already exists.")
                return
            
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_admin = User(username=username, password_hash=hashed_password)
            db.session.add(new_admin)
            db.session.commit()
            print(f"Admin user {username} created successfully.")

    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow()}

    return app 