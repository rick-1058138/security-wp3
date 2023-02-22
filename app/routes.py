from flask import render_template
from app import app, db
from app.models import Student, Group
from flask import jsonify, request
from app.models import Student


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

@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([{'id': student.id, 'name': student.name} for student in students])

@app.route('/students', methods=['POST'])
def create_student():
    name = request.json['name']
    student = Student(name=name)
    db.session.add(student)
    db.session.commit()
    return jsonify({'id': student.id, 'name': student.name})

@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    student = Student.query.get_or_404(id)
    return jsonify({'id': student.id, 'name': student.name})

@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student {} ID: {} is verwijderd".format(student.name, student.id)})