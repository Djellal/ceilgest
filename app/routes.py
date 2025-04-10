from flask import Blueprint, render_template
from app.models import AppSettings

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    settings = AppSettings.query.get(1)
    return render_template('index.html', settings=settings)

@bp.app_errorhandler(404)
def page_not_found(e):
    settings = AppSettings.query.get(1)
    return render_template('404.html', settings=settings), 404