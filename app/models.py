from datetime import datetime
from app import db
from dataclasses import dataclass
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, Text, Time, Date
from sqlalchemy.orm import relationship


import random
import string





@dataclass
class Group(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    name: str = db.Column(db.String(50))

    group_meetings = db.relationship('GroupMeeting', back_populates='group')
    student_groups = db.relationship('StudentGroup', back_populates='group')

    def __repr__(self):
        return f"Group('{self.start_date}', '{self.end_date}')"

# many to many relationship for students and meetings
@dataclass
class StudentMeeting(db.Model):
    id:int = db.Column(db.Integer, primary_key=True)    
    student_id:int = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    meeting_id:int = db.Column(db.Integer, db.ForeignKey('meeting.id'), nullable=False)
    checkin_date:str = db.Column(db.DateTime)
    present  = db.Column(db.Boolean, nullable=False)

    student = db.relationship('Student', back_populates='meetings')
    meeting = db.relationship('Meeting', back_populates='students')
    # meetings = db.relationship('Meeting', backref='student', lazy=True)

# many to many relationship for groups and meetings
@dataclass
class GroupMeeting(db.Model):
    id:int = db.Column(db.Integer, primary_key=True)    
    group_id:int = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    meeting_id:int = db.Column(db.Integer, db.ForeignKey('meeting.id'), nullable=False)

    group = db.relationship('Group', back_populates='meetings')
    meeting = db.relationship('Meeting', back_populates='groups')


@dataclass
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student_number = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    student_groups = db.relationship('StudentGroup', back_populates='student')
    student_meeting = db.relationship('StudentMeeting', back_populates='student')
    user = db.relationship('User', back_populates='student')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"Student('{self.full_name}')"


    def __init__(self, name):
        self.name = name
        # create random password and password code 
        characters = string.ascii_letters + string.digits
        self.password = ''.join(random.choice(characters) for i in range(60))
        self.password_code = ''.join(random.choice(characters) for i in range(15))

            
    def __repr__(self):
        return f"Student('{self.name}')"

@dataclass
class Meeting(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(100), nullable=False)
    start_time: datetime.time = db.Column(db.Time(), nullable=False)
    end_time: datetime.time = db.Column(db.Time(), nullable=False)
    date: datetime.date = db.Column(db.Date(), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='moet nog starten')
    description: str = db.Column(db.Text(), nullable=False)
    meeting_code: int = db.Column(db.Integer(), nullable=False, unique=True)

    students = db.relationship('StudentMeeting', back_populates='meeting')
    groups = db.relationship('GroupMeeting', back_populates='meeting')
    teacher = db.relationship('TeacherMeeting', back_populates='meeting')
    answer = db.relationship('Question', back_populates='meeting')

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    teacher_meetings = db.relationship('TeacherMeeting', back_populates='teacher')
    user = db.relationship('User', back_populates='teacher')
    

@dataclass
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    password_code = db.Column(db.String(255))
    admin = db.Column(db.Boolean, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)

    student = db.relationship('Student', back_populates='user',)
    teacher = db.relationship('Teacher', back_populates='user',)

@dataclass
class StudentGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)

    group = db.relationship('Group', back_populates='student_groups')
    student = db.relationship('Student', back_populates='student_groups')

@dataclass
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)

    meeting = db.relationship('Meeting', back_populates='questions')

@dataclass
class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)

    question = db.relationship('Question', back_populates='answers')

@dataclass
class TeacherMeeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer(), db.ForeignKey('group.id'), nullable=False)
    teacher_id = db.Column(db.Integer(), db.ForeignKey('teacher.id'), nullable=False)
    meeting_id = db.Column(db.Integer(), db.ForeignKey('meeting.id'), nullable=False)

    meeting = db.relationship('Meeting', back_populates='teacher_meeting')
    teacher = db.relationship('Teacher', back_populates='teacher_meeting')
    group = db.relationship('Group', back_populates='teacher_meeting')