import os
from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

LISTEN_ALL = "0.0.0.0"
FLASK_IP = LISTEN_ALL
FLASK_PORT = 81
FLASK_DEBUG = True

basedir = os.path.abspath(os.path.dirname(__file__))

# https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application

# app.config['SQLALCHEMY_DATABASE_URI'] =\
#     'sqlite:///' + os.path.join(basedir, 'databases/aanwezigheidstool.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Alien Software'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.app_context().push()
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


# class Student(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(20), nullable=False)
#     student_id = db.relationship('StudentForGroup', backref='idk', lazy=True)

#     def __repr__(self):
#         return f"Student('{self.name}')"


# class StudentsForGroup:
#     id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.Integer, db.ForeignKey(
#         'student.id'), nullable=False)
#     group_id = db.Column(db.Integer, db.ForeignKey(
#         'group.id'), nullable=False)


# class Group(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     start_date = db.Column(db.DateTime, nullable=False,
#                            default=datetime.cestnow())
#     end_date = db.Column(db.DateTime, nullable=False,
#                          defaulr=datetime.cestnow())
#     group_id = db.relationship('StudentForGroup', backref='idk', lazy=True)

#     def __repr__(self):
#         return f"Group('{self.start_date}', '{self.end_date}')"


@app.route("/")
def hello_world():
    return render_template('index.html')


@app.route("/rooster")
def rooster():
    return render_template('rooster.html')


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/code-input")
def code_input():
    return render_template("code-input.html")


@app.route("/les_overzicht")
def les_overzicht():
    return render_template("les_overzicht.html")


# @app.route("/test")
# def test():
#     student = students(name='Klaas')
#     db.session.add(student)
#     db.session.commit()
#     return '1'


if __name__ == "__main__":
    app.run(host=FLASK_IP, port=FLASK_PORT, debug=FLASK_DEBUG)
