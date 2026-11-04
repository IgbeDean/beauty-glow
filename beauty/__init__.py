# IMPORT NECESSARY THINGS
import os
from flask import Flask
from decouple import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


# INITIALIZE EXTENSIONS
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app():
    # INITIALIZE THE FLASK APP
    app = Flask(__name__)

    # BASE DIRECTORY setup for local SQLite fallback
    base_dir = os.path.abspath(os.path.dirname(__file__))
    default_db_path = f"sqlite:///{os.path.join(base_dir, '../instance/beauty.db')}"

    # APPLY CONFIGURATIONS
    app.config['SECRET_KEY'] = config('SECRET_KEY', default='dev-fallback-secret-key-9988')

    # DATABASE CONFIGURATIONS
    db_uri = config('DATABASE_URL', default=config('DATABASE_URI', default=default_db_path))
    
    # Fix Render PostgreSQL scheme compatibility
    if db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # BIND EXTENSIONS TO APP
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # CREATE DATABASE TABLES
    with app.app_context():
        from beauty.models import Product
        db.create_all()
        print("✅ Database tables created (if they didn't exist).")

    # IMPORT BLUEPRINTS
    from beauty.routes.main.main_route import main
    from beauty.routes.auth.auth_route import auth
    from beauty.routes.user.user_route import user
    from beauty.routes.admin.admin_route import admin

    # REGISTER BLUEPRINTS
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(admin)

    return app