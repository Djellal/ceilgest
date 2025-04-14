from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import db, Course_Registration, Session, Course, CourseLevel, State, Municipality, Profession, Group
from datetime import datetime
from app.models import AppSettings, User  # Add User to imports
import pdfkit
from flask import make_response
from functools import wraps  # Add this import

bp = Blueprint('main', __name__)

# Add admin_required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access denied', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

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
            # Redirect to view-registration page instead of index
            return redirect(url_for('main.view_registration', registration_id=registration.id))
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
    
    # Add this line to get active courses
    courses = Course.query.filter_by(is_active=True).all()
    
    registrations = Course_Registration.query.filter_by(
        user_id=current_user.id
    ).order_by(Course_Registration.registration_date.desc()).all()
    
    active_registrations = [r for r in registrations if r.session_id == current_session.id]
    past_registrations = [r for r in registrations if r.session_id != current_session.id]

    return render_template(
        'student_dashboard.html',
        settings=settings,
        active_registrations=active_registrations,
        past_registrations=past_registrations,
        current_session=current_session,
        courses=courses  # Add this parameter
    )


@bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    settings = AppSettings.query.get(1)
    
    # Calculate statistics
    stats = {
        'total_users': User.query.count(),
        # Fix the students count - assuming is_student is a property or column
        'students_count': User.query.filter(User.is_student == True).count(),
        'active_courses': Course.query.filter_by(is_active=True).count(),
        'total_levels': CourseLevel.query.count(),
        'current_registrations': Course_Registration.query.filter_by(session_id=settings.current_session_id).count(),
        'validated_registrations': Course_Registration.query.filter_by(
            session_id=settings.current_session_id, 
            registration_validated=True
        ).count(),
        'total_revenue': db.session.query(db.func.sum(Course_Registration.paid_fee_value)).filter_by(
            session_id=settings.current_session_id
        ).scalar() or 0
    }
    
    # Get recent registrations
    recent_registrations = Course_Registration.query.order_by(
        Course_Registration.registration_date.desc()
    ).limit(5).all()
    
    return render_template(
        'admin_dashboard.html',
        settings=settings,
        stats=stats,
        recent_registrations=recent_registrations
    )


@bp.route('/about')
def about():
    settings = AppSettings.query.get(1)  # Get settings from database
    return render_template('about.html', settings=settings)


