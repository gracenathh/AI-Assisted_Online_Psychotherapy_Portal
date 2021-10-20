#routes file details each page and function to be used by the web application, and also links respective HTML pages
from wtforms import form
from FYP.forms import LoginForm, PatientForm, RegisterForm, UpdateDetailsForm, ChangePasswordForm, SearchPatientForm, RequestResetForm, ResetPasswordForm
from flask import render_template, url_for, redirect, flash, abort, request, session
from flask_login import UserMixin, login_user, current_user
from flask_login.utils import logout_user
from werkzeug.utils import secure_filename
import os
import secrets
from sqlalchemy import sql
from datetime import datetime
from FYP import app, db, mail
from FYP.models import User, Patient, Variables, VideoFiles
from flask_mail import Message
from FYP.DeepLearning.Script import test, main

#Login page matches user input from form and results queried from database for user authentication
#Error message displayed if no matching results, user will have to try again 
@app.route('/', methods=['GET', 'POST'])
def loginpage():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please Try Again.')
    return render_template('loginpage.html', title='login', form=form)

#Logs user out and redirects them back to login page. User will need to login again to access web app.
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('loginpage'))

#Allows registration of user by committing their field entries into the database from the form
@app.route('/register', methods=['GET', 'POST'])
def registerpage():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data, firstname=form.firstname.data, lastname=form.lastname.data, organization=form.organization.data, title=form.title.data)
        db.session.add(user)
        db.session.commit()
        flash('Account Created')
        return redirect(url_for('loginpage'))
    return render_template('registerpage.html', title ='Register', form=form)

#Function to sent an email to the registered email address of user who wants to reset their password, using the SMTP account
def sendresetemail(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='psychportal3162@gmail.com', recipients=[user.email])
    msg.body = f'''If you have requested to reset your password, please click the following link:
    {url_for('resettoken', token=token, _external=True)}
    If you did not request this, please ignore this email. 
    Thank you.'''
    mail.send(msg)

#Allows user to reset their password and calls sendresetemail function. User must already be registered and will be checked by querying database.
@app.route('/resetpassword', methods=['GET','POST'])
def resetrequestpage():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        sendresetemail(user)
        flash('An email has been sent to your registered email address')
        return redirect(url_for('loginpage'))
    return render_template('resetrequestpage.html', title='Reset Request', form=form)

#Page that user gets redirected to from the email they received, url is created from the token. 
#Token is validated using function from User class, if invalid, user cannot reset token.
#otherwise user can enter a new password twice to confirm, and changes will be committed
@app.route('/resetpassword/<token>', methods=['GET', 'POST'])
def resettoken(token):
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

#dashboard page route
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', title ='dashboard')

#account details page route
@app.route('/account', methods=['GET', 'POST'])
def account():
    return render_template('accountpage.html', title ='Account')

#this page allows user to change their information, changes are committed
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

#allows user to change their password
@app.route('/changepassword', methods=['GET', 'POST'])
def changepassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.commit()
        flash('Password Changed!')
        return redirect(url_for('account'))
    return render_template('changepasswordpage.html', title='Change Password', form=form)

#shows all patient records that the user has put in. records from other users will not show.
#search function on this page takes in string input by user and uses SQL to query the database and returns matching records
@app.route('/user/records', methods=['GET', 'POST'])
def userrecords():
    form= SearchPatientForm()
    search = form.search.data
    if request.method == 'POST':
        search = form.search.data
        search = search.strip()
     
        likestring = "%{}%".format(search)
        sql = "SELECT id, firstname, lastname, country FROM patient WHERE therapyid = :b AND firstname LIKE :x OR lastname LIKE :y OR id LIKE :z OR country LIKE :a"
        stmt = db.text(sql).bindparams(x=likestring, y=likestring, z=likestring, a=likestring, b=current_user.id)
        patients = db.session.execute(stmt).fetchall()

    else: patients = Patient.query.filter_by(therapyid = current_user.id).all()
    return render_template('userrecords.html', title='Records', patients=patients, form=form, search=search)

