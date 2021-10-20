#to run: in cmd, navigate to /FYP, enter command: "set FLASK_APP=FYP:newapp" then enter "flask run"
#to check db version in cmd, navigate to /FYP, enter command: "set FLASK_APP=FYP:newapp" then enter "flask db current --directory FYP/migrations"
#__init__ file initializes the flask application via setting appname, database, secret key, related folders, login manager, SMTP account and connecting to the routings
from flask import Flask
from os.path import join, dirname, realpath
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
import smtplib

#videos uploaded will be stored in this directory
VIDEO_UPLOADER = join(dirname(realpath(__file__)), 'static/uploads/')

app = Flask(__name__)

#secret key for signing flask session cookies
app.config['SECRET_KEY'] = 'cc108b47c5a06f710fdb8bf12cac68e2'
#assigns a database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

app.config['UPLOAD_FOLDER'] = VIDEO_UPLOADER

db = SQLAlchemy(app)
migrate=Migrate(app,db, render_as_batch=True)
login_manager = LoginManager(app)

#connects an SMTP account for use with reset password feature
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TSL']= True
app.config['EMAIL_HOST_USER'] = 'psychportal3162@gmail.com'
app.config['EMAIL_HOST_PASSWORD'] = 'Portal3162'
mail = Mail(app)

s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls()
s.login('psychportal3162@gmail.com', 'Portal3162')


#webpage routings
from FYP import routes

newapp = app
