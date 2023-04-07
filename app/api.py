from flask import jsonify, request, url_for
from app import app, db
from app.models import Question, Student, Group, Meeting, StudentMeeting, Teacher, GroupMeeting, TeacherMeeting, User, StudentGroup
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
        try:
            meeting = Meeting.query.get_or_404(id)
            meeting.name = request.json['name']
            meeting.start_time = request.json['start_time']
            meeting.end_time = request.json['end_time']
            meeting.date = datetime.strptime(request.json['date'], '%Y-%m-%d').date()
            meeting.description = request.json['description']
            db.session.commit()
            result = "ok"
            error = ""
        except Exception as e:
            result = "error"
            error = str(e)

        return jsonify({'result': result, "error": error})
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
        return jsonify({"result": "error", "error": "invalid method"})
    
@app.route("/api/meeting/between/<start>/<end>")
def meetings_between(start, end):
    try:
        result = Meeting.query.filter(Meeting.date.between(start, end)).all()

        error = ""
    except Exception as e:
        result = "error"
        error = str(e)
    return jsonify({"result": result, "error": error})

@app.route("/api/meeting/filter/<filter>", methods=["GET"])
def meetings_filter(filter):
    group_dict = []
    teacher_dict = []

    try:
        result = Meeting.query.filter(Meeting.name.like(f'{filter}%')).order_by(Meeting.date).all()
        # add groups for each meeting to group dictionary
        for row in result:
            groups = []
            for group in row.groups:
                item = {
                    "group_name": group.group.name,
                    "start_date": group.group.start_date,
                    "end_date": group.group.end_date,                    
                    }
                groups.append(item)

            meeting_groups = { 
                "meeting_id": row.id,
                "groups": groups
            }
            group_dict.append(meeting_groups)

            teachers = []
            for teacher in row.teachers:
                item = {
                    "first_name": teacher.teacher.first_name,
                    "last_name": teacher.teacher.last_name,                
                    }
                teachers.append(item)

            meeting_teachers = { 
                "meeting_id": row.id,
                "teachers": teachers
            }
            teacher_dict.append(meeting_teachers)

        error = ""
    except Exception as e:
        result = "error"
        error = str(e)
    return jsonify({"result": result, "groups": group_dict, "teachers": teacher_dict, "error": error})

@app.route("/api/meeting/limit/<limit>", methods=["GET"])
def meetings_limit(limit):
    group_dict = []
    teacher_dict = []
    try:
        result = Meeting.query.filter(Meeting.date >= datetime.today().date()).order_by(Meeting.date).limit(limit).all()
        
        # add groups for each meeting to group dictionary
        for row in result:
            groups = []
            for group in row.groups:
                item = {
                    "group_name": group.group.name,
                    "start_date": group.group.start_date,
                    "end_date": group.group.end_date,                    
                    }
                groups.append(item)

            meeting_groups = { 
                "meeting_id": row.id,
                "groups": groups
            }
            group_dict.append(meeting_groups)

            teachers = []
            for teacher in row.teachers:
                item = {
                    "first_name": teacher.teacher.first_name,
                    "last_name": teacher.teacher.last_name,                
                    }
                teachers.append(item)

            meeting_teachers = { 
                "meeting_id": row.id,
                "teachers": teachers
            }
            teacher_dict.append(meeting_teachers)
            # print(teacher_dict)


        error = ""
    except Exception as e:
        result = "error"
        error = str(e)
    return jsonify({"result": result, "groups": group_dict, "teachers": teacher_dict, "error": error})



@app.route("/api/studentmeeting/<code>")
def handle_studentmeeting(code=None):
    student_dict = []
    try:
        # get the meeting correlated with the meeting code
        meeting = Meeting.query.filter_by(meeting_code=code).first()
        result = meeting.students

        # loop through students objects that are present in the meeting and add them to student_dict
        present_students = StudentMeeting.query.filter_by(meeting_id=meeting.id, present=True).all()
        for row in present_students:
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
    data = request.get_json()
    student_number = data["studentNumber"]
    first_name = data["studentFirstName"]
    last_name = data["studentLastName"]
    email = data["studentEmail"]
    student_group = data["studentGroup"]
    student = Student(student_number=student_number, first_name=first_name,
                      last_name=last_name, email=email)
    db.session.add(student)
    db.session.commit()

    student_group = StudentGroup(student_id=student.id, group_id=student_group)
    db.session.add(student_group)
    db.session.commit()
    return {
        "status": "Student aangemaakt"
    }


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


