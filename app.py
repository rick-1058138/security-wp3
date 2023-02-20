import os
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
# import datetime 
from datetime import datetime

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

class Meeting(db.Model):
    meeting_id = db.Column('meeting_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    start_time = db.Column(db.String(10))
    end_time = db.Column(db.String(10))
    date = db.Column(db.Date())
    status = db.Column(db.String(100))
    description = db.Column(db.Text())
    lesson_code = db.Column(db.Integer())

    # def __init__(self, name, start_time, end_time, date, status, description, lesson_code):
    #     self.name = name
    #     self.start_time = start_time
    #     self.end_time = end_time
    #     self.date = date
    #     self.status = status
    #     self.description = description
    #     self.lesson_code = lesson_code

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        db.session.add(obj)
        db.session.commit()


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

def result_to_dict(sql_result):
    result_dict = []
    for row in sql_result:
        result_dict.append(({column.name: str(getattr(row, column.name)) for column in row.__table__.columns}))
    return result_dict

@app.route("/api/meeting", methods=("GET", "POST", "PUT", "PATCH", "DELETE"))
def handle_meeting():
    if request.method == "GET":
        meetings = Meeting.query.all()
        # for meeting in meetings:
        #     print(meeting.meeting_id)
        dict = {"result": result_to_dict(meetings)}
        return jsonify(dict)
    elif request.method == "POST":
        body = request.json
        try:
            meeting = Meeting(name=body["name"], start_time=body["start_time"], end_time=body["end_time"], date=datetime.now(), status="niet begonnen", description="dit is een meeting", lesson_code=123456)
            db.session.add(meeting)
            db.session.commit()
            result = "ok"
            error = ""
        except Exception as e:
            result = "error"
            error = str(e)
        return jsonify({"result": result, "error": error})
        # return request.get_json()
    elif request.method == "PUT":
        return "PUT"
    elif request.method == "PATCH":
        return "PATCH"
    elif request.method == "DELETE":
        return "DELETE"
    else:
        return "INVALID!"

@app.route("/testmeeting")
def test_meeting():
    Meeting.create(name="test", start_time="10:00", end_time="11:00", date=datetime.date(1987, 6,16), status="niet begonnen", description="dit is een meeting", lesson_code=123456)
    return "Meeting toegevoegd"

# @app.route("/test")
# def test():
#     student = students(name='Klaas')
#     db.session.add(student)
#     db.session.commit()
#     return '1'


if __name__ == "__main__":
    app.run(host=FLASK_IP, port=FLASK_PORT, debug=FLASK_DEBUG)
