from datetime import datetime
from app import db, login_manager
from dataclasses import dataclass
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, Text, Time, Date
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from app import bcrypt


import random
import string


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)

    return user


@dataclass
class Group(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    start_date: datetime.date = db.Column(db.Date, nullable=False)
    end_date: datetime.date = db.Column(db.Date, nullable=False)
    name: str = db.Column(db.String(50))

    meetings = db.relationship('GroupMeeting', back_populates='group')
    students = db.relationship('StudentGroup', back_populates='group')

    def __repr__(self):
        return f"Group('{self.start_date}', '{self.end_date}')"

    def __init__(self, start_date, end_date, name):
        self.start_date = start_date
        self.end_date = end_date
        self.name = name


# many to many relationship for students and meetings
@dataclass
class StudentMeeting(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)

    student_id: int = db.Column(
        db.Integer, db.ForeignKey('student.id'), nullable=False)
    meeting_id: int = db.Column(
        db.Integer, db.ForeignKey('meeting.id'), nullable=False)
    checkin_date: str = db.Column(db.DateTime)
    present: bool = db.Column(db.Boolean, nullable=False)
    signed_off: bool = db.Column(db.Boolean, nullable=False)
    reason: str = db.Column(db.String(500), nullable=False)

    student = db.relationship('Student', back_populates='meetings')
    meeting = db.relationship('Meeting', back_populates='students')
    # meetings = db.relationship('Meeting', backref='student', lazy=True)

    def __init__(self, student_id, meeting_id, checkin_date, present, reason, signed_off=False):
        self.student_id = student_id
        self.meeting_id = meeting_id
        self.checkin_date = checkin_date
        self.present = present
        self.signed_off = signed_off
        self.reason = reason


# many to many relationship for groups and meetings


@dataclass
class GroupMeeting(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    group_id: int = db.Column(
        db.Integer, db.ForeignKey('group.id'), nullable=False)
    meeting_id: int = db.Column(
        db.Integer, db.ForeignKey('meeting.id'), nullable=False)

    group = db.relationship('Group', back_populates='meetings')
    meeting = db.relationship('Meeting', back_populates='groups')


@dataclass
class Student(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    student_number: int = db.Column(db.String(20), nullable=False)
    first_name: str = db.Column(db.String(50), nullable=False)
    last_name: str = db.Column(db.String(50), nullable=False)

    groups = db.relationship('StudentGroup', back_populates='student')
    meetings = db.relationship('StudentMeeting', back_populates='student')
    user = db.relationship('User', back_populates='student')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"Student('{self.full_name}')"

    def __init__(self, first_name, last_name, email, student_number=None):
        user = User(email=email, role=1, admin=False)
        db.session.add(user)
        db.session.commit()
        self.first_name = first_name
        self.last_name = last_name

        if student_number == None:
            self.student_number = random.randint(1_000_000, 9_999_999)
        else:
            self.student_number = student_number
        self.user_id = user.id


@dataclass
class Meeting(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(100), nullable=False)
    start_time: str = db.Column(db.String(20), nullable=False)
    end_time: str = db.Column(db.String(20), nullable=False)
    date: datetime.date = db.Column(db.Date(), nullable=False)
    # status: 0 = not started yet - 1 = started - 2 = ended
    status: int = db.Column(db.Integer, nullable=False, default=0)
    description: str = db.Column(db.Text(), nullable=False)
    meeting_code: int = db.Column(db.Integer(), nullable=False, unique=True)

    students = db.relationship('StudentMeeting', back_populates='meeting')
    groups = db.relationship('GroupMeeting', back_populates='meeting')
    teachers = db.relationship('TeacherMeeting', back_populates='meeting')
    question = db.relationship('Question', back_populates='meeting')

    def __init__(self, name, start_time, end_time, date, description, meeting_code):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.date = date
        self.description = description
        self.meeting_code = meeting_code

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        db.session.add(obj)
        db.session.commit()


@dataclass
class Teacher(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name: str = db.Column(db.String(50), nullable=False)
    last_name: str = db.Column(db.String(50), nullable=False)

    meetings = db.relationship('TeacherMeeting', back_populates='teacher')
    user = db.relationship('User', back_populates='teacher')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __init__(self, first_name, last_name, email, admin):
        user = User(email=email, role=0, admin=admin)
        db.session.add(user)
        db.session.commit()
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user.id


@dataclass
class User(UserMixin, db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    email: str = db.Column(db.String(255), unique=True, nullable=False)
    password: str = db.Column(db.String(255), nullable=False)
    password_code: str = db.Column(db.String(255))
    admin: bool = db.Column(db.Boolean, nullable=False)
    # role: 0 = teacher, 1 = student
    role: int = db.Column(db.Integer, nullable=False)
    created_date = db.Column(
        db.DateTime, nullable=False, default=datetime.now())

    student = db.relationship('Student', back_populates='user',)
    teacher = db.relationship('Teacher', back_populates='user',)

    def __init__(self, email, role, admin=False):
        self.email = email
        # create random password and password code
        characters = string.ascii_letters + string.digits
        # password = ''.join(random.choice(characters) for i in range(60))
        password = bcrypt.generate_password_hash("werkplaats3")
        password_code = ''.join(random.choice(characters) for i in range(15))

        self.role = role
        self.password = password
        self.password_code = password_code
        self.admin = admin

    def update_password(self, password):
        self.password = bcrypt.generate_password_hash(password)
        db.session.commit()

    def reset_password_code(self):
        # create random password and password code
        characters = string.ascii_letters + string.digits
        password_code = ''.join(random.choice(characters) for i in range(15))
        self.password_code = password_code
        db.session.commit()

    def remove_password_code(self):
        self.password_code = None
        db.session.commit()


@dataclass
class StudentGroup(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    student_id: int = db.Column(
        db.Integer, db.ForeignKey('student.id'), nullable=False)
    group_id: int = db.Column(
        db.Integer, db.ForeignKey('group.id'), nullable=False)

    group = db.relationship('Group', back_populates='students')
    student = db.relationship('Student', back_populates='groups')

    def __init__(self, student_id, group_id):
        self.student_id = student_id
        self.group_id = group_id


@dataclass
class Question(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    meeting_id: int = db.Column(
        db.Integer, db.ForeignKey('meeting.id'), nullable=False)
    text: str = db.Column(db.String(500), nullable=False)

    meeting = db.relationship('Meeting', back_populates='question')
    answers = db.relationship('Answer', back_populates='question')

    def __init__(self, text, meeting_id):
        self.text = text
        self.meeting_id = meeting_id


@dataclass
class Answer(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    text: str = db.Column(db.String(255))
    question_id: int = db.Column(
        db.Integer, db.ForeignKey('question.id'), nullable=False)

    question = db.relationship('Question', back_populates='answers')

    def __init__(self, text, question_id):
        self.text = text
        self.question_id = question_id


@dataclass
class TeacherMeeting(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    teacher_id: int = db.Column(
        db.Integer(), db.ForeignKey('teacher.id'), nullable=False)
    meeting_id: int = db.Column(
        db.Integer(), db.ForeignKey('meeting.id'), nullable=False)

    meeting = db.relationship('Meeting', back_populates='teachers')
    teacher = db.relationship('Teacher', back_populates='meetings')
