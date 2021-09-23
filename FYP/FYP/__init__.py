#to run: in cmd, navigate to /FYP, enter command: "set FLASK_APP=FYP:newapp" then enter "flask run"
#to check db version in cmd, navigate to /FYP, enter command: "set FLASK_APP=FYP:newapp" then enter "flask db current --directory FYP/migrations"

from flask import Flask
from os.path import join, dirname, realpath
from flask_sqlalchemy import SQLAlchemy, declarative_base
from sqlalchemy.schema import MetaData
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

meta = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
      })
Base = declarative_base(metadata=meta)


from FYP import routes

newapp = app
