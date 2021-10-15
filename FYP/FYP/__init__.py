#to run: in cmd, navigate to /FYP, enter command: "set FLASK_APP=FYP:newapp" then enter "flask run"
#to check db version in cmd, navigate to /FYP, enter command: "set FLASK_APP=FYP:newapp" then enter "flask db current --directory FYP/migrations"

from flask import Flask
from os.path import join, dirname, realpath
import os
from flask_sqlalchemy import SQLAlchemy, declarative_base
from sqlalchemy.schema import MetaData
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
import smtplib

VIDEO_UPLOADER = join(dirname(realpath(__file__)), 'static/uploads/')

app = Flask(__name__)

app.config['SECRET_KEY'] = 'cc108b47c5a06f710fdb8bf12cac68e2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = VIDEO_UPLOADER

db = SQLAlchemy(app)
migrate=Migrate(app,db, render_as_batch=True)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TSL']= True
app.config['EMAIL_HOST_USER'] = 'psychportal3162@gmail.com'
app.config['EMAIL_HOST_PASSWORD'] = 'Portal3162'
mail = Mail(app)

s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls()
s.login('psychportal3162@gmail.com', 'Portal3162')

"""
meta = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
      })
Base = declarative_base(metadata=meta)
"""

from FYP import routes

newapp = app
