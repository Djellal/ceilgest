from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, AppSettings, Session
from werkzeug.utils import secure_filename
import os

bp = Blueprint('app_settings', __name__)

@bp.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def manage_settings():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    settings = AppSettings.query.get_or_404(1)
    sessions = Session.query.all()
    
    if request.method == 'POST':
        try:
            settings.organization_name = request.form['organization_name']
            settings.address = request.form['address']
            settings.tel = request.form['tel']
            settings.email = request.form['email']
            settings.website = request.form['website']
            settings.facebook = request.form['facebook']
            settings.twitter = request.form['twitter']
            settings.linkedin = request.form['linkedin']
            settings.youtube = request.form['youtube']
            settings.current_session_id = request.form['current_session_id']
            settings.registration_opened = 'registration_opened' in request.form
            
            db.session.commit()
            flash('Settings updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating settings: {str(e)}', 'danger')
    
    return render_template('admin/settings.html', settings=settings, sessions=sessions)