from flask import render_template
from app import app
from app.models import Student, Group


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
