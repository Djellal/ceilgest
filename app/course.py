from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Course, AppSettings

bp = Blueprint('course', __name__, url_prefix='/admin')

@bp.route('/courses')
@login_required
def list_courses():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    courses = Course.query.all()
    settings = AppSettings.query.get(1)
    return render_template('course/list.html', courses=courses, settings=settings)

@bp.route('/course/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    settings = AppSettings.query.get(1)
    
    if request.method == 'POST':
        try:
            course = Course(
                code=request.form['code'],
                name=request.form['name'],
                name_ar=request.form['name_ar'],
                duration=int(request.form['duration']),
                course_type=request.form['course_type'],
                is_active='is_active' in request.form
            )
            db.session.add(course)
            db.session.commit()
            flash('Course created successfully', 'success')
            return redirect(url_for('course.list_courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating course: {str(e)}', 'danger')
    
    return render_template('course/create.html', settings=settings)

@bp.route('/course/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    course = Course.query.get_or_404(id)
    settings = AppSettings.query.get(1)
    
    if request.method == 'POST':
        try:
            course.code = request.form['code']
            course.name = request.form['name']
            course.name_ar = request.form['name_ar']
            course.duration = int(request.form['duration'])
            course.course_type = request.form['course_type']
            course.is_active = 'is_active' in request.form
            db.session.commit()
            flash('Course updated successfully', 'success')
            return redirect(url_for('course.list_courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating course: {str(e)}', 'danger')
    
    return render_template('course/edit.html', course=course, settings=settings)

@bp.route('/course/<int:id>/delete', methods=['POST'])
@login_required
def delete_course(id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    course = Course.query.get_or_404(id)
    try:
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting course: {str(e)}', 'danger')
    
    return redirect(url_for('course.list_courses'))