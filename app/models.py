# models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

shanghai_tz = pytz.timezone('Asia/Shanghai')

db = SQLAlchemy()

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    create_date = db.Column(db.DateTime, default=lambda: datetime.now(shanghai_tz))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'author': self.author,
            'create_date': self.create_date.strftime('%Y-%m-%d %H:%M:%S')
        }