from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Session, AppSettings
from datetime import datetime

bp = Blueprint('session', __name__)

@bp.route('/sessions')
@login_required
def list_sessions():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    sessions = Session.query.all()
    settings = AppSettings.query.get(1)  # Get settings
    return render_template('session/list.html', sessions=sessions, settings=settings)

@bp.route('/session/create', methods=['GET', 'POST'])
@login_required
def create_session():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            session = Session(
                code=request.form['code'],
                name=request.form['name'],
                name_ar=request.form['name_ar'],
                start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d'),
                end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d')
            )
            db.session.add(session)
            db.session.commit()
            flash('Session created successfully', 'success')
            return redirect(url_for('session.list_sessions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating session: {str(e)}', 'danger')
    
    return render_template('session/create.html')

@bp.route('/session/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_session(id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    session = Session.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            session.code = request.form['code']
            session.name = request.form['name']
            session.name_ar = request.form['name_ar']
            session.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
            session.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
            db.session.commit()
            flash('Session updated successfully', 'success')
            return redirect(url_for('session.list_sessions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating session: {str(e)}', 'danger')
    
    return render_template('session/edit.html', session=session)

@bp.route('/session/<int:id>/delete', methods=['POST'])
@login_required
def delete_session(id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    session = Session.query.get_or_404(id)
    try:
        db.session.delete(session)
        db.session.commit()
        flash('Session deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting session: {str(e)}', 'danger')
    
    return redirect(url_for('session.list_sessions'))