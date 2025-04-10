from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Profession, AppSettings

bp = Blueprint('profession', __name__, url_prefix='/admin')

@bp.route('/professions')
@login_required
def list_professions():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    professions = Profession.query.all()
    settings = AppSettings.query.get(1)
    return render_template('profession/list.html', professions=professions, settings=settings)

@bp.route('/profession/create', methods=['GET', 'POST'])
@login_required
def create_profession():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    settings = AppSettings.query.get(1)
    
    if request.method == 'POST':
        try:
            profession = Profession(
                name=request.form['name'],
                name_ar=request.form['name_ar'],
                fee_value=float(request.form['fee_value'])
            )
            db.session.add(profession)
            db.session.commit()
            flash('Profession created successfully', 'success')
            return redirect(url_for('profession.list_professions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating profession: {str(e)}', 'danger')
    
    return render_template('profession/create.html', settings=settings)

@bp.route('/profession/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_profession(id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    profession = Profession.query.get_or_404(id)
    settings = AppSettings.query.get(1)
    
    if request.method == 'POST':
        try:
            profession.name = request.form['name']
            profession.name_ar = request.form['name_ar']
            profession.fee_value = float(request.form['fee_value'])
            db.session.commit()
            flash('Profession updated successfully', 'success')
            return redirect(url_for('profession.list_professions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profession: {str(e)}', 'danger')
    
    return render_template('profession/edit.html', profession=profession, settings=settings)

@bp.route('/profession/<int:id>/delete', methods=['POST'])
@login_required
def delete_profession(id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    profession = Profession.query.get_or_404(id)
    try:
        db.session.delete(profession)
        db.session.commit()
        flash('Profession deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting profession: {str(e)}', 'danger')
    
    return redirect(url_for('profession.list_professions'))