@bp.route('/admin/registrations')
@login_required
def admin_registrations():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    settings = AppSettings.query.get(1)
    
    # Get filter parameters
    search = request.args.get('search', '')
    session_id = request.args.get('session_id', type=int)
    course_id = request.args.get('course_id', type=int)
    level_id = request.args.get('level_id', type=int)
    group_id = request.args.get('group_id', type=int)
    status = request.args.get('status')  # Add status parameter
    
    # Default to current session if no session filter
    if not session_id:
        session_id = settings.current_session_id
    
    # Build query
    query = Course_Registration.query
    
    if search:
        query = query.filter(
            db.or_(
                Course_Registration.first_name.ilike(f'%{search}%'),
                Course_Registration.last_name.ilike(f'%{search}%'),
                Course_Registration.inscription_code.ilike(f'%{search}%'),
                Course_Registration.tel.ilike(f'%{search}%')
            )
        )
    
    if session_id:
        query = query.filter(Course_Registration.session_id == session_id)
    
    if course_id:
        query = query.filter(Course_Registration.course_id == course_id)
    
    if level_id:
        query = query.filter(Course_Registration.course_level_id == level_id)
    
    if group_id:
        query = query.filter(Course_Registration.group_id == group_id)
    
    # Add status filter
    if status == 'validated':
        query = query.filter(Course_Registration.registration_validated == True)
    elif status == 'pending':
        query = query.filter(Course_Registration.registration_validated == False)
    
    registrations = query.order_by(Course_Registration.registration_date.desc()).all()
    
    # Handle Excel export
    if request.args.get('export') == 'excel':
        try:
            import pandas as pd
            from io import BytesIO
            from flask import send_file
            
            # Create DataFrame
            data = []
            for reg in registrations:
                data.append({
                    'Code': reg.inscription_code,
                    'First Name': reg.first_name,
                    'Last Name': reg.last_name,
                    'Phone': reg.tel,
                    'Course': reg.course.name,
                    'Level': reg.course_level.name if reg.course_level else 'N/A',
                    'Session': reg.session.name,
                    'Group': reg.group.group_name if reg.group else 'Not assigned',
                    'Fee': reg.paid_fee_value,
                    'Registration Date': reg.registration_date.strftime('%d/%m/%Y'),
                    'Validated': 'Yes' if reg.registration_validated else 'No'
                })
            
            df = pd.DataFrame(data)
            
            # Create Excel file
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Registrations', index=False)
                worksheet = writer.sheets['Registrations']
                
                # Format the worksheet
                for i, col in enumerate(df.columns):
                    column_len = max(df[col].astype(str).map(len).max(), len(col) + 2)
                    worksheet.set_column(i, i, column_len)
            
            output.seek(0)
            
            # Generate filename with date
            from datetime import datetime
            filename = f"registrations_{datetime.now().strftime('%Y%m%d')}.xlsx"
            
            return send_file(
                output, 
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
        except ImportError:
            flash('Excel export requires pandas and xlsxwriter packages', 'warning')
            return redirect(url_for('main.admin_registrations'))
    
    # Get dropdown options for filters
    sessions = Session.query.all()
    courses = Course.query.all()
    levels = CourseLevel.query.all()
    groups = Group.query.all()
    
    return render_template('admin/registrations.html',
                          settings=settings,
                          registrations=registrations,
                          sessions=sessions,
                          courses=courses,
                          levels=levels,
                          groups=groups)


@bp.route('/edit-registration/<int:registration_id>', methods=['GET', 'POST'])
@login_required
def edit_registration(registration_id):
    registration = Course_Registration.query.get_or_404(registration_id)
    settings = AppSettings.query.get(1)
    
    # Check permissions
    if not (current_user.is_admin or 
            (current_user.is_student and 
             current_user.id == registration.user_id and 
             registration.session_id == settings.current_session_id)):
        flash('You cannot edit this registration', 'danger')
        return redirect(url_for('main.student_dashboard'))

    if request.method == 'POST':
        try:
            # Update editable fields
            registration.address = request.form['address']
            registration.tel = request.form['tel']
            registration.notes = request.form.get('notes', '')
            
            # Only update validation if admin
            if current_user.is_admin:
                registration.registration_validated = 'registration_validated' in request.form
                # Add this line to update paid_fee_value
                if 'paid_fee_value' in request.form:
                    registration.paid_fee_value = float(request.form.get('paid_fee_value', registration.paid_fee_value))
            
            # Handle course changes - only if not validated or admin
            if 'course' in request.form and (current_user.is_admin or not registration.registration_validated):
                new_course_id = int(request.form['course'])
                registration.course_id = new_course_id
                
                # If admin is changing course level
                if current_user.is_admin and 'course_level' in request.form:
                    registration.course_level_id = int(request.form['course_level'])
                # If student is changing course, set appropriate level
                elif current_user.id == registration.user_id and new_course_id != registration.course_id:
                    # Find the first level for this course
                    first_level = CourseLevel.query.filter_by(course_id=new_course_id).order_by(CourseLevel.level_order).first()
                    if first_level:
                        registration.course_level_id = first_level.id
            
            db.session.commit()
            flash('Registration updated successfully', 'success')
            if current_user.is_admin:
                return redirect(url_for('main.admin_registrations'))
            elif current_user.is_teacher:
                return redirect(url_for('main.teacher_dashboard'))
            else:
                return redirect(url_for('main.student_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating registration: {str(e)}', 'danger')

    # Get dropdown options
    states = State.query.all()
    professions = Profession.query.all()
    courses = Course.query.filter_by(is_active=True).all()
    levels = CourseLevel.query.all()
    
    return render_template(
        'edit_registration.html',
        settings=settings,
        registration=registration,
        states=states,
        professions=professions,
        courses=courses,
        levels=levels
    )


@bp.route('/api/municipalities')
def get_municipalities():
    state_id = request.args.get('state_id')
    municipalities = Municipality.query.filter_by(state_id=state_id).all()
    return jsonify([{'id': m.id, 'name': m.name} for m in municipalities])


@bp.route('/view-registration/<int:registration_id>')
@login_required
def view_registration(registration_id):
    registration = Course_Registration.query.get_or_404(registration_id)
    settings = AppSettings.query.get(1)
    
    # Check permissions
    if not (current_user.is_admin or 
            (current_user.is_student and current_user.id == registration.user_id)):
        flash('Access denied', 'danger')
        return redirect(url_for('main.student_dashboard'))
    
    return render_template('view_registration.html',
                         registration=registration,
                         settings=settings)


@bp.route('/registration/<int:registration_id>/pdf')
@login_required
def generate_registration_pdf(registration_id):
    registration = Course_Registration.query.get_or_404(registration_id)
    settings = AppSettings.query.get(1)  # Add this line to get settings
    
    # Check permissions
    if not (current_user.is_admin or current_user.id == registration.user_id):
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    # Render HTML template with current datetime
    from datetime import datetime
    html = render_template(
        'pdf/registration.html', 
        registration=registration,
        settings=settings,  # Add this line
        now=datetime.now()
    )
    
    # PDF options
    options = {
        'page-size': 'A4',
        'margin-top': '0.25in',
        'margin-right': '0.25in',
        'margin-bottom': '0.25in',
        'margin-left': '0.25in',
        'encoding': "UTF-8",
    }
    
    # Generate PDF
    pdf = pdfkit.from_string(html, False, options=options)
    
    # Create response
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=registration_{registration.inscription_code}.pdf'
    
    return response


@bp.route('/admin/courses')
@login_required
@admin_required
def admin_courses():
    settings = AppSettings.query.get(1)
    courses = Course.query.all()
    return render_template('admin/courses.html', settings=settings, courses=courses)

@bp.route('/admin/users')
@login_required
@admin_required
def admin_users():
    settings = AppSettings.query.get(1)
    users = User.query.all()
    return render_template('admin/users.html', settings=settings, users=users)

@bp.route('/admin/settings')
@login_required
@admin_required
def admin_settings():
    settings = AppSettings.query.get(1)
    return render_template('admin/settings.html', settings=settings)

