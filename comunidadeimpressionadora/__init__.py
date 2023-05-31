from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = '71959ebc89ab53fc286e22ea9fd99888'
if os.getenv("DATABASE_URL"):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comunidade.db'

database = SQLAlchemy(app)
bcript = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_criarconta'
login_manager.login_message = 'Por favor faça login ou crie uma conta para continuar'
login_manager.login_message_category = 'alert-info'

from comunidadeimpressionadora import routes
