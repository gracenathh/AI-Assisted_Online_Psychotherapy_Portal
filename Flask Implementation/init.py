import os
import getpass
import re
from flask import Flask, flash, request, redirect, url_for, render_template
# from werkzeug.datastructures import V
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
from datetime import datetime


VIDEO_UPLOADER = join(dirname(realpath(__file__)), 'static/uploads/')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///webapp.db"
app.config['UPLOAD_FOLDER'] = VIDEO_UPLOADER
db = SQLAlchemy(app)

class VideoFiles(db.Model):
    videoID = db.Column(db.Integer, primary_key = True)
    videoName = db.Column(db.String(300), nullable = False)
    videoData = db.Column(db.LargeBinary, nullable = False)

@app.route('/')
def hello_world():
    return login_page()

@app.route("/login")
def login_page():
    return render_template('login.html')

@app.route("/register")
def register_page():
    return render_template('register.html')

@app.route("/login_auth", methods=['POST'])
def login_auth():
    email = request.form.get('email')
    password = request.form.get('pass')
    #return "The email is {} and the password is {}".format(email, password)
    return index()

@app.route("/index")
def index():
    return render_template("uploads.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/upload", methods=['POST', 'GET'])
def video_upload():
    if request.method == 'POST':
        video_file = request.files['videoFile']
        if not video_file:
            return "No video uploaded", 400
        
        filename = secure_filename(video_file.filename)
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
    video_array = []
    for i in video_data:
        video_array.append(i.videoName)

    print(video_array)

    return render_template("videoDB.html", videos = video_array, user = Variables.username)

@app.route("/unprocessedVideo")
def unprocessedVideo():
    return render_template("unprocessed-video-details-page-13.html")


class Variables:
    username = getpass.getuser()
    date = datetime.now()


if __name__ == "__main__":
    app.run(debug=True)