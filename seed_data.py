# Standard library imports
import email
# Third-party imports
from app import create_app
# Database models
from app.models import (
    AppSettings,
    Course,
    CourseLevel,
    Municipality,
    Profession,  # Add this import
    Role,
    State,
    User,
    db
)

def seed_app_settings():
    app = create_app()
    with app.app_context():
        if not AppSettings.query.get(1):
            default_settings = AppSettings(
                id=1,
                organization_name='CeilGest',
                address='123 Main St',
                tel='123-456-7890',
                email='ceil@univ-setif.dz',
                facebook='https://facebook.com/ceilgest',
                twitter='https://twitter.com/ceilgest',
                linkedin='https://linkedin.com/ceilgest',
                youtube='https://youtube.com/ceilgest',
                website='https://www.ceilgest.com',
                registration_opened=False
            )
            db.session.add(default_settings)
            db.session.commit()
            print("Default AppSettings created successfully!")
        else:
            print("Default AppSettings already exists")



def seed_roles():
    app = create_app()
    with app.app_context():
        # Check if roles already exist
        if Role.query.filter_by(name='Admin').first():
            print("Roles already exist in the database. Skipping seed.")
            return
            
        # Create the roles
        roles = [
            Role(name='Admin'),
            Role(name='Teacher'),
            Role(name='Student')
        ]
        
        # Add all roles to the database
        for role in roles:
            db.session.add(role)
            
        # Commit the changes
        db.session.commit()
        print("Successfully seeded roles: Admin, Teacher, Student")


def seed_admin():
    app = create_app()
    with app.app_context():
        # Create admin role if it doesn't exist
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role:
            admin_role = Role(name='Admin')
            db.session.add(admin_role)
            db.session.commit()

        # Check if admin user already exists
        if not User.query.filter_by(username='djellal').first():
            admin_user = User(
                username='djellal',
                email='djellal@univ-setif.dz',
                role_id=admin_role.id
            )
            admin_user.set_password('dhb571982')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists")

def seed_courses():
    app = create_app()
    with app.app_context():
        # Check if courses already exist
        if Course.query.filter_by(code='ENG').first():
            print("Courses already exist in the database. Skipping seed.")
            return

        # Seed English Course with levels
        english = Course(
            code='ENG',
            name='English Language',
            name_ar='اللغة الإنجليزية',
            duration=120,
            image='english_course.jpg',  # Added image
            course_type='Language',
            is_active=True
        )
        db.session.add(english)
        db.session.commit()

        # Add English levels
        levels = [
            ('A1', 'مبتدئ', 30),
            ('A2', 'ابتدائي', 30),
            ('B1', 'متوسط', 30),
            ('B2', 'فوق المتوسط', 30),
            ('C1', 'متقدم', 30)
        ]
        
        prev_level = None
        for i, (name, name_ar, duration) in enumerate(levels, 1):
            level = CourseLevel(
                name=f'Level {name}',
                name_ar=f'المستوى {name_ar}',
                duration=duration,
                course_id=english.id,
                next_level_id=None
            )
            if prev_level:
                prev_level.next_level_id = level.id
            db.session.add(level)
            prev_level = level
        
        db.session.commit()

        # Seed French Course with levels
        french = Course(
            code='FRN',
            name='French Language',
            name_ar='اللغة الفرنسية',
            duration=120,
            image='french_course.jpg',  # Added image
            course_type='Language',
            is_active=True
        )
        db.session.add(french)
        db.session.commit()

        french_levels = [
            ('Débutant', 'مبتدئ', 30),
            ('Intermédiaire', 'متوسط', 30),
            ('Avancé', 'متقدم', 30)
        ]
        
        prev_level = None
        for name, name_ar, duration in french_levels:
            level = CourseLevel(
                name=name,
                name_ar=f'المستوى {name_ar}',
                duration=duration,
                course_id=french.id,
                next_level_id=None
            )
            if prev_level:
                prev_level.next_level_id = level.id
            db.session.add(level)
            prev_level = level
        
        db.session.commit()

        # Seed Computer Skills Course
        computer = Course(
            code='COM',
            name='Computer Skills',
            name_ar='مهارات الحاسوب',
            duration=90,
            course_type='Workshop',
            is_active=True
        )
        db.session.add(computer)
        db.session.commit()

        computer_levels = [
            ('Basic', 'أساسي', 30),
            ('Intermediate', 'متوسط', 30),
            ('Advanced', 'متقدم', 30)
        ]
        
        prev_level = None
        for name, name_ar, duration in computer_levels:
            level = CourseLevel(
                name=name,
                name_ar=f'المستوى {name_ar}',
                duration=duration,
                course_id=computer.id,
                next_level_id=None
            )
            if prev_level:
                prev_level.next_level_id = level.id
            db.session.add(level)
            prev_level = level
        
        db.session.commit()

        print("Successfully seeded all courses and levels!")



