from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery

app = Flask(__name__)

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///D:\hse\4 course\course-work\CourseWork2021\database\database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# celery -A source.celery worker --loglevel=DEBUG --pool=eventlet --concurrency=4
# backend=app.config['CELERY_RESULT_BACKEND']
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

db = SQLAlchemy(app)

from source import routes