@app.route("/api/student/filter/<filter>", methods=["GET"])
def students_filter(filter):
    try:
        result = Student.query.filter(Student.first_name.like(f'{filter}%') | Student.last_name.like(f'{filter}%') | Student.student_number.like(f'{filter}%')).all()

        error = ""
    except Exception as e:
        result = "error"
        error = str(e)
    return jsonify({"result": result, "error": error})

@app.route("/api/student/limit/<limit>", methods=["GET"])
def students_limit(limit):
    try:
        result = Student.query.limit(limit).all()
        
        error = ""
    except Exception as e:
        result = "error"
        error = str(e)
    return jsonify({"result": result, "error": error})



@app.route("/api/teachermeeting/<meeting_id>", methods=["GET"])
@app.route("/api/teachermeeting", methods=["POST"])
def handle_teachermeeting(meeting_id = None):
    if request.method == "POST":
        body = request.json
        try:
            item = TeacherMeeting(
                teacher_id=body['teacher_id'], meeting_id=body['meeting_id'])
            db.session.add(item)
            db.session.commit()
            result = "ok"
            error = ""
        except Exception as e:
            result = "error"
            item = ""
            error = str(e)
        return jsonify({"result": result, "meeting": item, "error": error})
    elif request.method == "GET":
        try:
            result = []
            teachermeeting = TeacherMeeting.query.filter_by(meeting_id=meeting_id).all()
            for teacher in teachermeeting:
                result.append(teacher.teacher.full_name)
            print(result)
            error = ""
        except Exception as e:
            result = "error"
            error = str(e)
        return jsonify({"result": result, "error": error})
    
# Show all teachers
@app.route('/api/teacher', methods=['GET'])
def get_teachers():
    try:
        result = Teacher.query.all()
        error = ""
    except Exception as e:
        result = "error"
        error = str(e)
    # teachers = Teacher.query.all()
    # return jsonify([{'id': teacher.id, 'name': teacher.name} for teacher in teachers])
    return jsonify({"result": result, "error": error})


# Add teacher
@app.route('/api/teacher', methods=['POST'])
def create_teacher():
    data = request.get_json()
    first_name = data["teacherFirstName"]
    last_name = data["teacherLastName"]
    email = data["teacherEmail"]
    admin = False
    if "teacherAdmin" in data:
        admin = True
    teacher = Teacher(first_name=first_name, last_name=last_name,email=email, admin=admin)
    db.session.add(teacher)
    db.session.commit()
    return {
        "status": "Docent aangemaakt"
    }

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


@app.route("/api/teacher/filter/<filter>", methods=["GET"])
def teachers_filter(filter):
    user_dict = []
    try:
        result = Teacher.query.filter(Teacher.first_name.like(f'{filter}%') | Teacher.last_name.like(f'{filter}%')).all()
        for row in result:
            # print(row.user.email)
            user = { 
                "user_id": row.user_id,
                "email": row.user.email
            }
            user_dict.append(user)

        error = ""
    except Exception as e:
        result = "error"
        error = str(e)
    return jsonify({"result": result, "users": user_dict, "error": error})

@app.route("/api/teacher/limit/<limit>", methods=["GET"])
def teachers_limit(limit):
    user_dict = []
    try:
        result = Teacher.query.limit(limit).all()
        for row in result:
            # print(row.user.email)
            user = { 
                "user_id": row.user_id,
                "email": row.user.email
            }
            user_dict.append(user)

        error = ""
    except Exception as e:
        result = "error"
        error = str(e)
    return jsonify({"result": result, "users": user_dict ,"error": error})



@app.route('/api/group', methods=['GET'])
def get_group():
    group = Group.query.all()
    return jsonify({"result": group})


@app.route('/api/group', methods=['POST'])
def create_group():
    data = request.get_json()
    name = data["groupName"]
    start_date = data["groupStartDate"]
    end_date = data["groupEndDate"]
    formatted_startdate = datetime.strptime(start_date, "%Y-%m-%d")
    formatted_enddate = datetime.strptime(end_date, "%Y-%m-%d")
    group = Group(name=name, start_date=formatted_startdate,
                  end_date=formatted_enddate)
    db.session.add(group)
    db.session.commit()
    return {
        "status": "Klas aangemaakt"
    }


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



@app.route("/api/group/filter/<filter>", methods=["GET"])
def groups_filter(filter):
    try:
        result = Group.query.filter(Group.name.like(f'{filter}%')).all()

        error = ""
    except Exception as e:
        result = "error"
        error = str(e)
    return jsonify({"result": result, "error": error})

@app.route("/api/group/limit/<limit>", methods=["GET"])
def groups_limit(limit):
    try:
        result = Group.query.limit(limit).all()
        
        error = ""
    except Exception as e:
        result = "error"
        error = str(e)
    return jsonify({"result": result, "error": error})



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

