from datetime import datetime
from app import db

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Student('{self.name}')"


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow())
    end_date = db.Column(db.DateTime, nullable=False,
                         default=datetime.utcnow())

    def __repr__(self):
        return f"Group('{self.start_date}', '{self.end_date}')"
