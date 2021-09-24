from FYP.forms import LoginForm, PatientForm, RegisterForm, UpdateDetailsForm, ChangePasswordForm, SearchPatientForm
from flask import render_template, url_for, redirect, flash, abort, request
from flask_login import UserMixin, login_user, current_user
from flask_login.utils import logout_user
from werkzeug.utils import secure_filename
import os
import re
import secrets
from PIL import Image
from FYP import app, db
from FYP.models import User, Patient, Variables, VideoFiles


from FYP.DeepLearning.Script import test

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
            flash('Login Unsuccessful')
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
        user = User(email=form.email.data, password=form.password.data, firstname=form.firstname.data, lastname=form.lastname.data)
        db.session.add(user)
        db.session.commit()
        flash('Account Created')
        return redirect(url_for('loginpage'))
    return render_template('registerpage.html', title ='Register', form=form)

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
        patient = Patient(title = form.title.data, firstname=form.firstname.data, lastname=form.lastname.data, city=form.city.data, country=form.country.data,  dob=form.dob.data, guardiantitle=form.guardiantitle.data,
            guardianfirstname=form.guardianfirstname.data, guardianlastname=form.guardianlastname.data, email=form.email.data, countrycode=form.countrycode.data, phonenumber=form.phonenumber.data, relationship=form.relationship.data)
        
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

@app.route('/patient/<id>', methods=["GET"])
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

        # if not os.path.exists(".\static\uploads"):
        #     print("")
        #     os.makedirs(".\static\uploads")

        video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        newVideo = VideoFiles(videoName=filename, videoData=video_file.read())
        print(newVideo.videoName)
        print(newVideo.videoData)
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
    #     video_array.append(i.videoName)

    # print(video_array)

    return render_template("videoDB.html", videos = video_data, user = Variables.username)

@app.route("/unprocessedVideo/<int:videoID>")
def unprocessedVideo(videoID):

    #Page for a specific video
    vid = VideoFiles.query.get_or_404(videoID)
    return render_template("unprocessed-video-details-page-13.html",video = vid)


@app.route("/processedVideo/<int:videoID>")
def processedVideo(videoID):


    #Page for a specific video
    vid = VideoFiles.query.get_or_404(videoID)

    #Perform the DL output here. Shld print here then render template with the output
    try:    
        print("/static/uploads/" + vid.videoName)

        test()
    except: 
        return 'Error'


    return render_template("video-output-page-11.html",video = vid)



@app.route('/patient/<id>/update', methods=["GET", "POST"])
def updaterecordpage(id):
    patient = Patient.query.get_or_404(id)
    if patient.therapist != current_user:
        abort(403)
    form = PatientForm()
    if form.validate_on_submit():
        patient.title = form.title.data 
        patient.firstname=form.firstname.data 
        patient.lastname=form.lastname.data 
        patient.city=form.city.data
        patient.country=form.country.data
        patient.dob=form.dob.data 
        patient.guardiantitle=form.guardiantitle.data
        patient.guardianfirstname=form.guardianfirstname.data
        patient.guardianlastname=form.guardianlastname.data
        patient.email=form.email.data
        patient.countrycode=form.countrycode.data 
        patient.phonenumber=form.phonenumber.data
        patient.relationship=form.relationship.data
        """
        if form.picture.data:
            picture_file = storePicture(form.picture.data)
            patient.picture = picture_file
        db.session.commit()
        """
        
        flash('Record Updated')
        return redirect(url_for('recordpage', id=patient.id))
    return render_template('updaterecord.html', title='Update Record', form=form)

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