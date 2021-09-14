from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.core import DateTimeField, FormField, IntegerField, SelectField
from wtforms.fields.simple import FileField, PasswordField, SubmitField
from flask_wtf.file import FileAllowed
from wtforms.form import Form
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from FYP.models import User

class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])

    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    fullname = StringField('fullname', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    confirmPassword = PasswordField('confirm password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Register')

    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email Already Registered!')
    


class PatientForm(FlaskForm):
    title = SelectField(u'title', choices=[('Mr.'), ('Miss')])
    firstname = StringField('firstname', validators=[DataRequired()])
    lastname = StringField('lastname', validators=[DataRequired()])
    dob = DateTimeField('dob', format='%d%m%y')
    city = StringField('city')
    country = StringField('country')
    #picture = FileField('Upload Picture', validators=[FileAllowed(['.jpg', 'png'])])

    guardiantitle = SelectField(u'title', choices=[('Dr.'), ('Mr.'), ('Mrs.'), ('Ms.'), ('Mdm'), ('Miss')])
    guardianfirstname = StringField('guardianfirstname', validators=[DataRequired()])
    guardianlastname = StringField('guardianlastname', validators=[DataRequired()])
    relationship = SelectField(u'relationship', choices=[('Parent'), ('Sibling'), ('Grandparent'), ('Guardian')])
    email = StringField('email', validators=[Email()])
    countrycode = IntegerField('countrycode')
    phonenumber = IntegerField('phonenumber')

    submit = SubmitField('Add Record')

class ChangePasswordForm(FlaskForm):
    password = PasswordField('password', validators=[DataRequired()])
    confirmpassword = PasswordField('confirm password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Change Password')

class UpdateDetailsForm(FlaskForm):
    title = SelectField(u'Title', choices=[('Dr.'), ('Mr.'), ('Mrs.'), ('Ms.'), ('Mdm'), ('Miss')])
    email = StringField('email', validators=[DataRequired(), Email()])
    fullname = StringField('fullname', validators=[DataRequired()])
    organization = StringField('organization', validators=[DataRequired()])

    submit = SubmitField('Update')