from datetime import datetime
from app import db
from dataclasses import dataclass


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow())
    end_date = db.Column(db.DateTime, nullable=False,
                         default=datetime.utcnow())

    def __repr__(self):
        return f"Group('{self.start_date}', '{self.end_date}')"

# many to many relationship for students and meetings
class StudentMeeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'))
    checkin_date = db.Column(db.DateTime)

    student = db.relationship('Student', back_populates='meetings')
    meeting = db.relationship('Meeting', back_populates='students')
    # meetings = db.relationship('Meeting', backref='student', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    meetings = db.relationship('StudentMeeting', back_populates='student')

    def __repr__(self):
        return f"Student('{self.name}')"

@dataclass
class Meeting(db.Model):
    id:int = db.Column(db.Integer, primary_key=True)
    name:str = db.Column(db.String(100))
    start_time:str = db.Column(db.String(10))
    end_time:str = db.Column(db.String(10))
    date:str = db.Column(db.Date())
    status:str = db.Column(db.String(100))
    description:str = db.Column(db.Text())
    lesson_code:int = db.Column(db.Integer())
    students = db.relationship('StudentMeeting', back_populates='meeting')

    def __init__(self, name, start_time, end_time, date, status, description, lesson_code):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.date = date
        self.status = status
        self.description = description
        self.lesson_code = lesson_code

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        db.session.add(obj)
        db.session.commit()

