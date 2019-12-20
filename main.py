from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import *
import sys, os, shutil, json, multiprocessing, cv2, threading
from functools import partial
from os import listdir
from os.path import isfile, join
# CAMERA SCRIPT
import camera
settings_file = os.path.dirname(os.path.realpath(__file__)) + '/settings.json'
settings_json = []

cascade_files_dir = os.path.dirname(os.path.realpath(__file__)) + '/Data Models'
cascade_files = [f for f in listdir(cascade_files_dir) if isfile(join(cascade_files_dir, f))]
isActive = False

saved_color = []
send_email = []
cap_screen = []
record_video = []
smiley_face = []
dark_mode = []
face_detect = []

email_address = []

email_delay = []
picture_delay = []
selected_data_index = []
button_css = ''

class MainMenu(QMainWindow):
    def __init__(self, parent = None):
        super(MainMenu, self).__init__(parent)
        self.menu()
        self.setMinimumSize(400, 320)
        lay = QWidget(self)
        lay.setContentsMargins(5, 5, 5, 5)
        self.setWindowTitle('Control Panel')
        self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogNoButton')))
        self.grid = QGridLayout()
        self.grid.addWidget(self.DelayGroup(), 0, 0)
        self.grid.addWidget(self.ComboBox(), 1, 0)
        self.grid.addWidget(self.CheckGroup(), 0, 1)
        self.grid.addWidget(self.Controll(), 1, 1)
        lay.setLayout(self.grid)
        self.setCentralWidget(lay)


    def menu(self):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode
        self.menubar = self.menuBar()
        self.statusbar = self.statusBar()
        viewMenu = QMenu('View', self)
        
        darkmode = QAction('Dark mode', self, checkable=True)
        darkmode.setStatusTip('enable/disable Dark mode')
        darkmode.setChecked(True if dark_mode[0] == 'True' else False)
        darkmode.triggered.connect(partial(self.checkboxClicked, darkmode, 'Dark mode'))
        viewMenu.addAction(darkmode)

        settingsMenu = QMenu('Configuration', self)
        email = QAction('Set Email', self)
        email.triggered.connect(partial(self.verifyEmailAddress, ''))
        email.setStatusTip('Your email address.')

        recordvideo = QAction('Record Video', self, checkable=True)
        recordvideo.setChecked(True if record_video[0] == 'True' else False)
        recordvideo.triggered.connect(partial(self.checkboxClicked, recordvideo, 'Record Video'))
        recordvideo.setStatusTip('Record footage of the webcam.')
        
        captureScreen = QAction('Record Screen', self, checkable=True)
        captureScreen.setChecked(True if cap_screen[0] == 'True' else False)
        captureScreen.triggered.connect(partial(self.checkboxClicked, captureScreen, 'Capture Screen'))
        captureScreen.setStatusTip('Record footage of the screen.')
        
        sendEmails = QAction('Send Emails', self, checkable=True)
        sendEmails.setChecked(True if send_email[0] == 'True' else False)
        sendEmails.triggered.connect(partial(self.checkboxClicked, sendEmails, 'Send Emails'))
        sendEmails.setStatusTip('Send emails when Motion/Face detected.')
        
        smileyFace = QAction('Smiley Face Addon', self, checkable=True)
        smileyFace.setChecked(True if smiley_face[0] == 'True' else False)
        smileyFace.triggered.connect(partial(self.checkboxClicked, smileyFace, 'Smiley Face Addon'))
        smileyFace.setStatusTip('Make smiley face when *Face detected.')
        
        self.faceDetection = QAction('Face Detection', self, checkable=True)
        self.faceDetection.setChecked(True if face_detect[0] == 'True' else False)
        self.faceDetection.triggered.connect(partial(self.checkboxClicked, self.faceDetection, 'Face Detection'))
        self.faceDetection.setStatusTip('Enabled: Face detection. Disabled: Motion detection.')
        
        
        settingsMenu.addAction(email)
        settingsMenu.addAction(recordvideo)
        settingsMenu.addAction(captureScreen)
        settingsMenu.addAction(sendEmails)
        settingsMenu.addAction(smileyFace)
        settingsMenu.addAction(self.faceDetection)

        self.menubar.addMenu(viewMenu)
        self.menubar.addMenu(settingsMenu)

    def resizeEvent(self, event):
        super(MainMenu, self).resizeEvent(event)
        self.menubar.resize(self.width(), self.menubar.height())

    def verifyEmailAddress(self, s):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, button_css, selected_data_index, face_detect, email_address
        import re
        rx = re.compile(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$")
        email, done1 = QInputDialog.getText(self, 'Email Verification', 'Email Address:', echo=QLineEdit.Normal, text=s)
        if done1:
            if rx.match(email):
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [int(self.cascadeList.currentIndex())],
                    "face detect":[face_detect[0]],
                    "email address": [email]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
                with open(settings_file) as file:
                    saved_color.clear()
                    send_email.clear()
                    cap_screen.clear()
                    record_video.clear()
                    smiley_face.clear()
                    dark_mode.clear()
                    email_delay.clear()
                    picture_delay.clear()
                    face_detect.clear()
                    email_address.clear()
                    settings_json = json.load(file)
                    for info in settings_json:
                        for color in info['saved color']:
                            saved_color.append(color)
                        for screen in info['capture screen']:
                            cap_screen.append(screen)
                        for video in info['record video']:
                            record_video.append(video)
                        for email_b in info['send email']:
                            send_email.append(email_b)
                        for smile in info['smiley face']:
                            smiley_face.append(smile)
                        for dark in info['dark mode']:
                            dark_mode.append(dark)
                        for email_d in info['email delay']:
                            email_delay.append(email_d)
                        for picture in info['picture delay']:
                            picture_delay.append(picture)
                        for ind in info['selected data index']:
                            selected_data_index.append(ind)
                        for face in info['face detect']:
                            face_detect.append(face)
                        for email in info['email address']:
                            email_address.append(email)
                button = QMessageBox.information(self, "Success", f"The email: \"{email}\" has been successfully saved!", QMessageBox.Ok, QMessageBox.Ok)
            else:
                button = QMessageBox.critical(self, "Wrong Email address.", f"\"{email}\" is an Invalid email address, please try again.", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if button == QMessageBox.Yes:
                    self.verifyEmailAddress(email)
                else:
                    return
    def ComboBox(self):
        global selected_data_index
        groupBox = QGroupBox("Recognition type")

        self.cascadeList = QComboBox()
        for i, j in enumerate(cascade_files):
            j = j.replace('haarcascade_', '')
            j = j.replace('.xml', '')
            j = j.replace('_', ' ')
            self.cascadeList.addItem(j)
        self.cascadeList.setCurrentIndex(int(selected_data_index[0]))
        self.cascadeList.setToolTip('A list of diffrent recognition types.')
        self.cascadeList.currentTextChanged.connect(self.comboBoxChanged)
        # self.cascadeList.setStyleSheet('color: white')
        vbox = QVBoxLayout()
        vbox.addWidget(self.cascadeList)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox
    def CheckGroup(self):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode
        groupBox = QGroupBox("Configuration")

        # captureScreen = QCheckBox('Capture Screen')
        captureScreen = QPushButton('Capture Screen')
        captureScreen.setCheckable(True)
        captureScreen.setChecked(True if cap_screen[0] == 'True' else False)
        captureScreen.setStyleSheet('background-color: hsl(126, 81%, 29%)') if cap_screen[0] == 'True' else captureScreen.setStyleSheet('background-color: rgb(106, 11, 11)')
        captureScreen.toggled.connect(lambda:self.checkboxClicked(captureScreen))
        captureScreen.setToolTip('Record your entire screen (*Very performance heavy)')

        RecordVideo = QPushButton('Record Video')
        RecordVideo.setCheckable(True)
        RecordVideo.setChecked(True if record_video[0] == 'True' else False)
        RecordVideo.setStyleSheet('background-color: hsl(126, 81%, 29%)') if record_video[0] == 'True' else RecordVideo.setStyleSheet('background-color: rgb(106, 11, 11)')
        RecordVideo.toggled.connect(lambda:self.checkboxClicked(RecordVideo))
        RecordVideo.setToolTip('Record the webcam.')

        EmailPictures = QPushButton('Send Emails')
        EmailPictures.setCheckable(True)
        EmailPictures.setChecked(True if send_email[0] == 'True' else False)
        EmailPictures.setStyleSheet('background-color: hsl(126, 81%, 29%)') if send_email[0] == 'True' else EmailPictures.setStyleSheet('background-color: rgb(106, 11, 11)')
        EmailPictures.toggled.connect(lambda:self.checkboxClicked(EmailPictures))
        EmailPictures.setToolTip('Sends you an email for the movement it just detected.')

        SmileyFace = QPushButton('Smiley Face Addon')
        SmileyFace.setCheckable(True)
        SmileyFace.setChecked(True if smiley_face[0] == 'True' else False)
        SmileyFace.setStyleSheet('background-color: hsl(126, 81%, 29%)') if smiley_face[0] == 'True' else SmileyFace.setStyleSheet('background-color: rgb(106, 11, 11)')
        SmileyFace.toggled.connect(lambda:self.checkboxClicked(SmileyFace))
        SmileyFace.setToolTip('Will draw a smiley face where your face is.')

        DarkTheme = QPushButton('Dark mode')
        DarkTheme.setCheckable(True)
        DarkTheme.setChecked(True if dark_mode[0] == 'True' else False)
        DarkTheme.setText('Dark mode' if dark_mode[0] == 'True' else 'Light mode')
        DarkTheme.setStyleSheet('background-color: hsl(126, 81%, 29%)') if dark_mode[0] == 'True' else DarkTheme.setStyleSheet('background-color: rgb(106, 11, 11)')
        DarkTheme.toggled.connect(lambda:self.checkboxClicked(DarkTheme))
        DarkTheme.setToolTip('Enabled Dark/Light theme for window.')

        self.FaceDetection = QPushButton('Face Detection')
        self.FaceDetection.setCheckable(True)
        self.FaceDetection.setText('Face Detection' if face_detect[0] == 'True' else 'Motion Detection')
        self.FaceDetection.setChecked(True if face_detect[0] == 'True' else False)
        self.FaceDetection.setStyleSheet('background-color: hsl(126, 81%, 29%)') if face_detect[0] == 'True' else self.FaceDetection.setStyleSheet('background-color: rgb(106, 11, 11)')
        self.FaceDetection.toggled.connect(lambda:self.checkboxClicked(self.FaceDetection))
        self.FaceDetection.setToolTip('You can either use face detection or motion detection.')

        vbox = QVBoxLayout()
        # vbox.addWidget(captureScreen)
        # vbox.addWidget(RecordVideo)
        # vbox.addWidget(EmailPictures)
        # vbox.addWidget(SmileyFace)
        # vbox.addWidget(DarkTheme)
        # vbox.addWidget(self.FaceDetection)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)
        return groupBox
    def DelayGroup(self):
        global email_delay, picture_delay, saved_color
        groupBox = QGroupBox("Delays")

        Label1 = QLabel('Email Sending Delay:')
        self.EmailDelay = QLineEdit(str(email_delay[0]))
        self.EmailDelay.setValidator(QIntValidator())
        self.EmailDelay.textChanged.connect(self.lineEditChanged)
        self.EmailDelay.setToolTip(f'Program will wait {self.EmailDelay.text()} before sending another email')

        Labe2 = QLabel('Take Picture Delay:')
        self.ImageDelay = QLineEdit(str(picture_delay[0]))
        self.ImageDelay.setValidator(QIntValidator())
        self.ImageDelay.textChanged.connect(self.lineEditChanged)
        self.ImageDelay.setToolTip(f'Program will wait {self.ImageDelay.text()} before taking another picture (*Record video)')

        Labe3 = QLabel('Color:')

        self.ColorDialog = QPushButton('Box Color')
        self.ColorDialog.clicked.connect(self.Open_Color_Dialog)
        self.ColorDialog.setToolTip('Change the color of lines in face detection.')
        self.ColorDialog.setStyleSheet(button_css)
        vbox = QVBoxLayout()
        vbox.addWidget(Label1)
        vbox.addWidget(self.EmailDelay)
        vbox.addWidget(Labe2)
        vbox.addWidget(self.ImageDelay)
        vbox.addWidget(Labe3)
        vbox.addWidget(self.ColorDialog)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox
    def Controll(self):
        groupBox = QGroupBox("Control")
        self.start = QPushButton('Start', self)
        self.start.setStyleSheet('background-color: hsl(126, 81%, 29%)')
        self.start.setToolTip('Start/Stop the webcam')
        self.start.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaPlay')))
        self.start.clicked.connect(self.startCamera)
        vbox = QVBoxLayout()
        vbox.addWidget(self.start)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox
    def comboBoxChanged(self):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, button_css, selected_data_index, face_detect, email_address
        settings_json.pop(0)
        settings_json.append({
            "saved color": [saved_color[0], saved_color[1], saved_color[2]],
            "capture screen": [cap_screen[0]],
            "record video": [record_video[0]],
            "smiley face": [smiley_face[0]],
            "dark mode": [dark_mode[0]],
            "send email": [send_email[0]],
            "email delay": [email_delay[0]],
            "picture delay": [picture_delay[0]],
            "selected data index": [int(self.cascadeList.currentIndex())],
            "face detect":[face_detect[0]],
            "email address": [email_address[0]]
        })
        with open(settings_file, mode='w+', encoding='utf-8') as file:
            json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        with open(settings_file) as file:
            saved_color.clear()
            send_email.clear()
            cap_screen.clear()
            record_video.clear()
            smiley_face.clear()
            dark_mode.clear()
            email_delay.clear()
            picture_delay.clear()
            selected_data_index.clear()
            face_detect.clear()
            email_address.clear()
            settings_json = json.load(file)
            for info in settings_json:
                for color in info['saved color']:
                    saved_color.append(color)
                for screen in info['capture screen']:
                    cap_screen.append(screen)
                for video in info['record video']:
                    record_video.append(video)
                for email_b in info['send email']:
                    send_email.append(email_b)
                for smile in info['smiley face']:
                    smiley_face.append(smile)
                for dark in info['dark mode']:
                    dark_mode.append(dark)
                for email_d in info['email delay']:
                    email_delay.append(email_d)
                for picture in info['picture delay']:
                    picture_delay.append(picture)
                for ind in info['selected data index']:
                    selected_data_index.append(ind)
                for face in info['face detect']:
                    face_detect.append(face)
                for email in info['email address']:
                    email_address.append(email)
    def lineEditChanged(self):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, selected_data_index, face_detect, email_address

        self.EmailDelay.setToolTip(f'Program will wait {self.EmailDelay.text()} before sending another email')
        self.ImageDelay.setToolTip(f'Program will wait {self.ImageDelay.text()} before taking another picture (*Record video)')

        if self.ImageDelay.text() == '':
            return
        if self.EmailDelay.text() == '':
            return
        if int(self.EmailDelay.text()) <= 6:
            self.EmailDelay.setText('7')

        if int(self.ImageDelay.text()) <= 4:
            self.ImageDelay.setText('5')

        if int(self.ImageDelay.text()) >= 4 and int(self.EmailDelay.text()) >= 6:
            settings_json.pop(0)
            settings_json.append({
                "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                "capture screen": [cap_screen[0]],
                "record video": [record_video[0]],
                "smiley face": [smiley_face[0]],
                "dark mode": [dark_mode[0]],
                "send email": [send_email[0]],
                "email delay": [int(self.EmailDelay.text())],
                "picture delay": [int(self.ImageDelay.text())],
                "selected data index": [selected_data_index[0]],
                "face detect":[face_detect[0]],
                "email address": [email_address[0]]
            })
            with open(settings_file, mode='w+', encoding='utf-8') as file:
                json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            with open(settings_file) as file:
                saved_color.clear()
                send_email.clear()
                cap_screen.clear()
                record_video.clear()
                smiley_face.clear()
                dark_mode.clear()
                email_delay.clear()
                picture_delay.clear()
                selected_data_index.clear()
                face_detect.clear()
                email_address.clear()
                settings_json = json.load(file)
                for info in settings_json:
                    for color in info['saved color']:
                        saved_color.append(color)
                    for screen in info['capture screen']:
                        cap_screen.append(screen)
                    for video in info['record video']:
                        record_video.append(video)
                    for email_b in info['send email']:
                        send_email.append(email_b)
                    for smile in info['smiley face']:
                        smiley_face.append(smile)
                    for dark in info['dark mode']:
                        dark_mode.append(dark)
                    for email_d in info['email delay']:
                        email_delay.append(email_d)
                    for picture in info['picture delay']:
                        picture_delay.append(picture)
                    for ind in info['selected data index']:
                        selected_data_index.append(ind)
                    for face in info['face detect']:
                        face_detect.append(face)
                    for email in info['email address']:
                        email_address.append(email)
    @pyqtSlot()
    def Open_Color_Dialog(self):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, button_css, selected_data_index, face_detect, email_address
        color = QColorDialog.getColor()
        if color.isValid():
            settings_json.pop(0)
            settings_json.append({
                "saved color": [color.red(), color.green(), color.blue()],
                "capture screen": [cap_screen[0]],
                "record video": [record_video[0]],
                "smiley face": [smiley_face[0]],
                "dark mode": [dark_mode[0]],
                "send email": [send_email[0]],
                "email delay": [email_delay[0]],
                "picture delay": [picture_delay[0]],
                "selected data index": [selected_data_index[0]],
                "face detect":[face_detect[0]],
                "email address": [email_address[0]]
            })
            with open(settings_file, mode='w+', encoding='utf-8') as file:
                json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            with open(settings_file) as file:
                saved_color.clear()
                send_email.clear()
                cap_screen.clear()
                record_video.clear()
                smiley_face.clear()
                dark_mode.clear()
                email_delay.clear()
                picture_delay.clear()
                selected_data_index.clear()
                face_detect.clear()
                email_address.clear()
                settings_json = json.load(file)
                for info in settings_json:
                    for color in info['saved color']:
                        saved_color.append(color)
                    for screen in info['capture screen']:
                        cap_screen.append(screen)
                    for video in info['record video']:
                        record_video.append(video)
                    for email_b in info['send email']:
                        send_email.append(email_b)
                    for smile in info['smiley face']:
                        smiley_face.append(smile)
                    for dark in info['dark mode']:
                        dark_mode.append(dark)
                    for email_d in info['email delay']:
                        email_delay.append(email_d)
                    for picture in info['picture delay']:
                        picture_delay.append(picture)
                    for ind in info['selected data index']:
                        selected_data_index.append(ind)
                    for face in info['face detect']:
                        face_detect.append(face)
                    for email in info['email address']:
                        email_address.append(email)

        button_css = 'background-color: rgb(' + str(saved_color[0]) + ', ' + str(saved_color[1]) + ', ' + str(saved_color[2]) + ');'
        self.ColorDialog.setStyleSheet(button_css)
    def checkboxClicked(self, b, name, m):
        print(b.isChecked())
        print(name)
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, selected_data_index, face_detect, email_address
        # b.setStyleSheet('background-color: hsl(126, 81%, 29%)') if b.isChecked() == True else b.setStyleSheet('background-color: rgb(106, 11, 11)')
        if name == "Capture Screen":
            if b.isChecked() == True:
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": ["True"],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": ["False"],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == "Record Video":
            if b.isChecked() == True:
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": ['True'],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": ['False'],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == "Send Emails":
            if b.isChecked() == True:
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": ['True'],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": ['False'],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == "Smiley Face Addon":
            if b.isChecked() == True:
                if face_detect[0] == 'False' or not self.cascadeList.currentIndex() == 7 and not self.cascadeList.currentIndex() == 6 and not self.cascadeList.currentIndex() == 5 and not self.cascadeList.currentIndex() == 4:
                    buttonReply = QMessageBox.question(self, "Enable 'face detection'", "You currently do not have 'face detection' enabled, if you want to get the best result, I would suggest you enable it.\nDo you want to enable 'face detection'?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    if buttonReply == QMessageBox.Yes:
                        self.cascadeList.setCurrentIndex(7)
                        self.faceDetection.setChecked(True)
                        self.checkboxClicked(self.faceDetection, 'Face Detection', '')
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": ['True'],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": ['False'],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == "Dark mode" or name == 'Light mode':
            if b.isChecked() == True:
                b.setText('Dark mode')
                app.setStyle("Fusion")
                palette = QPalette()
                gradient = QLinearGradient(0, 0, 0, 400)
                gradient.setColorAt(0.0, QColor(40, 40, 40))
                gradient.setColorAt(1.0, QColor(30, 30, 30))
                palette.setBrush(QPalette.Window, QBrush(gradient))
                palette.setColor(QPalette.WindowText, Qt.white)
                palette.setColor(QPalette.Base, QColor(25, 25, 25))
                palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
                palette.setColor(QPalette.ToolTipBase, Qt.white)
                palette.setColor(QPalette.ToolTipText, Qt.white)
                palette.setColor(QPalette.Text, Qt.white)
                palette.setColor(QPalette.Button, QColor(30, 30, 30))
                palette.setColor(QPalette.ButtonText, Qt.white)
                palette.setColor(QPalette.BrightText, Qt.red)
                palette.setColor(QPalette.Link, QColor(42, 130, 218))
                palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
                palette.setColor(QPalette.HighlightedText, Qt.black)
                app.setPalette(palette)
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": ['True'],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                b.setText('Light mode')
                app.setStyle("Fusion")
                app.setPalette(QApplication.style().standardPalette())
                palette = QPalette()
                gradient = QLinearGradient(0, 0, 0, 400)
                gradient.setColorAt(0.0, QColor(240, 240, 240))
                gradient.setColorAt(1.0, QColor(215, 215, 215))
                palette.setColor(QPalette.ButtonText, Qt.black)
                palette.setBrush(QPalette.Window, QBrush(gradient))
                app.setPalette(palette)
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": ['False'],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == "Face Detection" or name == 'Motion Detection':
            if b.isChecked() == True:
                b.setText('Face Detection')
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":['True'],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                b.setText('Motion Detection')
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":['False'],
                    "email address": [email_address[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        with open(settings_file) as file:
            saved_color.clear()
            send_email.clear()
            cap_screen.clear()
            record_video.clear()
            smiley_face.clear()
            dark_mode.clear()
            email_delay.clear()
            picture_delay.clear()
            face_detect.clear()
            email_address.clear()
            settings_json = json.load(file)
            for info in settings_json:
                for color in info['saved color']:
                    saved_color.append(color)
                for screen in info['capture screen']:
                    cap_screen.append(screen)
                for video in info['record video']:
                    record_video.append(video)
                for email_b in info['send email']:
                    send_email.append(email_b)
                for smile in info['smiley face']:
                    smiley_face.append(smile)
                for dark in info['dark mode']:
                    dark_mode.append(dark)
                for email_d in info['email delay']:
                    email_delay.append(email_d)
                for picture in info['picture delay']:
                    picture_delay.append(picture)
                for ind in info['selected data index']:
                    selected_data_index.append(ind)
                for face in info['face detect']:
                    face_detect.append(face)
                for email in info['email address']:
                    email_address.append(email)
    def startCamera(self):
        global isActive
        isActive = not isActive
        if not isActive:
            self.start.setText('Start')
            self.start.setStyleSheet('background-color: hsl(126, 81%, 29%)')
            self.start.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaPlay')))
            self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogNoButton')))
            # multiprocessing.Process(target=live.end_cam).start()
            camera.end_cam()
        else:
            self.start.setStyleSheet('background-color: rgb(106, 11, 11)')
            self.start.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaStop')))
            self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogYesButton')))
            self.start.setText('Stop')
            print('closed capture')
            cv2.destroyAllWindows()
            camera.start_cam()
            # multiprocessing.Process(target=live.start_cam).start()
        # print(isActive)

# class
if __name__ == '__main__':
    if os.path.exists(settings_file):
        with open(settings_file) as file:
            settings_json = json.load(file)
            for info in settings_json:
                for color in info['saved color']:
                    saved_color.append(color)
                for screen in info['capture screen']:
                    cap_screen.append(screen)
                for video in info['record video']:
                    record_video.append(video)
                for email_b in info['send email']:
                    send_email.append(email_b)
                for smile in info['smiley face']:
                    smiley_face.append(smile)
                for dark in info['dark mode']:
                    dark_mode.append(dark)
                for email_d in info['email delay']:
                    email_delay.append(email_d)
                for picture in info['picture delay']:
                    picture_delay.append(picture)
                for ind in info['selected data index']:
                    selected_data_index.append(ind)
                for face in info['face detect']:
                    face_detect.append(face)
                for email in info['email address']:
                    email_address.append(email)
    elif not os.path.exists(settings_file):
        file = open(settings_file, "w+")
        file.write(
"""[
    {
        \"saved color\":[\"0\", \"255\", \"0\"],
        \"capture screen\": [\"False\"],
        \"record video\": [\"False\"],
        \"smiley face\": [\"False\"],
        \"dark mode\": [\"True\"],
        \"send email\": [\"True\"],
        \"email delay\": [\"10\"],
        \"picture delay\": [\"5\"],
        \"selected data index\": [\"7\"],
        \"face detect\": [\"True\"],
        \"email address\": [\"\"]
    }
]"""
)
        file.close()
        with open(settings_file) as file:
            settings_json = json.load(file)
            for info in settings_json:
                for color in info['saved color']:
                    saved_color.append(color)
                for screen in info['capture screen']:
                    cap_screen.append(screen)
                for video in info['record video']:
                    record_video.append(video)
                for email in info['send email']:
                    send_email.append(email)
                for smile in info['smiley face']:
                    smiley_face.append(smile)
                for dark in info['dark mode']:
                    dark_mode.append(dark)
                for email_d in info['email delay']:
                    email_delay.append(email_d)
                for picture in info['picture delay']:
                    picture_delay.append(picture)
                for ind in info['selected data index']:
                    selected_data_index.append(ind)
                for face in info['face detect']:
                    face_detect.append(face)
                for email in info['email address']:
                    email_address.append(email)
    button_css = 'background-color: rgb(' + str(saved_color[0]) + ', ' + str(saved_color[1]) + ', ' + str(saved_color[2]) + ')'

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    if dark_mode[0] == 'True':
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0.0, QColor(40, 40, 40))
        gradient.setColorAt(1.0, QColor(30, 30, 30))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(30, 30, 30))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(palette)
    else:
        app.setPalette(QApplication.style().standardPalette())
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0.0, QColor(240, 240, 240))
        gradient.setColorAt(1.0, QColor(215, 215, 215))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setBrush(QPalette.Window, QBrush(gradient))
        app.setPalette(palette)
    main = MainMenu()
    main.show()
    # START_CAMERA = multiprocessing.Process(target=MainMenu)
    sys.exit(app.exec_())
    # START_CAMERA.start()
