from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, Role, AppSettings  # Add AppSettings to imports
from werkzeug.security import generate_password_hash, check_password_hash
from app import login_manager

bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_student:
            return redirect(url_for('main.student_dashboard'))
        return redirect(url_for('main.index'))
        
    settings = AppSettings.query.get(1)  # Add this line to get settings
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            if user.is_student:
                return redirect(url_for('main.student_dashboard'))
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html', settings=settings)  # Pass settings here

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    settings = AppSettings.query.get(1)  # Add this line to get settings
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('auth.register'))
            
        # Get Student role by name instead of using hardcoded ID
        student_role = Role.query.filter_by(name='Student').first()
        if not student_role:
            flash('Error: Student role not found in the system')
            return redirect(url_for('auth.register'))
            
        new_user = User(username=username, email=email, role_id=student_role.id)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', settings=settings)  # Pass settings here

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/admin/users', methods=['GET'])
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    # Get filter and search parameters
    role_filter = request.args.get('role')
    search_query = request.args.get('search')
    
    # Base query
    query = User.query
    
    # Apply role filter if specified
    if role_filter and role_filter != 'all':
        query = query.filter_by(role_id=role_filter)
    
    # Apply search filter if specified
    if search_query:
        query = query.filter(
            (User.username.ilike(f'%{search_query}%')) | 
            (User.email.ilike(f'%{search_query}%'))
        )
    
    users = query.all()
    roles = Role.query.all()
    settings = AppSettings.query.get(1)
    
    return render_template(
        'admin/users.html',
        users=users,
        roles=roles,
        settings=settings,
        current_role_filter=role_filter,
        current_search=search_query
    )

@bp.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    settings = AppSettings.query.get(1)
    roles = Role.query.all()

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role_id = request.form.get('role_id')

        # Validation
        if not all([username, email, password, role_id]):
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.add_user'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.add_user'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('auth.add_user'))

        # Create user
        new_user = User(
            username=username,
            email=email,
            role_id=role_id
        )
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('User created successfully', 'success')
            return redirect(url_for('auth.manage_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'danger')

    return render_template('admin/add_user.html', settings=settings, roles=roles)


@bp.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)
    settings = AppSettings.query.get(1)
    roles = Role.query.all()

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role_id = request.form.get('role_id')

        # Validate username uniqueness (if changed)
        if username != user.username and User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.edit_user', user_id=user_id))

        # Validate email uniqueness (if changed)
        if email != user.email and User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('auth.edit_user', user_id=user_id))

        # Update user
        user.username = username
        user.email = email
        user.role_id = role_id
        if password:  # Only update password if provided
            user.set_password(password)

        try:
            db.session.commit()
            flash('User updated successfully', 'success')
            return redirect(url_for('auth.manage_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'danger')

    return render_template('admin/edit_user.html', 
                         user=user, 
                         settings=settings, 
                         roles=roles)
    