def seed_locations():
    app = create_app()
    with app.app_context():
        # Check if states already exist
        if State.query.first():
            print("States already exist in the database. Skipping seed.")
            return
            
        # Create Algerian states with their municipalities
        states_data = {
            "Algiers": {
                "name_ar": "الجزائر",
                "municipalities": [
                    ("Algiers Centre", "الجزائر وسط"),
                    ("Bab El Oued", "باب الواد"),
                    ("Hussein Dey", "حسين داي"),
                    ("El Harrach", "الحراش"),
                    ("Bir Mourad Raïs", "بئر مراد رايس")
                ]
            },
            "Oran": {
                "name_ar": "وهران",
                "municipalities": [
                    ("Oran", "وهران"),
                    ("Bir El Djir", "بئر الجير"),
                    ("Es Senia", "السانية"),
                    ("Arzew", "أرزيو"),
                    ("Ain Turk", "عين الترك")
                ]
            },
            "Constantine": {
                "name_ar": "قسنطينة",
                "municipalities": [
                    ("Constantine", "قسنطينة"),
                    ("El Khroub", "الخروب"),
                    ("Hamma Bouziane", "حامة بوزيان"),
                    ("Didouche Mourad", "ديدوش مراد"),
                    ("Ain Smara", "عين سمارة")
                ]
            },
            "Annaba": {
                "name_ar": "عنابة",
                "municipalities": [
                    ("Annaba", "عنابة"),
                    ("El Bouni", "البوني"),
                    ("El Hadjar", "الحجار"),
                    ("Sidi Amar", "سيدي عمار"),
                    ("Berrahal", "برحال")
                ]
            },
            "Setif": {
                "name_ar": "سطيف",
                "municipalities": [
                    ("Setif", "سطيف"),
                    ("Ain Arnat", "عين أرنات"),
                    ("El Eulma", "العلمة"),
                    ("Ain Oulmene", "عين ولمان"),
                    ("Bougaa", "بوقاعة")
                ]
            },
            "Batna": {
                "name_ar": "باتنة",
                "municipalities": [
                    ("Batna", "باتنة"),
                    ("Tazoult", "تازولت"),
                    ("Ain Touta", "عين التوتة"),
                    ("Barika", "بريكة"),
                    ("Arris", "أريس")
                ]
            },
            "Tlemcen": {
                "name_ar": "تلمسان",
                "municipalities": [
                    ("Tlemcen", "تلمسان"),
                    ("Mansourah", "منصورة"),
                    ("Chetouane", "شتوان"),
                    ("Maghnia", "مغنية"),
                    ("Ghazaouet", "الغزوات")
                ]
            }
        }
        
        # Add states and municipalities to the database
        for state_name, state_data in states_data.items():
            state = State(name=state_name, name_ar=state_data["name_ar"])
            db.session.add(state)
            db.session.flush()  # Flush to get the state ID
            
            # Add municipalities for this state
            for muni_name, muni_name_ar in state_data["municipalities"]:
                municipality = Municipality(
                    name=muni_name,
                    name_ar=muni_name_ar,
                    state_id=state.id
                )
                db.session.add(municipality)
        
        db.session.commit()
        print(f"Successfully seeded {len(states_data)} states with their municipalities!")

def seed_professions():
    app = create_app()
    with app.app_context():
        # Check if professions already exist
        if Profession.query.first():
            print("Professions already exist in the database. Skipping seed.")
            return
            
        professions = [
            ("Student", "طالب", 4000),
            ("Externe", "خارجي", 8000),
            ("Employee", "موظف", 6000)
        ]
        
        for name, name_ar, fee_value in professions:
            profession = Profession(
                name=name,
                name_ar=name_ar,
                fee_value=fee_value
            )
            db.session.add(profession)
        
        db.session.commit()
        print("Successfully seeded professions!")

if __name__ == '__main__':
    seed_app_settings()
    seed_roles()
    seed_admin()
    seed_courses()
    seed_locations()
    seed_professions()  # Add this line