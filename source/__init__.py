from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from celery import Celery


app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "120d0d0d"
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
