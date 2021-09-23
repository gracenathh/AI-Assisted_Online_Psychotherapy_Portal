from flask_login import LoginManager, login_manager, UserMixin, login_user, current_user
from datetime import datetime
import getpass
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref, column_property
from FYP import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    #profilepicture = db.Column(db.String(20))
    title = db.Column(db.String(10))
    firstname = db.Column(db.String(120))
    lastname = db.Column(db.String(120))
    password = db.Column(db.String(60))
    organization = db.Column(db.String(60))
    patientRecord = db.relationship('Patient', backref='user', lazy='select')
    videoRecord = db.relationship('VideoFiles', backref='user', lazy='select')

    def __repr__(self):
        return f"User('{self.email}')"

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(5))
    firstname = db.Column(db.String(120))
    lastname = db.Column(db.String(120))
    city = db.Column(db.String(120))
    country = db.Column(db.String(60))
    dob = db.Column(db.Date)
    therapyid = db.Column(db.Integer, db.ForeignKey('user.id'))
    #picture = db.Column(db.string(30), default='defaultpic.jpg')

    guardiantitle = db.Column(db.String(5))
    guardianfirstname = db.Column(db.String(120))
    guardianlastname = db.Column(db.String(120))
    relationship = db.Column(db.String(20))
    email = db.Column(db.String(120))
    countrycode = db.Column(db.String(5))
    phonenumber = db.Column(db.Integer)

    def __repr__(self):
        return f"Patient('{self.fullname}')"

class VideoFiles(db.Model):
    videoID = db.Column(db.Integer, primary_key = True)
    videoName = db.Column(db.String(300), nullable = False)
    videoData = db.Column(db.LargeBinary, nullable = False)
    uploaderid = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"VideoFiles('{self.videoName}')"

class Variables:
    username = getpass.getuser()
    date = datetime.now()

