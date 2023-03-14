import time
from flask import Response, abort, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import login_user, current_user, login_required, logout_user
from app import app, db
from app.models import Question, Student, Group, Meeting, StudentMeeting, Teacher, GroupMeeting, User
from datetime import datetime

from random import randint
from faker import Faker


@app.errorhandler(404)
def page_not_found(e):
    # return custom 404 page when 404 error occures
    return render_template('404.html'), 404


@app.route("/admin")
@login_required
def admin():
    return render_template("admin.html")


@app.route("/create-teacher", methods=['POST'])
def create_teacher_form():
    firstname = request.form["admin-teacher-firstname"]
    lastname = request.form["admin-teacher-lastname"]
    email = request.form["admin-teacher-email"]
    admin = False
    if request.form.getlist("admin-teacher-admin-true"):
        admin = True
    teacher = Teacher(first_name=firstname,
                      last_name=lastname, email=email, admin=admin)
    db.session.add(teacher)
    db.session.commit()
    return render_template("/admin.html")


@app.route("/home")
@login_required
def home():
    return render_template('index.html')


@app.route("/timer/start")
@login_required
def start_timer():
    # UPDATE: set timer length through form where user can choose the length
    # UPDATE: set time of starting in db ( this time can later be used to check if a student can join a meeting or if they where to late)
    session['timer_length'] = 30
    session['start_time'] = time.time()
    return str(session['start_time'])


@app.route("/timer/update")
@login_required
def update_timer():
    print('start', session['start_time'])
    print('current', time.time())

    # calculate time left on timer
    session['time_left'] = round(
        session['timer_length'] - (time.time() - session['start_time']))
    mins, secs = divmod(session['time_left'], 60)
    # format time to mm:ss
    session['timer_text'] = '{:02d}:{:02d}'.format(mins, secs)

    # UPDATE: if timer == 0 update meeting status in db

    # check if time is less then 0, then set the timer to 0
    if (session['time_left'] < 0):
        session['time_left'] = 0
        mins, secs = divmod(session['time_left'], 60)
        session['timer_text'] = '{:02d}:{:02d}'.format(mins, secs)

    return jsonify({"result": {"timetext": session['timer_text'], "time": session['time_left']}})


@app.route("/rooster")
@login_required
def rooster():
    # current logged in student id
    # print(current_user.student[0].id)

    return render_template('rooster.html')


@app.route("/wachtwoord/nieuw/<code>", methods=("GET", "POST"))
def set_password(code=None):
    if request.method == "GET":

        # Check if password code exists
        exists = db.session.query(
            Student.query.filter_by(password_code=code).exists()
        ).scalar()
        if exists:
            return render_template('set_password.html', code=code)
        else:
            abort(404)

    elif request.method == "POST":
        # form validation
        print(request.form)
        if (request.form.get('password') == request.form.get('password_confirm')):
            flash("Je wachtwoord is aangepast!", 'success')
            return redirect(url_for('home'))
        else:
            flash("Wachtwoord velden komen niet overeen!", 'error')
            return render_template('set_password.html', code=code)


@app.route("/aanwezigheid/<code>")
@login_required
def presence(code=None):
    # check if code exists else throw 404 not found error
    exists = db.session.query(
        Meeting.query.filter_by(meeting_code=code).exists()
    ).scalar()
    if exists:
        return render_template('presence.html', code=code)
    else:
        abort(404)


@app.route('/aanmelden/<code>')
@login_required
def setpresence(code=None):
    # check if code exists else throw 404 not found error

    # UPDATE: later check here if user role is student
    if(current_user.student != []):
        #logged in student
        id = current_user.student[0].id
    else:
        flash("Je kunt niet meedoen aan deze bijeenkomst", 'error')
        return redirect(url_for("home"))

    exists = db.session.query(
        Meeting.query.filter_by(meeting_code=code).exists()
    ).scalar()
    if exists:
        meeting = Meeting.query.filter_by(meeting_code=code).first()
    else:
        abort(404)

    # UPDATE: if user logs in then execute below

    student_present = db.session.query(
        StudentMeeting.query.filter_by(
            meeting_id=meeting.id, student_id=id).exists()
    ).scalar()
    print(student_present)
    if student_present:
        # student is already present return to home, with message
        flash("Je was al aangemeld voor deze les", 'error')
        return redirect('/')
    else:
        # add student to meeting
        student = StudentMeeting(
            student_id=id, meeting_id=meeting.id, checkin_date=datetime.now(), present=True)
        db.session.add(student)
        db.session.commit()
        # student is added so return to home, with a message
        flash("Je bent aangemeld in de les!", 'success')
        return redirect('/')


@app.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = db.session.query(User).filter(User.email == username).first()
        if user and password == user.password:
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Gebruikersnaam of wachtwoord onjuist. Probeer opnieuw.", 'error')
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/code-input")
@login_required
def code_input():
    return render_template("code-input.html")


@app.route("/les_overzicht")
@login_required
def les_overzicht():
    return render_template("les_overzicht.html")


@app.route("/overview_page")
@login_required
def overview_page():
    return render_template('overview_page.html')


