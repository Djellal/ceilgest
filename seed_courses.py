from app import create_app
from app.models import db, Course, CourseLevel

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

if __name__ == '__main__':
    seed_courses()