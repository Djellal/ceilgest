from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    users = db.relationship('User', backref='role', lazy=True)

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    name_ar = db.Column(db.String(100), nullable=False)  # Arabic name
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<Session {self.code} - {self.name}>'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))  # Increase length to 256
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False, default=1)  # Default to Student

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role.name == 'Admin'

    @property
    def is_teacher(self):
        return self.role.name == 'Teacher'

    @property
    def is_student(self):
        return self.role.name == 'Student'


class AppSettings(db.Model):
    __tablename__ = 'app_settings'
    id = db.Column(db.Integer, primary_key=True)
    organization_name = db.Column(db.String(100), nullable=False, default='Ceilgest')
    organization_logo = db.Column(db.String(255))  # Path to image file
    address = db.Column(db.Text)
    tel = db.Column(db.String(20))
    email = db.Column(db.String(100))
    website = db.Column(db.String(100))
    facebook = db.Column(db.String(100))
    twitter = db.Column(db.String(100))
    linkedin = db.Column(db.String(100))
    youtube = db.Column(db.String(100))
    current_session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    registration_opened = db.Column(db.Boolean, default=False)
    terms_and_conditions = db.Column(db.Text)  # New field for terms and conditions
    
    current_session = db.relationship('Session', backref='app_settings')
    
    def __repr__(self):
        return f'<AppSettings {self.organization_name}>'


class State(db.Model):
    __tablename__ = 'states'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    name_ar = db.Column(db.String(300), nullable=False)
    municipalities = db.relationship('Municipality', backref='state', lazy=True)

    def __repr__(self):
        return f'<State {self.name}>'

class Municipality(db.Model):
    __tablename__ = 'municipalities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    name_ar = db.Column(db.String(300), nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('states.id'), nullable=False)

    def __repr__(self):
        return f'<Municipality {self.name}>'

class Profession(db.Model):
    __tablename__ = 'professions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    name_ar = db.Column(db.String(300), nullable=False)
    fee_value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Profession {self.name}>'


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(300), nullable=False)
    name_ar = db.Column(db.String(300), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255))  # Path to image file
    course_type = db.Column(db.Enum('Language', 'Workshop', name='course_type'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f'<Course {self.code} - {self.name}>'

class CourseLevel(db.Model):
    __tablename__ = 'course_levels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    name_ar = db.Column(db.String(300), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    next_level_id = db.Column(db.Integer, db.ForeignKey('course_levels.id'))
    
    course = db.relationship('Course', backref='levels')
    next_level = db.relationship('CourseLevel', remote_side=[id])
    
    def __repr__(self):
        return f'<CourseLevel {self.name}>'


class Course_Registration(db.Model):
    __tablename__ = 'course_registrations'
    id = db.Column(db.Integer, primary_key=True)
    inscription_code = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    first_name_ar = db.Column(db.String(100), nullable=False)
    last_name_ar = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    birth_state_id = db.Column(db.Integer, db.ForeignKey('states.id'), nullable=False)
    birth_municipality_id = db.Column(db.Integer, db.ForeignKey('municipalities.id'), nullable=False)
    address = db.Column(db.Text, nullable=False)
    tel = db.Column(db.String(20), nullable=False)
    profession_id = db.Column(db.Integer, db.ForeignKey('professions.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    course_level_id = db.Column(db.Integer, db.ForeignKey('course_levels.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    notes = db.Column(db.Text)
    paid_fee_value = db.Column(db.Float, nullable=False)
    registration_terms_accepted = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)  # Changed to nullable

    birth_state = db.relationship('State')
    birth_municipality = db.relationship('Municipality')
    profession = db.relationship('Profession')
    course = db.relationship('Course')
    course_level = db.relationship('CourseLevel')
    user = db.relationship('User')
    session = db.relationship('Session')

    def __repr__(self):
        return f'<Course_Registration {self.inscription_code}>'

    @staticmethod
    def generate_inscription_code():
        from datetime import datetime
        return f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), nullable=False)
    group_name_ar = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    course_level_id = db.Column(db.Integer, db.ForeignKey('course_levels.id'), nullable=True)  # Changed to nullable
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    max_students = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
    onupdate=db.func.current_timestamp())

    # Relationships
    course = db.relationship('Course')
    course_level = db.relationship('CourseLevel')
    teacher = db.relationship('User')
    session = db.relationship('Session')
    students = db.relationship('Course_Registration', backref='group', lazy=True)

    def __repr__(self):
        return f'<Group {self.group_name} - {self.course.name}>'