@app.route("/welcome_page")
@login_required
def welcome_page():
    return render_template('welcome_page.html')


@app.route("/api/groupmeeting", methods=["POST"])
def handle_groupmeeting():
    if request.method == "POST":
        body = request.json
        try:
            item = GroupMeeting(
                group_id=body['group_id'], meeting_id=body['meeting_id'])
            db.session.add(item)
            db.session.commit()
            result = "ok"
            error = ""
        except Exception as e:
            result = "error"
            error = str(e)
        return jsonify({"result": result, "meeting": item, "error": error})


@app.route("/base")
@login_required
def base():
    return render_template('base.html')


@app.route("/api/studentmeeting/<code>")
def handle_studentmeeting(code=None):
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


@app.route("/api/meeting/between/<start>/<end>")
def meetings_between(start, end):
    try:
        result = Meeting.query.filter(Meeting.date.between(start, end)).all()
        error = ""
    except Exception as e:
        result = "error"
        error = str(e)
    return jsonify({"result": result, "error": error})


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
            meeting = Meeting(name=body["name"], start_time=body["start_time"], end_time=body["end_time"],
                              date=date_object, description=body["description"], meeting_code=randint(10_000_000, 99_999_999))
            db.session.add(meeting)
            db.session.commit()
            result = "ok"
            error = ""
        except Exception as e:
            result = "error"
            error = str(e)
        return jsonify({"result": result, "meeting": meeting, "error": error})

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


@app.route("/faker")
def faker():
    fake = Faker()
    for _ in range(5):
        student = Student(first_name=fake.first_name(),
                          last_name=fake.last_name(), email=fake.free_email())
        db.session.add(student)
        db.session.commit()

        teacher = Teacher(first_name=fake.first_name(), last_name=fake.last_name(
        ), email=fake.free_email(), admin=randint(0, 1))
        db.session.add(teacher)
        db.session.commit()

        group = Group(start_date=datetime.now(),
                      end_date=datetime.now(), name=fake.word())
        db.session.add(group)
        db.session.commit()

    return "Data toegevoegd aan de database"


@app.route("/testdata")
def test():
    rick = Student('Rick')
    db.session.add(rick)
    db.session.commit()

    celeste = Student("Celèste")
    db.session.add(celeste)
    sam = Student("Sam")
    db.session.add(sam)
    marinda = Student("Marinda")
    db.session.add(marinda)

    Meeting.create(name="test", start_time="10:00", end_time="11:00", date=datetime.now(
    ), status="niet begonnen", description="dit is een meeting", meeting_code=randint(10_000_000, 99_999_999))
    group = Group(start_date="2023-3-2",
                  end_date="2024-3-2", name="Klas 1")
    db.session.add(group)
    studentmeeting = StudentMeeting(
        student=rick, meeting_id=1, checkin_date=datetime.now())
    db.session.add(studentmeeting)

    db.session.commit()
    return 'Test data toegevoegd aan de database'

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
    url = url_for('set_password', code=student.password_code, _external=True)
    return jsonify({'id': student.id, 'name': student.name, 'link': url})


# show a specific student
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


# Show all teachers
@app.route('/api/teacher', methods=['GET'])
def get_teachers():
    teachers = Teacher.query.all()
    return jsonify([{'id': teacher.id, 'name': teacher.name} for teacher in teachers])

# Add teacher


@app.route('/api/teacher', methods=['POST'])
def create_teacher():
    name = request.json['name']
    teacher = Teacher(name=name)
    db.session.add(teacher)
    db.session.commit()
    return jsonify({'id': teacher.id, 'name': teacher.name})

# Show specific teacher


@app.route('/api/teacher/<int:id>', methods=['GET'])
def get_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    return jsonify({'id': teacher.id, 'name': teacher.name})

# Delete teacher


@app.route('/api/teacher/<int:id>', methods=['DELETE'])
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    return jsonify({"message": "Docent {} ID: {} is verwijderd".format(teacher.name, teacher.id)})

# Update teacher


@app.route('/api/teacher/<int:id>', methods=['PUT'])
def update_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    teacher.name = request.json['name']
    db.session.commit()
    return jsonify({'id': teacher.id, 'name': teacher.name})


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


@app.route('/api/question/', methods=['POST'])
def create_question():
    body = request.json
    question = Question(text=body["text"], meeting_id=body["meeting_id"])
    db.session.add(question)
    db.session.commit()
    result = "ok"
    return jsonify({'text': question.text, 'id': question.meeting_id, 'result': result})


@app.route('/api/question/<id>', methods=['PUT'])
def update_question(id):
    question = Question.query.get_or_404(id)
    question.text = request.json['text']
    db.session.commit()
    return jsonify({'text': question.text, 'id': question.meeting_id, })


@app.route('/api/question/<id>', methods=['GET'])
def get_question_by_id(id=None):
    question = Question.query.get_or_404(id)
    return jsonify({'result': question})


@app.route('/api/question/<id>', methods=['DELETE'])
def delete_question(id):
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({"message": "Vraag ID: {} is verwijderd"})
