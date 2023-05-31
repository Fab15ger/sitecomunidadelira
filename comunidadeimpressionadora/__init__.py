from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os
import sqlalchemy


app = Flask(__name__)

app.config['SECRET_KEY'] = '71959ebc89ab53fc286e22ea9fd99888'
if os.getenv("DATABASE_URL"):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
else:
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comunidade.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'PGPASSWORD=uniza0kj00OeDTYfB7Jg psql -h containers-us-west-126.railway.app -U postgres -p 5667 -d railway'
    

database = SQLAlchemy(app)
bcript = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_criarconta'
login_manager.login_message = 'Por favor faça login ou crie uma conta para continuar'
login_manager.login_message_category = 'alert-info'

from comunidadeimpressionadora import models
engine = sqlalchemy.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
inspector = sqlalchemy.inspect(engine)
if not inspector.has_table("usuario"):
    with app.app_context():
        database.drop_all()
        database.create_all()
        print('Base de Dados criado')
else:
    print('Base de Dados já existente.')


from comunidadeimpressionadora import routes
