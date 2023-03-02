from datetime import datetime
from app import db
from dataclasses import dataclass


@dataclass
class Group(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    start_date: str = db.Column(db.String(10), nullable=False)
    end_date: str = db.Column(db.String(10), nullable=False)
    name: str = db.Column(db.String(50))

    meetings = db.relationship('GroupMeeting', back_populates='group')

    def __repr__(self):
        return f"Group('{self.start_date}', '{self.end_date}')"

# many to many relationship for students and meetings
@dataclass
class StudentMeeting(db.Model):
    id:int = db.Column(db.Integer, primary_key=True)    
    student_id:int = db.Column(db.Integer, db.ForeignKey('student.id'))
    meeting_id:int = db.Column(db.Integer, db.ForeignKey('meeting.id'))
    checkin_date:str = db.Column(db.DateTime)

    student = db.relationship('Student', back_populates='meetings')
    meeting = db.relationship('Meeting', back_populates='students')
    # meetings = db.relationship('Meeting', backref='student', lazy=True)

# many to many relationship for groups and meetings
@dataclass
class GroupMeeting(db.Model):
    id:int = db.Column(db.Integer, primary_key=True)    
    group_id:int = db.Column(db.Integer, db.ForeignKey('group.id'))
    meeting_id:int = db.Column(db.Integer, db.ForeignKey('meeting.id'))

    group = db.relationship('Group', back_populates='meetings')
    meeting = db.relationship('Meeting', back_populates='groups')


@dataclass
class Student(db.Model):
    id:int = db.Column(db.Integer, primary_key=True)
    name:str = db.Column(db.String(20), nullable=False)

    meetings = db.relationship('StudentMeeting', back_populates='student')

    def __init__(self, name):
        self.name = name
            
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
    meeting_code:int = db.Column(db.Integer())
    students = db.relationship('StudentMeeting', back_populates='meeting')
    groups = db.relationship('GroupMeeting', back_populates='meeting')

    def __init__(self, name, start_time, end_time, date, status, description, meeting_code):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.date = date
        self.status = status
        self.description = description
        self.meeting_code = meeting_code

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        db.session.add(obj)
        db.session.commit()

@dataclass
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Teacher('{self.name}')"

    def __repr__(self):
        return f"Teacher('{self.name}')"