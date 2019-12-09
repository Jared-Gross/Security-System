import cv2
import mss
import os
import os.path
from os.path import isfile, join
import shutil
# from tkinter import *
# import tkinter
from PIL import Image, ImageGrab
import moviepy.editor as mp
from datetime import datetime
import natsort as nt
import time
from multiprocessing import Process
import sys
# captureScreen = IntVar()
captureScreen = True
canvas_height=200
canvas_width=200
cap = cv2.VideoCapture(0)
START_TIME = 5
TIME = 0
cascadeLocationFolder = "Face Detection\\"
cascadeLists = [
    "{0}haarcascade_frontalface_default.xml".format(cascadeLocationFolder),
    "{0}haarcascade_eye.xml".format(cascadeLocationFolder),
    "{0}haarcascade_fullbody.xml".format(cascadeLocationFolder)
]
selectedCascade = ""
image_folder = 'Face Detection\\Pics'
video_name = 'temp.avi'
numOfPics = 0
cascade = cv2.CascadeClassifier(cascadeLists[0])
vid_cod = cv2.VideoWriter_fourcc(*'XVID')
output = cv2.VideoWriter("Face Detection/cam_video.mp4", vid_cod, 20.0, (640,480))
start = False
TIME_LIMIT = 100
def on_exists(fname):
    if os.path.isfile(fname):
        newfile = fname + ".old"
        print("{} -> {}".format(fname, newfile))
        # os.rename(fname, newfile)

def removePictures():
    for the_file in os.listdir(image_folder):
        file_path = os.path.join(image_folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def makeVideo():
    try:
        # for index, filename in enumerate(sorted(os.listdir("Face Detection\\Pics"))):
        #     print ('{0:02d}. {1}'.format(index + 1, filename))
        # for filename in sorted(os.listdir("Face Detection\\Pics")):
        #     print (filename)

        images = [img for img in os.listdir(
            image_folder) if img.endswith(".png")]
        if len(images) == 0:
            print('No Images Found')
            return
        else:
            images = nt.natsorted(images)
            frame = cv2.imread(os.path.join(image_folder, images[0]))
            height, width, layers = frame.shape
            video = cv2.VideoWriter(video_name, 0, 10, (width, height))
            for image in images:
                video.write(cv2.imread(os.path.join(image_folder, image)))
            video.release()
            print(len(images))
    except Exception as e:
        print(e)

def savePicture(num):
    try:
        if captureScreen:
            # CAPURE WEBCAM
            return_value,image = cap.read()
            cv2.imwrite("Face Detection\\Pics\\{0}.png".format(num),image)
        else:
            # CAPTURE SCREEN
            with mss.mss() as sct:
                filename = sct.shot(output="Face Detection\\Pics\\{0}.png".format(
                    num))
    except Exception as e:
        print(e)

def btnStop():
    try:
        makeVideo()
        removePictures()
        # When everything done, release the capture
        clip = mp.VideoFileClip(video_name)
        # make the height 360px ( According to moviePy documenation The width is then computed so that the width/height ratio is conserved.)
        clip_resized = clip.resize(height=360)
        clip_resized.write_videofile("Face Detection\\output.mp4")
        os.remove(video_name)
        print("Deleted: {0}".format(video_name))
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print(e)

# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)

def camRun():
    print("Starting..")
    global start
    global TIME
    try:
        while True:
            global numOfPics
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret:
                # Our operations on the frame come here
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Detect faces in the image
                faces = cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                # Draw a rectangle around the faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                # Display the resulting frame
                cv2.imshow('Camera', frame)
                output.write(frame)

                # If theres a face detected then save a picture of it
                if len(faces) >= 1:
                    TIME = START_TIME
                TIME -= 0.2

                if TIME >= 0:
                    numOfPics += 1
                    savePicture(numOfPics)
                    # savePicture(numOfPics)
                    # print("Found {0} faces!".format(len(faces)))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                btnStop()

    except Exception as e:
        print(e)

if __name__ == '__main__':
    camRun()
