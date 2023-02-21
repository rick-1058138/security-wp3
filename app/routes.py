from flask import jsonify, render_template, request
from app import app, db
from app.models import Student, Group, Meeting
from datetime import datetime

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


@app.route("/overview_page")
def overview_page():
    return render_template('overview_page.html')


@app.route("/welcome_page")
def welcome_page():
    return render_template('welcome_page.html')

def result_to_dict(sql_result):
    result_dict = []
    for row in sql_result:
        result_dict.append(({column.name: str(getattr(row, column.name)) for column in row.__table__.columns}))
    return result_dict

@app.route("/api/meeting/", methods=("GET", "POST", "PUT", "PATCH", "DELETE"))
@app.route("/api/meeting/<id>", methods=("GET", "POST", "PUT", "PATCH", "DELETE"))
def handle_meeting(id = None):
    if request.method == "GET":
        if id == None:
            meetings = Meeting.query.all()
            return jsonify({"result": meetings})
        else:
            meeting = Meeting.query.filter_by(meeting_id=id).first()
            return jsonify({"result": meeting})

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
        # update whole row
        return "PUT"
    elif request.method == "PATCH":
        # update part of row
        body = request.json
        try:
            meeting = Meeting.query.filter_by(meeting_id=body['id']).first()
            for item in body:
                print(item, body[item])
                # sets the column name used in request
                # result : meeting.item = body[item] // meeting.(column name) = value given
                setattr(meeting, item, body[item])

            db.session.commit()
            result = "ok"
            error = ""
        except Exception as e:
            result = "error"
            error = str(e)
        return jsonify({"result": result, "error": error})
        
    elif request.method == "DELETE":
        try:
            Meeting.query.filter_by(meeting_id=id).delete()
            db.session.commit()
            result = "ok"
            error = ""
        except Exception as e:
            result = "error"
            error = str(e)

        return jsonify({"result": result, "error": error})

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