from flask import jsonify, request, url_for
from app import app, db
from app.models import Question, Student, Group, Meeting, StudentMeeting, Teacher, GroupMeeting, User
from datetime import datetime

from random import randint

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
            Meeting.query.filter_by(id=meeting.id).delete()
            db.session.commit()
            result = "ok"
            error = ""
        except Exception as e:
            result = "error"
            error = str(e)

        return jsonify({"result": result, "error": error})

    else:
        return "INVALID!"
    
@app.route("/api/meeting/between/<start>/<end>")
def meetings_between(start, end):
    try:
        result = Meeting.query.filter(Meeting.date.between(start, end)).all()
        error = ""
    except Exception as e:
        result = "error"
        error = str(e)
    return jsonify({"result": result, "error": error})

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
    

# show list list of all students
@app.route('/api/student', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([{'id': student.id, 'name': student.name} for student in students])

# add a student
@app.route('/api/student', methods=['POST'])
def create_student():
    name = request.json['name']
    student = Student(name=name)
    db.session.add(student)
    db.session.commit()
    url = url_for('set_password', code=student.password_code, _external=True)
    return jsonify({'id': student.id, 'name': student.name, 'link': url})


# show a specific student
@app.route('/api/student/<int:id>', methods=['GET'])
def get_student(id):
    student = Student.query.get_or_404(id)
    return jsonify({'id': student.id, 'name': student.name})

# delete a student


@app.route('/api/student/<int:id>', methods=['DELETE'])
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
