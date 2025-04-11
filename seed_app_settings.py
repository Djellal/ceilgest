import email
from app import create_app
from app.models import db, AppSettings

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

if __name__ == '__main__':
    seed_app_settings()