from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.models import db, AppSettings, Session
from flask_ckeditor import CKEditor

bp = Blueprint('app_settings', __name__)

from flask_ckeditor import CKEditor

# Initialize CKEditor in your app factory or where you initialize extensions
# ckeditor = CKEditor(app)

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
            # Handle logo upload
            if 'logo' in request.files:
                logo = request.files['logo']
                if logo.filename != '':
                    filename = secure_filename(logo.filename)
                    upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
                    os.makedirs(upload_path, exist_ok=True)
                    logo.save(os.path.join(upload_path, filename))
                    settings.organization_logo = filename
            
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
            settings.terms_and_conditions = request.form.get('terms_and_conditions', '')
            
            db.session.commit()
            flash('Settings updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating settings: {str(e)}', 'danger')
    
    return render_template('admin/settings.html', settings=settings, sessions=sessions)