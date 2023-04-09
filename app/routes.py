import time
from flask import Response, abort, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import login_user, current_user, login_required, logout_user
from app import app, db, bcrypt
from app.models import Answer, Question, Student, Group, Meeting, StudentMeeting, Teacher, GroupMeeting, TeacherMeeting, User, StudentGroup
from datetime import datetime
from random import randint
from faker import Faker


@app.errorhandler(404)
def page_not_found(e):
    # return custom 404 page when 404 error occures
    return render_template('404.html'), 404


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if current_user.admin == 0:
        flash("Je hebt geen toegang tot deze pagina.", "error")
        return redirect(url_for("home"))
    students = Student.query.all()
    groups = Group.query.all()
    # groups = db.session.query(Group).all()
    # group_list = []
    # for group in groups:
    #     print(group.name)
    #     group_list.append({
    #         "name": group.name,
    #         "id": group.id
    #     })
    return render_template("admin.html", student_list=students, group_list=groups,  # group_list=group_list
                           )


@app.route("/home")
@login_required
def home():
    meetings = Meeting.query.filter(
        Meeting.date >= datetime.today().date()).order_by(Meeting.date).limit(5).all()
    return render_template('index.html', meetings=meetings)


@app.route("/profiel")
@login_required
def profile():
    return render_template('profile.html', user=current_user)


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
            User.query.filter_by(password_code=code).exists()
        ).scalar()
        if exists:
            return render_template('set_password.html', code=code)
        else:
            abort(404)

    elif request.method == "POST":
        # form validation
        print(request.form)
        if (request.form.get('password') == request.form.get('password_confirm')):
            exists = db.session.query(
                User.query.filter_by(password_code=code).exists()
            ).scalar()
            if exists:
                user = User.query.filter_by(password_code=code).first()
            else:
                flash("Je kunt je wachtwoord niet veranderen", 'error')
                return redirect(url_for('home'))

            # Update password in db
            user.update_password(request.form.get('password'))
            # reset password code so password cant be changed again with the same code
            user.reset_password_code()
            login_user(user)
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


@app.route("/meeting/start/<code>")
@login_required
def start_presence(code=None):
    if (current_user.role == 1):
        # user is a student
        abort(404)
    # check if code exists else throw 404 not found error
    exists = db.session.query(
        Meeting.query.filter_by(meeting_code=code).exists()
    ).scalar()
    if exists:
        session['timer_length'] = 60
        session['start_time'] = time.time()

        # update status in db
        meeting = Meeting.query.filter_by(meeting_code=code).first()
        meeting.status = 1
        db.session.commit()

        # Delete old record of same meeting if it was started before ( for testing )
        StudentMeeting.query.filter_by(meeting_id=meeting.id).delete()

        # loop through all students in each group
        for group in meeting.groups:
            # print(group.group.students)
            # loop through all students in group
            for student in group.group.students:
                # print(student.student.id)
                student = StudentMeeting(
                    student_id=student.student.id, meeting_id=meeting.id, checkin_date=datetime.now(), present=False)
                db.session.add(student)
                db.session.commit()

        return redirect(url_for('presence', code=code))
    else:
        abort(404)


@app.route('/aanmelden', methods=("GET", "POST"))
@login_required
def presence_code():
    if request.method == "GET":
        return render_template('code-input.html')
    elif request.method == "POST":
        code = request.form["meeting_code"]

        # validation
        # ----------

        if (current_user.role == 1):
            # logged in student
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
            flash("Deze les code bestaat niet", 'error')
            return redirect(url_for('presence_code'))

        # check if student is invited for meeting ( checks in studentmeeting table if they exist here)
        exists = db.session.query(
            StudentMeeting.query.filter_by(
                student_id=id, meeting_id=meeting.id).exists()
        ).scalar()
        if not exists:
            flash("Je bent niet uitgenodigd voor deze bijeenkomst", 'error')
            return redirect(url_for('presence_code'))

        student = StudentMeeting.query.filter_by(
            student_id=id, meeting_id=meeting.id).first()

        print(student)
        if student.present:
            # student is already present return to home, with message
            flash("Je was al aangemeld voor deze les", 'error')
            return redirect('/')

        # ------------

        return redirect(url_for('question', code=code))
        # return redirect(url_for('setpresence', code=code))


@app.route('/aanmelden/<code>')
@login_required
def setpresence(code=None):
    # check if user is a student
    if (current_user.role == 1):
        # logged in student
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
        flash("Deze les code bestaat niet", 'error')
        return redirect(url_for('presence_code'))

    # UPDATE: if user logs in then execute below

    # check if student is invited for meeting ( checks in studentmeeting table if they exist here)
    exists = db.session.query(
        StudentMeeting.query.filter_by(
            student_id=id, meeting_id=meeting.id).exists()
    ).scalar()
    if not exists:
        flash("Je bent niet uitgenodigd voor deze bijeenkomst", 'error')
        return redirect(url_for('presence_code'))

    student = StudentMeeting.query.filter_by(
        student_id=id, meeting_id=meeting.id).first()

    print(student)
    if student.present:
        # student is already present return to home, with message
        flash("Je was al aangemeld voor deze les", 'error')
        return redirect('/')

    return redirect(url_for('question', code=code))


@app.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":

        next_url = request.args.get("next")
        username = request.form["username"]
        password = request.form["password"]
        user = db.session.query(User).filter(
            User.email == username.lower()).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            if next_url:
                url = next_url[1:]
                return redirect(url)
            return redirect(url_for("home"))
        else:
            flash("Gebruikersnaam of wachtwoord onjuist. Probeer opnieuw.", 'error')
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/les/overzicht/<meeting_code>")
@login_required
def les_overzicht(meeting_code):
    meeting = Meeting.query.filter_by(meeting_code=meeting_code).first()
    question = Question.query.filter_by(meeting_id=meeting.id).first()
    group_meetings = meeting.groups
    group_names = [
        group_meeting.group.name for group_meeting in group_meetings]
    return render_template("les_overzicht.html", meeting_code=meeting_code, meeting=meeting, question=question, groups=group_names)