#page allows user to add a patient record. Each record has its foreign key filled with the user's ID. All other data is taken from user input and is committed. 
@app.route('/addrecord', methods=['GET', 'POST'])
def addrecordpage():
    form = PatientForm()
    if form.validate_on_submit():
        patient = Patient( therapyid = current_user.id, firstname=form.firstname.data, lastname=form.lastname.data, gender=form.gender.data, country=form.country.data,  age=form.age.data, guardiantitle=form.guardiantitle.data,
            guardianfirstname=form.guardianfirstname.data, guardianlastname=form.guardianlastname.data, email=form.email.data, relationship=form.relationship.data)
 
        db.session.add(patient)
        db.session.commit()
        flash('Patient Record Added')
        return redirect(url_for('dashboard'))
    else:
        flash('Error Adding!')
    return render_template('addrecord.html', title='Add Record', form=form)

#displays a page for a particular patient record using patient ID. If patient ID does not exist in database, 404 page is shown. 
#videos which have this patient's ID as foreign key will also be shown here
@app.route('/patient/<int:patient_id>', methods=["GET"])
def recordpage(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    videos = VideoFiles.query.filter_by(patientid = patient_id).all()
    return render_template('patient.html', title=patient.id, patient=patient, videos=videos)

@app.route("/upload", methods=['POST', 'GET'])
def video_upload():
    """
    Route for the user to upload the video onto the Video Database
    """

    # Call the post method to upload video
    if request.method == 'POST':
        # get the video file type:
        video_file = request.files['videoFile']
        patientid = request.form.get('patientid')
        if not video_file:
            return "No video uploaded", 400
        print(patientid)
        filename = secure_filename(video_file.filename)

       #Create the directory where to store videos if it does not exist
        videoDirectory =  os.path.join(os.getcwd(), 'FYP', 'static', 'uploads')        
        if not os.path.exists(videoDirectory):
            os.makedirs(videoDirectory)

        # datetime object containing current date and time
        now = datetime.now()

        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        # get the filename which is stored in the uploaded folder
        video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # create a new record in the video files
        newVideo = VideoFiles(videoName=filename, videoData=video_file.read(), videoDate=dt_string, uploaderid=current_user.id, patientid=patientid)
        # add the new record:
        db.session.add(newVideo)
        # commit the changes to the database
        db.session.commit()

        # Output on the screen as verification to the user:
        return {
            "message": "Video " + filename + " has been successfully uploaded!"
        }
        
        # return redirect(url_for('videoDB'))

    return render_template("uploads.html") 

@app.route("/display/<filename>")
def play_video(filename):
    """
    Display the video after uploaded:
    @param filename: name of the video file
    @return: redirect to the uploads.html page
    """
    return render_template("uploads.html", video = filename)


@app.route("/videoDb")
def videoDB():
    """
    Video database displaying the list of videos uploaded by the patient.
    @return: redirect to the video database page
    """
    video_data = VideoFiles.query.filter_by(uploaderid = current_user.id).all()
    return render_template("videoDB.html", user = Variables.username, videos = video_data)


@app.route("/processedVideo/<int:videoID>")
def processedVideo(videoID):
    #Display the Processed video page:
    vid = VideoFiles.query.get_or_404(videoID)
    if vid.videoEmotion == None: #If did not process the video before
        #Perform the DL output here. Shld print here then render template with the output
        try:    
            videoDirectory =  os.path.join(os.getcwd(), 'FYP', 'static', 'uploads', vid.videoName)
            print(videoDirectory)
            predictedresult = main(videoDirectory)

            #Store the results in the database
            vid.videoEmotion = predictedresult
            db.session.commit()

        except Exception as e: #print error message
            db.session.rollback()
            raise
            print(e)

    #Query the results from the database
    queriedResults = VideoFiles.query.get_or_404(videoID).videoEmotion
    print(queriedResults)

    # send the list of results to display the results for each vid:
    return render_template("outputDL.html", video = vid, ouput = queriedResults)

#allows user to update any existing record. If user tries to update any record from another user, there will be a 403 error. 
@app.route('/patient/<int:patient_id>/update', methods=["GET", "POST"])
def updaterecordpage(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if patient.user != current_user:
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
   
        db.session.commit()
        flash('Record Updated')
        return redirect(url_for('recordpage', id=patient.id))
    return render_template('updaterecordpage.html', title='Update Record', form=form)

#allows user to delete any existing record. If user tries to delete any record from another user, there will be a 403 error. 
@app.route('/patient/<int:patient_id>/delete', methods=['POST'])
def deleterecord(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if patient.user != current_user:
        abort(403)
    db.session.delete(patient)
    db.session.commit()
    flash('Record Deleted')
    return redirect(url_for('dashboard'))

