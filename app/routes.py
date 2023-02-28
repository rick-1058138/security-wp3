from flask import abort, flash, jsonify, redirect, render_template, request
from app import app, db
from app.models import Student, Group, Meeting, StudentMeeting
from datetime import datetime

from random import randint

@app.errorhandler(404)
def page_not_found(e):
    # return custom 404 page when 404 error occures
    return render_template('404.html'), 404

@app.route("/")
def hello_world():
    return render_template('index.html')


@app.route("/rooster")
def rooster():
    return render_template('rooster.html')

@app.route("/aanwezigheid/<code>")
def presence(code = None):
    # check if code exists else throw 404 not found error
    exists = db.session.query(
        Meeting.query.filter_by(meeting_code=code).exists()
    ).scalar()
    if exists:
        return render_template('presence.html')
    else:
        abort(404)

@app.route('/aanmelden/<code>/<user_id>')
def setpresence(code = None, user_id = None):
    # check if code exists else throw 404 not found error
    exists = db.session.query(
        Meeting.query.filter_by(meeting_code=code).exists()
    ).scalar()
    if exists:
        meeting = Meeting.query.filter_by(meeting_code=code).first()
    else:
        abort(404)

    # UPDATE: if user logs in then execute below
    # UPDATE: get user id from session
    
    # user id is from url for now, till user sessions are added

    student_present = db.session.query(
        StudentMeeting.query.filter_by(meeting_id=meeting.id, student_id=user_id).exists()
    ).scalar()
    print(student_present)
    if student_present:
        # student is already present return to home, with message
        flash("Je was al aangemeld voor deze les")
        return redirect('/')
    else:
        # add student to meeting
        student = StudentMeeting(student_id=user_id, meeting_id=meeting.id, checkin_date=datetime.now())
        db.session.add(student)
        db.session.commit()
        # student is added so return to home, with a message
        flash("Je bent aangemeld in de les!")
        return redirect('/')
    

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

@app.route("/api/studentmeeting/<code>")
def handle_studentmeeting(code = None):
    student_dict = []
    try:
        # get the meeting correlated with the meeting code
        meeting = Meeting.query.filter_by(meeting_code=code).first()
        result = meeting.students

        # loop through students objects that are in the meeting and add them to student_dict
        for row in meeting.students:
            student_dict.append(row.student)

        error = ""
    except Exception as e:
        result = "error"
        error = str(e)

    return jsonify({"result": result, "students": student_dict, "error": error})


@app.route("/api/meeting/", methods=("GET", "POST", "PUT", "PATCH", "DELETE"))
@app.route("/api/meeting/<id>", methods=("GET", "POST", "PUT", "PATCH", "DELETE"))
def handle_meeting(id=None):
    if request.method == "GET":
        if id == None:
            meetings = Meeting.query.all()
            return jsonify({"result": meetings})
        else:
            meeting = Meeting.query.filter_by(id=id).first()
            return jsonify({"result": meeting})

    elif request.method == "POST":
        body = request.json
        try:
            date_object = datetime.strptime(body['date'], '%Y-%m-%d').date()
            meeting = Meeting(name=body["name"], start_time=body["start_time"], end_time=body["end_time"], date=date_object, status="niet begonnen", description=body["description"], meeting_code=randint(10_000_000, 99_999_999))
            db.session.add(meeting)
            db.session.commit()
            result = "ok"
            error = ""
        except Exception as e:
            result = "error"
            error = str(e)
        return jsonify({"result": result, "error": error})

    elif request.method == "PUT":
        # update whole row
        return "PUT"
    elif request.method == "PATCH":
        # update part of row
        body = request.json
        try:
            meeting = Meeting.query.filter_by(id=body['id']).first()
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
            Meeting.query.filter_by(id=id).delete()
            db.session.commit()
            result = "ok"
            error = ""
        except Exception as e:
            result = "error"
            error = str(e)

        return jsonify({"result": result, "error": error})

    else:
        return "INVALID!"

# @app.route("/testmeeting")
# def test_meeting():
#     Meeting.create(name="test", start_time="10:00", end_time="11:00", date=datetime.now(), status="niet begonnen", description="dit is een meeting", meeting_code=123456)
#     return "Meeting toegevoegd"

# @app.route("/test")
# def test():
#     student = StudentMeeting(student_id=2, id=1, checkin_date=datetime.now())
#     db.session.add(student)
#     db.session.commit()
#     return 'Student aan meeting toegevoegd'

# show list list of all students


@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([{'id': student.id, 'name': student.name} for student in students])


# add a student
@app.route('/students', methods=['POST'])
def create_student():
    name = request.json['name']
    student = Student(name=name)
    db.session.add(student)
    db.session.commit()
    return jsonify({'id': student.id, 'name': student.name})


# show a specifiek student
@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    student = Student.query.get_or_404(id)
    return jsonify({'id': student.id, 'name': student.name})


# delete a student
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student {} ID: {} is verwijderd".format(student.name, student.id)})


@app.route('/api/group', methods=['GET'])
def get_group():
    group = Group.query.all()
    return jsonify({"result": group})


@app.route('/api/group', methods=['POST'])
def create_group():
    body = request.json
    group = Group(start_date=body["start_date"],
                  end_date=body["end_date"], name=body["name"])
    db.session.add(group)
    db.session.commit()
    result = "OK"
    return jsonify({"result": result})


@app.route('/api/group/<id>', methods=['PATCH'])
def update_group(id=None):
    body = request.json
    group = Group.query.filter_by(id=id).first()
    print(body)
    for item in body:
        print(item, body[item])
        setattr(group, item, body[item])
    db.session.commit()
    result = 'OK'
    return jsonify({"result": result})


@app.route('/api/group/<id>', methods=['GET'])
def get_group_by_id(id=None):
    group = Group.query.get_or_404(id)
    return jsonify({'result': group})


@app.route('/api/group/<id>', methods=['DELETE'])
def delete_group(id=None):
    group = Group.query.get_or_404(id)
    db.session.delete(group)
    db.session.commit()
    return jsonify({"message": "Group {group} is verwijderd"})
