import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

# https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application

# app.config['SQLALCHEMY_DATABASE_URI'] =\
#     'sqlite:///' + os.path.join(basedir, 'databases/aanwezigheidstool.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Alien Software'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aanwezigheidstool.db'
app.app_context().push()
db = SQLAlchemy(app)

from app import routes
