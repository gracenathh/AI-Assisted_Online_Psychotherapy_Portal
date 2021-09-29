
#Just trying out some sample python code

# #Imports
import sys
import cv2
import pathlib
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
import keras
from decimal import Decimal
import shutil

def test():
    print("Reached python script")


#Extract face and resize
def extract_face(img_list, min_size = (200,200)):
  idx = 0 
  while idx < len(img_list):
    img = img_list[idx]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor = 1.05, minNeighbors = 5, minSize= min_size ) #, minSize = (200,200)) 
  
    for (x, y, w, h) in faces:
      #if x == 0 or y == 0 or w == 0 or h == 0:
      #  print("None")
      faces = img[y:y + h, x:x + w]
      faces = cv2.resize(faces, (224,224),interpolation = cv2.INTER_AREA)

    if len(faces) != 0:
      img_list[idx] = faces
      idx += 1
    else:
      img_list.pop(idx)


# #Splitting video into frames, extracting and resizing
def slice_video(video_path):
  sourceVideoDirectory = os.path.normpath(video_path)

  to_return = []
  count = 0
  vidcap = cv2.VideoCapture(sourceVideoDirectory)
  success,image = vidcap.read()    #Grabs, decodes and returns the next video frame.
  success = True
  while success:
      vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*500))    # added this line. set() = set a property in video capture #0.167 for 6 frames per sec -> 6 img/3 sec
      #CAP_PROP_POS_MSEC = Current position of the video file in milliseconds.
      success,image = vidcap.read()
      if success == True:    #If have read in a new frame
        #cv2.imwrite(os.path.join(pathOut + "/frame_%d_.jpg" % count), image)     # save frame as JPEG file
        to_return.append(image)
      count = count + 1

  return to_return


#Data duplication
def duplicate(img_list):
  n = len(img_list)
  if n % 6 != 0:
    duplicate_num = 6 - (n%6)

    for i in range(duplicate_num):
      img_list.append(img_list[-1])

  return len(img_list)

#Create list of images in np.arr form
def transform_img(img_list):
  img_list = np.asarray(img_list)
  img_list = [np.expand_dims(img,0) for img in img_list]

  return img_list #return a list of tuple (np.arr of image, image code)


#Predicted label and time 
def get_label_time(arr, threshold = 0.30):
  label_code = {0: 'anger', 1: 'disgust', 2 : 'fear', 3 : 'happy', 4 : 'sad', 5 : 'surprise'}
  to_return = []
  time_str = "" 

  for i in range(len(arr)):
    prob = arr[i][0]
    idx = arr[i][1][0]

    if prob > threshold:
      hour = i*3 // 3600
      minute = i*3 // 60
      second = i*3 % 60

      if hour == 0 and minute == 0 and second == 0:
        pass
      else:
        if hour != 0:
          time_str += str(hour)
        
        # add minute
        if hour != 0 and len(str(minute)) == 1:
          time_str += ":0" + str(minute)
        
        else: #hour == 0 and len(minute)
          time_str += str(minute)

        # add second
        if len(str(second)) == 1:
          time_str += ":0" + str(second)

        else:
          time_str += ":" + str(second)

        to_return.append((label_code[idx], time_str))
      time_str = "" 

  return to_return

#Main function
def main(directory):

  # process file
  # 1 - Slice video
  extracted_img = slice_video(directory)

  # 2 - Extract face only & resize image
  extract_face(extracted_img)

  # 3 - Do data duplication & tansfrom image
  duplicate(extracted_img)
  img_list = transform_img(extracted_img)

  # 5 - Do prediction
  #print(os.getcwd())
  export_path = os.path.join(os.getcwd(), 'FYP', 'DeepLearning', 'Model.h5')
  trainedModel = keras.models.load_model(export_path)
  predicted_list = []
  for i in range(0, len(img_list),6):
    input = img_list[i:i+6]
    yhat = trainedModel.predict(input) #Use verbose to get progress bar
    predicted_list.append((yhat.max(), np.argmax(yhat, axis=1)))

  return get_label_time(predicted_list)



##################For brython update html elems
# from browser import document, html

# element = document.getElementById("test")

# para = document.createElement("P")
# text = document.createTextNode("Processing video progress")
# para.appendChild(text)
# element.appendChild(para)


# progressBar = document.createElement("progress")
# progressBar.setAttribute("id", "progressBarDL")
# progressBar.setAttribute("value", "32")
# progressBar.setAttribute("max", "100")

# label = document.createElement("label")
# label.setAttribute("for","progressBarDL")
# label.setAttribute("innerHTML", "Deep Learning Processing progress:")   
    
# element.appendChild(progressBar)
# element.appendChild(label)

####################For brython update html elems



