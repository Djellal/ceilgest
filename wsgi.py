import sys
import os

# Add the application directory to the Python path
sys.path.insert(0, '/home/djellal/workspace/ceilgest')

# Import the app object from your app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == '__main__':
    application.run()