from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Course, AppSettings
from werkzeug.utils import secure_filename
import os
from flask import current_app
from werkzeug.exceptions import RequestEntityTooLarge

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

UPLOAD_FOLDER = '/home/djellal/workspace/ceilgest/app/static/uploads/courses'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/course/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    settings = AppSettings.query.get(1)
    
    if request.method == 'POST':
        try:
            image_path = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '':
                    if file.content_length > current_app.config['MAX_CONTENT_LENGTH']:
                        flash('Image size exceeds maximum allowed limit', 'danger')
                        return render_template('course/create.html', settings=settings)
                    
                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                        file.save(os.path.join(UPLOAD_FOLDER, filename))
                        image_path = f'courses/{filename}'
                    else:
                        flash('Invalid file type. Allowed types are: png, jpg, jpeg, gif', 'danger')
                        return render_template('course/create.html', settings=settings)
            
            course = Course(
                code=request.form['code'],
                name=request.form['name'],
                name_ar=request.form['name_ar'],
                duration=int(request.form['duration']),
                course_type=request.form['course_type'],
                image=image_path,
                is_active='is_active' in request.form
            )
            db.session.add(course)
            db.session.commit()
            flash('Course created successfully', 'success')
            return redirect(url_for('course.list_courses'))
        except RequestEntityTooLarge:
            flash('File size exceeds maximum allowed limit', 'danger')
            return render_template('course/create.html', settings=settings)
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
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '':
                    if file.content_length > current_app.config['MAX_CONTENT_LENGTH']:
                        flash('Image size exceeds maximum allowed limit', 'danger')
                        return render_template('course/edit.html', course=course, settings=settings)
                    
                    if allowed_file(file.filename):
                        # Delete old image if exists
                        if course.image:
                            old_path = os.path.join(UPLOAD_FOLDER, course.image.split('/')[-1])
                            if os.path.exists(old_path):
                                os.remove(old_path)
                        
                        # Save new image
                        filename = secure_filename(file.filename)
                        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                        file.save(os.path.join(UPLOAD_FOLDER, filename))
                        course.image = f'courses/{filename}'
            
            course.code = request.form['code']
            course.name = request.form['name']
            course.name_ar = request.form['name_ar']
            course.duration = int(request.form['duration'])
            course.course_type = request.form['course_type']
            course.is_active = 'is_active' in request.form
            db.session.commit()
            flash('Course updated successfully', 'success')
            return redirect(url_for('course.list_courses'))
        except RequestEntityTooLarge:
            flash('File size exceeds maximum allowed limit', 'danger')
            return render_template('course/edit.html', course=course, settings=settings)
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