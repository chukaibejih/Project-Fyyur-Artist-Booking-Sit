import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connected to the database and implemented SQLALCHEMY_DATABASE_URI
SQLALCHEMY_DATABASE_URI = 'postgresql://Ibejih:2000money@localhost:5432/fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False

WTF_CSRF_ENABLED = False
