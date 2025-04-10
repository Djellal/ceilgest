from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, Course_Registration, Session, Course, CourseLevel, State, Municipality, Profession
from datetime import datetime
from app.models import AppSettings

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    settings = AppSettings.query.get(1)
    courses = Course.query.filter_by(is_active=True).all()
    return render_template('index.html', settings=settings, courses=courses)

@bp.app_errorhandler(404)
def page_not_found(e):
    settings = AppSettings.query.get(1)
    return render_template('404.html', settings=settings), 404

@bp.route('/register-course', methods=['GET', 'POST'])
@login_required
def register_course():
    if not current_user.is_student:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    settings = AppSettings.query.get(1)
    if not settings.registration_opened:
        flash('Registration is currently closed', 'warning')
        return redirect(url_for('main.index'))

    current_session = Session.query.filter_by(id=settings.current_session_id).first()
    
    # Check existing registrations
    existing_registrations = Course_Registration.query.filter_by(
        user_id=current_user.id,
        session_id=current_session.id
    ).count()
    
    if existing_registrations >= 2:
        flash('You can only register for 2 courses per session', 'warning')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            registration = Course_Registration(
                inscription_code=Course_Registration.generate_inscription_code(),
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                first_name_ar=request.form['first_name_ar'],
                last_name_ar=request.form['last_name_ar'],
                birth_date=datetime.strptime(request.form['birth_date'], '%Y-%m-%d'),
                birth_state_id=request.form['birth_state'],
                birth_municipality_id=request.form['birth_municipality'],
                address=request.form['address'],
                tel=request.form['tel'],
                profession_id=request.form['profession'],
                course_id=request.form['course'],
                course_level_id=request.form['course_level'],
                paid_fee_value=float(request.form['fee_value']),
                registration_terms_accepted='terms_accepted' in request.form,
                notes=request.form.get('notes', ''),
                user_id=current_user.id,
                session_id=current_session.id
            )
            db.session.add(registration)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')

    # Get dropdown options
    states = State.query.all()
    professions = Profession.query.all()
    courses = Course.query.filter_by(is_active=True).all()
    levels = CourseLevel.query.all()
    
    return render_template(
        'course_registration.html',
        settings=settings,
        states=states,
        professions=professions,
        courses=courses,
        levels=levels,
        current_session=current_session
    )


@bp.route('/student-dashboard')
@login_required
def student_dashboard():
    if not current_user.is_student:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    settings = AppSettings.query.get(1)
    current_session = Session.query.get(settings.current_session_id)
    
    # Get all registrations for this student
    registrations = Course_Registration.query.filter_by(
        user_id=current_user.id
    ).order_by(Course_Registration.registration_date.desc()).all()
    
    # Separate active and past registrations
    active_registrations = [r for r in registrations if r.session_id == current_session.id]
    past_registrations = [r for r in registrations if r.session_id != current_session.id]

    return render_template(
        'student_dashboard.html',
        settings=settings,
        active_registrations=active_registrations,
        past_registrations=past_registrations,
        current_session=current_session
    )


@bp.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    settings = AppSettings.query.get(1)  # Add this line to get settings
    return render_template('admin_dashboard.html', settings=settings)  # Pass settings to template
    # Add your admin dashboard statistics and data here
    return render_template('admin_dashboard.html')