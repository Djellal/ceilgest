from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Group, Course, CourseLevel, User, Session, AppSettings  # Add AppSettings to imports
from flask_login import LoginManager
from flask import jsonify
from app.models import CourseLevel

# Remove the import from app and get login_manager from current_app instead
bp = Blueprint('group', __name__, url_prefix='/groups')

@bp.route('/')
@login_required  # This decorator will work without direct login_manager access
def index():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    settings = AppSettings.query.get(1)
    # Start with base query filtered by current session
    query = Group.query.filter_by(session_id=settings.current_session_id)
    
    # Get filter parameters from URL
    course_id = request.args.get('course_id', type=int)
    level_id = request.args.get('level_id', type=int)
    
    # Apply additional filters if provided
    if course_id:
        query = query.filter_by(course_id=course_id)
    if level_id:
        query = query.filter_by(course_level_id=level_id)
    
    groups = query.all()
    courses = Course.query.all()
    levels = CourseLevel.query.all()
    
    return render_template('group/index.html', 
                         groups=groups, 
                         settings=settings,
                         courses=courses,
                         levels=levels)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    settings = AppSettings.query.get(1)
    
    if request.method == 'POST':
        # Convert empty string to None for nullable fields
        course_level_id = request.form.get('course_level_id')
        course_level_id = int(course_level_id) if course_level_id else None
        
        group = Group(
            group_name=request.form['group_name'],
            group_name_ar=request.form['group_name_ar'],
            course_id=int(request.form['course_id']),
            course_level_id=course_level_id,
            teacher_id=int(request.form['teacher_id']),
            session_id=int(request.form.get('session_id', settings.current_session_id)),
            max_students=int(request.form['max_students'])
        )
        db.session.add(group)
        db.session.commit()
        flash('Group created successfully', 'success')
        return redirect(url_for('group.index'))
    
    courses = Course.query.all()
    teachers = User.query.filter_by(role_id=2).all()
    sessions = Session.query.all()
    return render_template('group/create.html', 
                         courses=courses, 
                         teachers=teachers, 
                         sessions=sessions,
                         settings=settings,
                         default_session_id=settings.current_session_id)  # Pass default to template

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    settings = AppSettings.query.get(1)  # Get app settings
    group = Group.query.get_or_404(id)
    
    if request.method == 'POST':
        group.group_name = request.form['group_name']
        group.group_name_ar = request.form['group_name_ar']
        group.course_id = request.form['course_id']
        group.course_level_id = request.form.get('course_level_id')
        group.teacher_id = request.form['teacher_id']
        group.session_id = request.form['session_id']
        group.max_students = request.form['max_students']
        
        db.session.commit()
        flash('Group updated successfully', 'success')
        return redirect(url_for('group.index'))
    
    courses = Course.query.all()
    teachers = User.query.filter_by(role_id=2).all()
    sessions = Session.query.all()
    levels = CourseLevel.query.filter_by(course_id=group.course_id).all()
    
    return render_template('group/edit.html', 
                         group=group,
                         courses=courses,
                         teachers=teachers,
                         sessions=sessions,
                         levels=levels,
                         settings=settings)  # Add settings to context

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    group = Group.query.get_or_404(id)
    db.session.delete(group)
    db.session.commit()
    flash('Group deleted successfully', 'success')
    return redirect(url_for('group.index'))


@bp.route('/api/courses/<int:course_id>/levels')
def get_course_levels(course_id):
    levels = CourseLevel.query.filter_by(course_id=course_id).all()
    return jsonify([{
        'id': level.id,
        'name': level.name,
        'name_ar': level.name_ar
    } for level in levels])