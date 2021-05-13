from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from celery import Celery

import os
from datetime import timedelta

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", 'local-secret')
app.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///D:\hse\4 course\course-work\CourseWork2021\database\database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# celery -A source.celery worker --loglevel=DEBUG --pool=eventlet --concurrency=4
# backend=app.config['CELERY_RESULT_BACKEND']
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

from source import routes
