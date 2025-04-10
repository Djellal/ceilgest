from app import create_app
from app.models import db, User, Role

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

if __name__ == '__main__':
    seed_admin()