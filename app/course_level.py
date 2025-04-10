from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Course, CourseLevel, AppSettings

bp = Blueprint('course_level', __name__, url_prefix='/admin')

@bp.route('/course/<int:course_id>/levels')
@login_required
def list_levels(course_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    course = Course.query.get_or_404(course_id)
    settings = AppSettings.query.get(1)
    return render_template('course_level/list.html', course=course, settings=settings)

@bp.route('/course/<int:course_id>/level/create', methods=['GET', 'POST'])
@login_required
def create_level(course_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    course = Course.query.get_or_404(course_id)
    settings = AppSettings.query.get(1)
    
    if request.method == 'POST':
        try:
            level = CourseLevel(
                name=request.form['name'],
                name_ar=request.form['name_ar'],
                duration=int(request.form['duration']),
                course_id=course_id,
                previous_level_id=request.form['previous_level_id'] or None
            )
            db.session.add(level)
            db.session.commit()
            flash('Level created successfully', 'success')
            return redirect(url_for('course_level.list_levels', course_id=course_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating level: {str(e)}', 'danger')
    
    return render_template('course_level/create.html', course=course, settings=settings)

@bp.route('/level/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_level(id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    level = CourseLevel.query.get_or_404(id)
    settings = AppSettings.query.get(1)
    
    if request.method == 'POST':
        try:
            level.name = request.form['name']
            level.name_ar = request.form['name_ar']
            level.duration = int(request.form['duration'])
            level.previous_level_id = request.form['previous_level_id'] or None
            db.session.commit()
            flash('Level updated successfully', 'success')
            return redirect(url_for('course_level.list_levels', course_id=level.course_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating level: {str(e)}', 'danger')
    
    return render_template('course_level/edit.html', level=level, settings=settings)

@bp.route('/level/<int:id>/delete', methods=['POST'])
@login_required
def delete_level(id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    level = CourseLevel.query.get_or_404(id)
    course_id = level.course_id
    try:
        db.session.delete(level)
        db.session.commit()
        flash('Level deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting level: {str(e)}', 'danger')
    
    return redirect(url_for('course_level.list_levels', course_id=course_id))