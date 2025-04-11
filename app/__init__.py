from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
# Remove this line: from flask_admin import Admin
from app.config import Config
from app.models import db
from app.session import bp as session_bp
from app.app_settings import bp as app_settings_bp
from app.state import bp as state_bp
from app.profession import bp as profession_bp
from app.course import bp as course_bp
from app.course_level import bp as course_level_bp
from flask_bootstrap import Bootstrap5
from flask_debugtoolbar import DebugToolbarExtension
from flask_ckeditor import CKEditor

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    bootstrap = Bootstrap5(app)
    app.config.from_object(config_class)
    ckeditor = CKEditor(app)
    
    # Remove this line: admin = Admin(app, name='Ceilgest Admin', template_mode='bootstrap4')
    
    
    
    # Enable SQL query recording
    app.config['SQLALCHEMY_RECORD_QUERIES'] = True
    
    # Debug toolbar setup
    app.config['DEBUG_TB_ENABLED'] = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    toolbar = DebugToolbarExtension(app)
    
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(session_bp, url_prefix='/admin')
    app.register_blueprint(app_settings_bp)
    app.register_blueprint(state_bp)
    app.register_blueprint(profession_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(course_level_bp)

    return app
