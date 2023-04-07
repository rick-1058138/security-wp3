import os
from flask_bcrypt import Bcrypt
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_qrcode import QRcode
from flask_login import LoginManager

from flask_swagger_ui import get_swaggerui_blueprint

basedir = os.path.abspath(os.path.dirname(__file__))



app = Flask(__name__)

# API documentation 
SWAGGER_URL = '/api/docs'  
API_URL = '/static/swagger.json' 
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Aanwezigheidstool"
    }
    
)
app.register_blueprint(swaggerui_blueprint)


app.config['SECRET_KEY'] = 'Alien Software'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aanwezigheidstool.db'
app.app_context().push()
db = SQLAlchemy(app)
QRcode(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Je moet eerst inloggen!'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt(app)
app.secret_key = 'ThisKeyIsSuperSecret'

from app import routes, api
