from flask import Blueprint, render_template
from app.models import AppSettings

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    settings = AppSettings.query.get(1)  # Get the first settings record
    return render_template('index.html', settings=settings)