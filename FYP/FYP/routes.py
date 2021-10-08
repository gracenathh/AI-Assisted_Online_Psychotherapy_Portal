from FYP.forms import LoginForm, PatientForm, RegisterForm, UpdateDetailsForm, ChangePasswordForm, SearchPatientForm, RequestResetForm, ResetPasswordForm
from flask import render_template, url_for, redirect, flash, abort, request
from flask_login import UserMixin, login_user, current_user
from flask_login.utils import logout_user
from werkzeug.utils import secure_filename
import os
import re
import secrets
from PIL import Image
from FYP import app, db, mail
from FYP.models import User, Patient, Variables, VideoFiles
from flask_mail import Message

from FYP.DeepLearning.Script import test, main

@app.route('/', methods=['GET', 'POST'])
def loginpage():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        #if user and bcrypt.check_password_hash(user.password, form.password.data):
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please Try Again.')
    return render_template('loginpage.html', title='login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('loginpage'))

@app.route('/register', methods=['GET', 'POST'])
def registerpage():
    form = RegisterForm()
    if form.validate_on_submit():
        #hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        #user = User(email=form.email.data, password=hashed_password)
        user = User(email=form.email.data, password=form.password.data, firstname=form.firstname.data, lastname=form.lastname.data, organization=form.organization.data, title=form.title.data)
        db.session.add(user)
        db.session.commit()
        flash('Account Created')
        return redirect(url_for('loginpage'))
    return render_template('registerpage.html', title ='Register', form=form)

def sendresetemail(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@psychportal.com', reciepients=[user.email])
    msg.body = f'''If you have requested to reset your password, please click the following link:
    {url_for('reset_token', token=token, _external=True)}
    If you did not request this, please ignore this email. 
    Thank you.'''
    mail.send(msg)

@app.route('/resetpassword', methods=['GET','POST'])
def resetrequestpage():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        sendresetemail(user)
        flash('An email has been sent to your registered email address')
        return redirect(url_for('loginpage'))
    return render_template('resetrequestpage.html', title='Reset Request', form=form)

@app.route('/resetpassword/<token>', methods=['GET', 'POST'])
def resetoken(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token, please request to reset your password again')
        return redirect(url_for('resetrequestpage'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        flash('Your password has been updated!')
        return redirect(url_for('loginpage'))
    return render_template('resettoken.html', title='Reset Password', form=form)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', title ='dashboard')

@app.route('/account', methods=['GET', 'POST'])
def account():
    return render_template('accountpage.html', title ='Account')

@app.route('/accountupdate', methods=['GET', 'POST'])
def accountupdate():
    form = UpdateDetailsForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.title = form.title.data
        current_user.organization = form.organization.data
        db.session.commit()
    return render_template('accountupdatepage.html', title='Account Update', form=form)

@app.route('/changepassword', methods=['GET', 'POST'])
def changepassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.commit()
        flash('Password Changed!')
        return redirect(url_for('account'))
    return render_template('changepasswordpage.html', title='Change Password', form=form)

@app.route('/user/records', methods=['GET', 'POST'])
def userrecords():
    search = SearchPatientForm(request.form)
    if request.method == 'POST':
        return recordresults(search)
    patients = Patient.query.filter_by(therapyid = current_user.id).all()
    return render_template('userrecords.html', title='Records', patients=patients, form=search)

@app.route('/patient/new', methods=['GET', 'POST'])
def addrecordpage():
    form = PatientForm()
    if form.validate_on_submit():
        patient = Patient( firstname=form.firstname.data, lastname=form.lastname.data, gender=form.gender.data, country=form.country.data,  age=form.age.data, guardiantitle=form.guardiantitle.data,
            guardianfirstname=form.guardianfirstname.data, guardianlastname=form.guardianlastname.data, email=form.email.data, relationship=form.relationship.data)
        
        #if form.picture.data:
            #picture_file = storePicture(form.picture.data)
            #patient.picture = picture_file
        
        db.session.add(patient)
        db.session.commit()
        flash('Patient Record Added')
        return redirect(url_for('dashboard'))
    else:
        flash('Error Adding!')
    return render_template('addrecord.html', title='Add Record', form=form)

@app.route('/patient/<int:patient_id>', methods=["GET"])
def recordpage(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    #picture = url_for('static', filename='images/' + patient.id)
    return render_template('patient.html', title=patient.id, patient=patient)
    #,picture=picture)

@app.route('/recordsresults')
def recordresults(search):
    results = []
    searchquery = search.data['search']

    if search.data['search'] == '':
        results = Patient.query.filter_by(therapyid = current_user.id).all()

    if not results:
        flash('No Matching Record!')
        return redirect('/user/records')

    else:
        return render_template('recordresults.html', results=results)

@app.route("/upload", methods=['POST', 'GET'])
def video_upload():
    if request.method == 'POST':
        video_file = request.files['videoFile']
        if not video_file:
            return "No video uploaded", 400
        
        filename = secure_filename(video_file.filename)

       #Create the directory where to store videos if it does not exist
        videoDirectory =  os.path.join(os.getcwd(), 'FYP', 'static', 'uploads')        
        if not os.path.exists(videoDirectory):
            os.makedirs(videoDirectory)

        video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        newVideo = VideoFiles(videoName=filename, videoData=video_file.read())
        db.session.add(newVideo)
        db.session.commit()

        return {
            "message": "Video " + filename + " has been successfully uploaded!"
        }
        
        # return redirect(url_for('videoDB'))

    return render_template("uploads.html") 

@app.route("/display/<filename>")
def play_video(filename):
    # CHECK FOR FILE EXISTS
    # video_data = VideoFiles.query.all()
    # video_array = []
    # for i in video_data:
    #     if (i.videoName == filename):
    #         video_array.append(i.videoName)

    # print(video_array)

    return render_template("uploads.html", video = filename)


@app.route("/videoDb")
def videoDB():
    video_data = VideoFiles.query.all()
    # video_array = []
    # for i in video_data:
    #    video_array.append(i.videoName)

    # print(video_array)

    return render_template("videoDB.html", user = Variables.username, videos = video_data)
    # videos = video_array,

@app.route("/unprocessdVideo/<int:videoID>")
def unprocessedVideo(videoID):
    vid = VideoFiles.query.get_or_404(videoID)
    return render_template("unprocessed-video-details-page-13.html",video = vid)

@app.route("/processedVideo/<int:videoID>")
def processedVideo(videoID):
    #Page for a specific video
    vid = VideoFiles.query.get_or_404(videoID)
    if vid.videoEmotion == None: #If did not process the video before
        #Perform the DL output here. Shld print here then render template with the output
        try:    
            videoDirectory =  os.path.join(os.getcwd(), 'FYP', 'static', 'uploads', vid.videoName)
            print(videoDirectory)
            predictedresult = main(videoDirectory)
            #print(predictedresult)

            #Store the results in the database
            vid.videoEmotion = predictedresult
            db.session.commit()

        except Exception as e: #print error message
            print(e)

    #Query the results from the database
    queriedResults = VideoFiles.query.get_or_404(videoID).videoEmotion
    print(queriedResults)

    #return render_template("video-output-page-11.html",video = vid)
    return render_template("outputDL.html", video = vid, ouput = queriedResults)




@app.route('/patient/<id>/update', methods=["GET", "POST"])
def updaterecordpage(id):
    patient = Patient.query.get_or_404(id)
    if patient.therapist != current_user:
        abort(403)
    form = PatientForm()
    if form.validate_on_submit():
        patient.gender = form.gender.data 
        patient.firstname=form.firstname.data 
        patient.lastname=form.lastname.data 
        patient.age=form.age.data
        patient.country=form.country.data
        
        patient.guardiantitle=form.guardiantitle.data
        patient.guardianfirstname=form.guardianfirstname.data
        patient.guardianlastname=form.guardianlastname.data
        patient.email=form.email.data
        
        patient.relationship=form.relationship.data
        """
        if form.picture.data:
            picture_file = storePicture(form.picture.data)
            patient.picture = picture_file
        db.session.commit()
        """
        
        flash('Record Updated')
        return redirect(url_for('recordpage', id=patient.id))
    return render_template('updaterecordpage.html', title='Update Record', form=form)

"""
@app.route('/patient/id/delete', methods=['POST'])
def deleterecord(id):
    patient = Patient.query.get_or_404(id)
    if patient.therapist != current_user:
        abort(403)
    db.session.delete(patient)
    db.session.commit()
    flash('Record Deleted')
    return redirect(url_for('dashboard'))
"""
"""
def storePicture(form_picture):
    randomhex = secrets.token_hex(8)
    _, f_ext = os.path.splittext(form_picture.filename)
    picture_fn = randomhex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)

    outputsize = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(outputsize)
    i.save(picture_path)

    return picture_fn
    """