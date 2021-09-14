#to run: in cmd, navigate to /FYP, enter command: "set FLASK_APP=FYP:newapp" then enter "flask run"
#to check db version in cmd, navigate to /FYP, enter command: "set FLASK_APP=FYP:newapp" then enter "flask db current --directory FYP/migrations"

from flask import Flask
from os.path import join, dirname, realpath
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

VIDEO_UPLOADER = join(dirname(realpath(__file__)), 'static/uploads/')

app = Flask(__name__)

app.config['SECRET_KEY'] = 'cc108b47c5a06f710fdb8bf12cac68e2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = VIDEO_UPLOADER

db = SQLAlchemy(app)
migrate=Migrate(app,db, render_as_batch=True)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)


from FYP import routes

newapp = app
