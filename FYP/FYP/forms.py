from flask.app import Flask
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.core import DateTimeField, FormField, IntegerField, SelectField
from wtforms.fields.simple import FileField, PasswordField, SubmitField
from flask_wtf.file import FileAllowed
from wtforms.form import Form
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from FYP.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    title = SelectField(u'Title', choices=[('Dr.'), ('Mr.'), ('Mrs.'), ('Ms.'), ('Mdm'), ('Miss')])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    organization = StringField('Organization')
    password = PasswordField('Password', validators=[DataRequired()])
    confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Register')

    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email Already Registered!')
    


class PatientForm(FlaskForm):
    gender = SelectField(u'Gender', choices=[('Male'), ('Female')])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    age = IntegerField('Age in Years')
    country = StringField('Country')
    #picture = FileField('Upload Picture', validators=[FileAllowed(['.jpg', 'png'])])

    guardiantitle = SelectField(u'Title', choices=[('Dr.'), ('Mr.'), ('Mrs.'), ('Ms.'), ('Mdm'), ('Miss')])
    guardianfirstname = StringField('First Name', validators=[DataRequired()])
    guardianlastname = StringField('Last Name', validators=[DataRequired()])
    relationship = SelectField(u'Relationship', choices=[('Parent'), ('Sibling'), ('Grandparent'), ('Guardian')])
    email = StringField('Email', validators=[Email()])

    submit = SubmitField('Submit')

class ChangePasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirmpassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Change Password')

class UpdateDetailsForm(FlaskForm):
    title = SelectField(u'Title', choices=[('Dr.'), ('Mr.'), ('Mrs.'), ('Ms.'), ('Mdm'), ('Miss')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    organization = StringField('Organization', validators=[DataRequired()])

    submit = SubmitField('Update')

class SearchPatientForm(FlaskForm):
    search = StringField('Search')
    
class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('CONFIRM')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Email Does Not Exist. Please enter the email you have registered with.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirmpassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Reset Password')