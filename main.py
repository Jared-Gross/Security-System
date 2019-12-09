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
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import pyqtSlot, Qt, pyqtSignal, QThread
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtWidgets
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

class External(QThread):
    """
    Runs a counter thread.
    """
    countChanged = pyqtSignal(int)

    def run(self):
        count = 0
        while count < TIME_LIMIT:
            count +=1
            time.sleep(0.1)
            self.countChanged.emit(count)
            
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Face Detection'
        self.left = 100
        self.top = 100
        self.width = canvas_width
        self.height = canvas_height
        self.initUI()
        
    def slot_method(self):
        Toggle()
        
    def messageBox(self, text):
        QMessageBox.critical(self, 'Error!', "Log:\n" + text, QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
        
    def onActivated(self, text):
        if text == "frontalface_default":
            selectedCascade = cascadeLists[0]
            cascade = cv2.CascadeClassifier(cascadeLists[0])
        elif text == "eye":
            selectedCascade = cascadeLists[1]
            cascade = cv2.CascadeClassifier(cascadeLists[1])
        elif text == "fullbody":
            selectedCascade = cascadeLists[2]
            cascade = cv2.CascadeClassifier(cascadeLists[2])
        print(text)
    def clickBox(self, state):
        if state == QtCore.Qt.Checked:
            print('Checked')
        else:
            print('Unchecked')
            
    # def onButtonClick(self):
    #         self.calc = External()
    #         self.calc.countChanged.connect(self.onCountChanged)
    #         self.calc.start()

    # def onCountChanged(self, value):
    #     self.progress.setValue(value)
        
    def initUI(self):
        # self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)
        self.setFixedSize(self.width, self.height)
        # self.setStyleSheet("background-color: black;")
        
        # TOOL BAR MENU
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        
        exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close_application)
        fileMenu.addAction(exitButton)
        
        # edit = fileMenu.addMenu("haar Cascade")
        # edit.addAction("Change")
        
        # BUTTON
        button = QPushButton('Start/Stop',self)
        button.setToolTip('Start/Stop The Webcam')
        button.clicked.connect(self.slot_method)
        button.move(self.width / 4, self.height / 4)

        # # COMBO BOX
        combo = QComboBox(self)
        for i in cascadeLists:
            i = i.replace(cascadeLocationFolder + "haarcascade_", '')
            i = i.replace(".xml", '')
            combo.addItem(i)
        combo.activated[str].connect(self.onActivated) 
        combo.move(self.width / 4, self.height / 2)
        
        # CHECK BOX
        CheckBox = QCheckBox("Record Screen")
        CheckBox.setChecked(False)
        CheckBox.stateChanged.connect(self.clickBox)
        CheckBox.move(20, 20)
        
        # Now use a palette to switch to dark colors:
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(palette)

        # PROGRESS BAR
        progress = QProgressBar(self)
        progress.setGeometry(0, self.height - 25, self.width, 25)
        progress.setMaximum(100)
        
        self.show()
    def close_application(self):
        choice = QMessageBox.question(self, 'Exit!',
                                            "Are you sure you want to exit?",
                                            QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            sys.exit()
        else:
            pass
            
def on_exists(fname):
    if os.path.isfile(fname):
        newfile = fname + ".old"
        print("{} -> {}".format(fname, newfile))
        # os.rename(fname, newfile)
        
def removePictures():
    folder = 'C:\\Users\\Jared\\Documents\\Python Scripts\\Face Detection\\Pics'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            x = App()
            x.messageBox(str(e))
            
def makeVideo():
    try:
        # for index, filename in enumerate(sorted(os.listdir("Face Detection\\Pics"))):
        #     print ('{0:02d}. {1}'.format(index + 1, filename))
        # for filename in sorted(os.listdir("Face Detection\\Pics")):
        #     print (filename)
            
        images = [img for img in os.listdir(
            image_folder) if img.endswith(".png")]
        if len(images) == 0:
            x = App()
            x.messageBox("No images found!")
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
        x = App()
        x.messageBox(str(e))
        
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
        x = App()
        x.messageBox(str(e))
        
def btnStop():
    try:
        # makeVideo()
        # removePictures()
        # When everything done, release the capture
        # clip = mp.VideoFileClip(video_name)
        # make the height 360px ( According to moviePy documenation The width is then computed so that the width/height ratio is conserved.)
        # clip_resized = clip.resize(height=360)
        # clip_resized.write_videofile("Face Detection\\output.mp4")
        # os.remove(video_name)
        print("Deleted: {0}".format(video_name))
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        x = App()
        x.messageBox(str(e))
        
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
                    # savePicture(numOfPics)
                    # savePicture(numOfPics)
                    # print("Found {0} faces!".format(len(faces)))
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                btnStop()
                
    except Exception as e:
        x = App()
        x.messageBox(str(e))
    
def Toggle():
    try:
        global start
        start = not start
        if start == True:
            numOfPics = 0
            camRun()
        elif start == False:
            btnStop()
        print(start)
    except Exception as e:
        x = App()
        x.messageBox(str(e))
        
            
if __name__ == '__main__':
    app=QApplication(sys.argv)
    ex=App()
    # camRun()
    sys.exit(app.exec_())