@app.route("/overzicht/<id>")
@login_required
def overview_page(id=None):
    student = Student.query.filter_by(id=id).first()
    student_meetings = StudentMeeting.query.filter_by(student_id=id).all()
    return render_template('overview.html', student=student, meetings=student_meetings)


@app.route("/vraag/<code>", methods=["GET", "POST"])
@login_required
def question(code=None):
    meeting = Meeting.query.filter_by(meeting_code=code).first()
    question = Question.query.filter_by(meeting_id=meeting.id).first()
    if request.method == "GET":
        return render_template('question.html', question=question, code=code)
    elif request.method == "POST":
        print(request.form["answer"])
        answer = Answer(text=request.form["answer"], question_id=question.id)
        db.session.add(answer)
        db.session.commit()

        # update student presence in db
        student_id = current_user.student[0].id
        # update presence of student in meeting
        studentmeeting = StudentMeeting.query.filter_by(
            student_id=student_id, meeting_id=meeting.id).first()
        studentmeeting.checkin_date = datetime.now()
        studentmeeting.present = True
        db.session.commit()

        # student is added so return to home, with a message
        flash("Je bent aangemeld in de les!", 'success')
        return redirect('/')


@app.route("/faker")
def faker():
    fake = Faker()
    for _ in range(5):
        student = Student(first_name=fake.first_name(),
                          last_name=fake.last_name(), email=fake.free_email())
        db.session.add(student)
        db.session.commit()

    teacher = Teacher(first_name="Mark", last_name="Otting",
                      email="m.otting@hr.nl", admin=1)
    db.session.add(teacher)
    db.session.commit()

    groups = [
        "SWD1A", "SWD1B", "SWD1C", "SWD1D"
    ]

    for group in groups:
        group = Group(start_date=datetime.now(),
                      end_date=datetime.now(), name=group)
        db.session.add(group)
        db.session.commit()

    return "Data toegevoegd aan de database"


@app.route("/meeting/delete/<id>")
@login_required
def delete_meeting(id=None):
    if (current_user.role == 1):
        # user is a student
        abort(404)

    Meeting.query.filter_by(id=id).delete()
    # delete data of meeting in all other tables
    GroupMeeting.query.filter_by(meeting_id=id).delete()
    StudentMeeting.query.filter_by(meeting_id=id).delete()
    TeacherMeeting.query.filter_by(meeting_id=id).delete()

    db.session.commit()
    flash("Bijeenkomst verwijderd", "success")
    return redirect(url_for("rooster"))


@app.route("/lessen/zoeken")
@login_required
def search_meetings():
    return render_template("meetings.html")


@app.route("/studenten/zoeken")
@login_required
def search_students():
    return render_template("students.html")


@app.route("/klassen/zoeken")
@login_required
def search_groups():
    return render_template("groups.html")


@app.route("/klas/<id>")
@login_required
def group_detail(id=None):
    group = Group.query.filter_by(id=id).first()
    return render_template("group-detail.html", group=group)


@app.route("/docenten/zoeken")
@login_required
def search_teachers():
    return render_template("teachers.html")


# @app.route("/admin/add-student-to-group", methods=['POST'])
# @login_required
# def add_student_to_group_form():
#     group_id = request.form["admin-student-to-group-group"]
#     student_id = request.form["admin-student-to-group-student"]

#     student_group = StudentGroup(student_id=student_id, group_id=group_id)
#     db.session.add(student_group)
#     db.session.commit()
#     return redirect(url_for("admin"))


@app.route('/admin/add-students-to-group', methods=['POST'])
@login_required
def add_students_to_group():
    if not current_user.admin:
        return redirect(url_for('admin'))

    student_ids = request.form.getlist('student_ids[]')
    group_id = request.form['group_id']

    for student_id in student_ids:
        student_group = StudentGroup(student_id=student_id, group_id=group_id)
        db.session.add(student_group)

    db.session.commit()

    count = len(student_ids)
    group = Group.query.filter_by(id=group_id).first()
    flash(f'{count} Student(en) aan "{group.name}" toegevoegd', 'success')
    return redirect(url_for('admin'))


@app.route('/student_history/<student_number>')
@login_required
def student_history(student_number):
    # Get the student based on student_number
    student = Student.query.filter_by(student_number=student_number).first()

    # Check if the student exists
    if not student:
        abort(404)

    # Query the presence data
    presence_data = StudentMeeting.query.filter_by(student_id=student.id).all()

    # Pass the data to the template
    return render_template('student_history.html', presence_data=presence_data, student=student)


@app.route("/afmelden/", methods=["POST"])
@login_required
def absence():
    current_user
    meeting_code = request.form["meeting_code"]
    absence = request.form["absence"]
    meeting = Meeting.query.filter_by(meeting_code=meeting_code).first()
    exists = db.session.query(
        StudentMeeting.query.filter_by(
            student_id=current_user.student[0].id, meeting_id=meeting.id).exists()
    ).scalar()
    if exists:
        student_meeting = StudentMeeting.query.filter_by(
            student_id=current_user.student[0].id, meeting_id=meeting.id).first()
        student_meeting.signed_off = True
        student_meeting.reason = absence
        db.session.commit()
    else:
        student = StudentMeeting(student_id=current_user.student[0].id, meeting_id=meeting.id,
                                 checkin_date=datetime.now(), present=False, signed_off=True, reason=absence)
        db.session.add(student)
        db.session.commit()
    return redirect(url_for('home'))
