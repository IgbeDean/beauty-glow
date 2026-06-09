# IMPORT NECESSARY THINGS
import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


# LOAD EVNIRONMENT VARIABLE
load_dotenv()


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


    # APPLY CONFIGURATIONS
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # DATABASE CONFIGURATIONS
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    # BIND EXTENSIONS TO APP
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)


    # CREATE DATABASE
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