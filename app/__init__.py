from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config import Config
from app.models import db
from app.session import bp as session_bp
from app.app_settings import bp as app_settings_bp

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(session_bp, url_prefix='/admin')
    app.register_blueprint(app_settings_bp)

    return app