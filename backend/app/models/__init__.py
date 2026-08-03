from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models here
from .models import Question, Topic

# Make models available at package level
__all__ = ['Question', 'Topic', 'db']