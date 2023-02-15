import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

LISTEN_ALL = "0.0.0.0"
FLASK_IP = LISTEN_ALL
FLASK_PORT = 81
FLASK_DEBUG = True

basedir = os.path.abspath(os.path.dirname(__file__))

# https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'databases/aanwezigheidstool.db')

app.config['SECRET_KEY'] = "Alien Software"

db = SQLAlchemy(app)


class students(db.Model):
    id = db.Column('student_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))


def __init__(self, name):
    self.name = name


class groups(db.Model):
    id = db.Column('group_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))


def __init__(self, name):
    self.name = name


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


if __name__ == "__main__":
    app.run(host=FLASK_IP, port=FLASK_PORT, debug=FLASK_DEBUG)
