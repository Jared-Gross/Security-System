#!/usr/bin/env python3
import webbrowser, socket, sys, os, shutil, json, multiprocessing, cv2, atexit, threading, re, time, imutils, argparse
from imutils.video import VideoStream
from os.path import isfile, join
from functools import partial
from datetime import datetime
from natsort import natsorted
from os import listdir
from IPy import IP
from flask import Response, render_template, Flask, g, request
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import *
# sudo python3 -m pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org [NAME]

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
frame = None
ret = None

outputFrame = None

cycles_file = os.path.dirname(os.path.realpath(__file__)) + '/cycles.json'
cycles_json = []

OnToList = []
OnFromList = []
OffToList = []
OffFromList = []
alwaysOn = []
all_textboxes = []
OnTo_textboxes = []
OnFrom_textboxes = []
OffTo_textboxes = []
OffFrom_textboxes = []

isTimeToSendEmail = False
running = True

framesPerSecond = 0
lock = threading.Lock()
appWeb = Flask(__name__)
auto_start_server = []
ip = []
class MainMenu(QMainWindow):
    def __init__(self, parent = None):
        super(MainMenu, self).__init__(parent)
        mainlay = QWidget(self)
        mainlay.setContentsMargins(5, 5, 5, 5)
        lay = QVBoxLayout()
        top = QHBoxLayout()
        bottom = QHBoxLayout()
        self.setWindowTitle('J-Detection - Main Menu')
        self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))
        self.cameraScreen = QLabel(self)
        self.cameraScreen.setStyleSheet('border-radius: 3px; border-style: none; border: 1px solid black; background-color: rgb(10,10,10);')
        self.cameraScreen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cameraScreen.setAlignment(Qt.AlignCenter)
        top.addWidget(self.cameraScreen)
        self.grid = QGridLayout()
        self.grid.setRowStretch(0, 1)
        self.grid.addWidget(self.ComboBox(), 1, 0)
        bottom.addLayout(self.grid)
        lay.addLayout(top)
        lay.addLayout(bottom)
        mainlay.setLayout(lay)
        self.setCentralWidget(mainlay)
        self.menu()
        th = Thread(self)
        th.changePixmap.connect(self.setImage)
        camera.start_cam()
        th.start()
    def open_cycle_menu(self):
        self.c = CycleMenu()
        self.c.show()
    def closeEvent(self, event):
        exit_handler()
    @pyqtSlot(QImage)
    def setImage(self, image):
        self.setWindowTitle("J-Detection - Main Menu - {0:.2f} FPS".format(round(framesPerSecond,2)))
        self.cameraScreen.setPixmap(QPixmap.fromImage(image))
    def menu(self):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, selected_data_index, face_detect, email_address
        self.menubar = self.menuBar()
        self.statusbar = self.statusBar()
        serverMenu = QMenu('Server', self)
        self.autoStartServer = QAction('Auto start.', self, checkable=True)
        self.autoStartServer.setStatusTip('Start the server when program is executed. (Program restart is required!)')
        self.autoStartServer.setChecked(True if auto_start_server[0] == 'True' else False)
        self.autoStartServer.triggered.connect(self.auto_start)
        serverMenu.addAction(self.autoStartServer)
        if auto_start_server[0] == 'True':
            viewServer = QAction('Visit', self)
            viewServer.setStatusTip(f"Opens a new tab on your default browser to where the server is hosted. http://{ip[0]}:5000")
            viewServer.triggered.connect(self.visitServer)
            serverMenu.addAction(viewServer)
        self.setIP = QAction(f'Change host IP address', self)
        self.setIP.setStatusTip(f'The server will connect to the current IP address - {ip[0]}')
        self.setIP.triggered.connect(partial(self.change_ip_address, ''))
        serverMenu.addAction(self.setIP)
        
        viewMenu = QMenu('View', self)
        themesMenu = QMenu('Themes', self)
        
        self.systemmode = QAction('System default', self, checkable = True)
        self.systemmode.setStatusTip('enable/disable Light mode')
        self.systemmode.setChecked(True if dark_mode[0] == '0' else False)
        self.systemmode.triggered.connect(partial(self.checkboxClicked, self.systemmode, 'System mode'))
        
        self.darkmode = QAction('Dark mode', self, checkable = True)
        self.darkmode.setStatusTip('enable/disable Dark mode')
        self.darkmode.setChecked(True if dark_mode[0] == '1' else False)
        self.darkmode.triggered.connect(partial(self.checkboxClicked, self.darkmode, 'Dark mode'))
        
        self.lightmode = QAction('Light mode', self, checkable = True)
        self.lightmode.setStatusTip('enable/disable Light mode')
        self.lightmode.setChecked(True if dark_mode[0] == '2' else False)
        self.lightmode.triggered.connect(partial(self.checkboxClicked, self.lightmode, 'Light mode'))
        
        themesMenu.addAction(self.systemmode)
        themesMenu.addAction(self.darkmode)
        themesMenu.addAction(self.lightmode)
        viewMenu.addMenu(themesMenu)
        
        self.settingsMenu = QMenu('Configuration', self)
        self.email = QAction(self)
        
        self.removeEmail = QAction('Remove Email Address', self)
        self.removeEmail.triggered.connect(self.removeEmailAddress)
        self.removeEmail.setStatusTip(f'Remove an email address from {email_address[0]}.')
        
        if email_address[0] == '':
            self.email.setText('Set Email')
            self.email.triggered.connect(partial(self.verifyEmailAddress, '@gmail.com', True))
            self.email.setStatusTip('Your email address is currently set too: None')
        else:
            self.email.setText('Add Email')
            self.email.triggered.connect(partial(self.verifyEmailAddress, '@gmail.com', True))
            self.email.setStatusTip(f'Your email address is currently set too: {email_address[0]}')
            
        self.emailDelay = QAction(f'Set Email send delay - {email_delay[0]}')
        self.emailDelay.triggered.connect(partial(self.verifyEmailDelay))
        if email_delay[0] == '': self.emailDelay.setStatusTip('Your email send delay is currently set too: None')
        else: self.emailDelay.setStatusTip(f'Your email send delay is currently set too: {email_delay[0]}')
            
        self.colorMenu = QAction('Color')
        self.colorMenu.triggered.connect(partial(self.Open_Color_Dialog))
        self.colorMenu.setStatusTip('Change the color of the bounding boxes in program.')
        
        self.cycleMenu = QAction('Cycle Menu')
        self.cycleMenu.triggered.connect(partial(self.open_cycle_menu))
        self.cycleMenu.setStatusTip('Custimze when the program is active.')
        
        recordvideo = QAction('Record Video', self, checkable=True)
        recordvideo.setChecked(True if record_video[0] == 'True' else False)
        recordvideo.triggered.connect(partial(self.checkboxClicked, recordvideo, 'Record Video'))
        recordvideo.setStatusTip('Record footage of the webcam.')
        
        captureScreen = QAction('Capture Screen', self, checkable=True)
        captureScreen.setChecked(True if cap_screen[0] == 'True' else False)
        captureScreen.triggered.connect(partial(self.checkboxClicked, captureScreen, 'Capture Screen'))
        captureScreen.setStatusTip('Take screenshot of main moniter instead of the webcam.')
        
        self.sendEmails = QAction('Send Emails', self, checkable=True)
        self.sendEmails.setChecked(True if send_email[0] == 'True' else False)
        self.sendEmails.triggered.connect(partial(self.checkboxClicked, self.sendEmails, 'Send Emails'))
        self.sendEmails.setStatusTip('Send emails when Motion/Face detected.')
        
        smileyFace = QAction('Smiley Face Addon', self, checkable=True)
        smileyFace.setChecked(True if smiley_face[0] == 'True' else False)
        smileyFace.triggered.connect(partial(self.checkboxClicked, smileyFace, 'Smiley Face Addon'))
        smileyFace.setStatusTip('Make smiley face when *Face detected.')
        
        self.faceDetection = QAction(f'{self.cascadeList.currentText()} Detection', self, checkable=True)
        self.faceDetection.setChecked(True if face_detect[0] == 'True' else False)
        self.faceDetection.triggered.connect(partial(self.checkboxClicked, self.faceDetection, 'Face Detection'))
        self.faceDetection.setStatusTip(f'Enable: {self.cascadeList.currentText()} detection. Disable: Motion detection.')
        
        self.motionDetection = QAction('Motion Detection', self, checkable=True)
        self.motionDetection.setChecked(True if face_detect[0] == 'False' else False)
        self.motionDetection.triggered.connect(partial(self.checkboxClicked, self.motionDetection, 'Motion Detection'))
        self.motionDetection.setStatusTip(f'Enable: Motion detection. Disable: {self.cascadeList.currentText()} detection.')
        
        detectionMenu = QMenu('Detection', self)
        detectionMenu.addAction(self.faceDetection)
        detectionMenu.addAction(self.motionDetection)
        
        self.settingsMenu.addAction(self.cycleMenu)
        self.settingsMenu.addAction(self.colorMenu)
        # self.settingsMenu.addAction(recordvideo)
        self.settingsMenu.addAction(captureScreen)
        self.settingsMenu.addAction(self.sendEmails)
        self.settingsMenu.addAction(smileyFace)
        self.settingsMenu.addMenu(detectionMenu)
        self.settingsMenu.addAction(self.emailDelay)
        self.settingsMenu.addAction(self.email)
        if not email_address[0] == '': self.settingsMenu.addAction(self.removeEmail)
        self.menubar.addMenu(viewMenu)
        self.menubar.addMenu(self.settingsMenu)
        self.menubar.addMenu(serverMenu)
    def resizeEvent(self, event):
        super(MainMenu, self).resizeEvent(event)
        self.menubar.resize(self.width(), self.menubar.height())
    def change_ip_address(self, t):
        global saved_color, auto_start_server, ip, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, button_css, selected_data_index, face_detect, email_address
        if t == '': inputIP, done1 = QInputDialog.getText(self, 'Change IP', 'IP Address:', echo=QLineEdit.Normal, text=str(ip[0]))
        else: inputIP, done1 = QInputDialog.getText(self, 'Change IP', 'IP Address:', echo=QLineEdit.Normal, text=t)
        if done1:
            try:
                if IP(inputIP):
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
                        "email address": [email_address[0]],
                        "server auto start": [auto_start_server[0]],
                        "host address": [inputIP]
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
                        auto_start_server.clear()
                        ip.clear()
                        settings_json = json.load(file)
                        for info in settings_json:
                            for ind in info['selected data index']: selected_data_index.append(ind)
                            for dark in info['dark mode']: dark_mode.append(dark)
                            for face in info['face detect']: face_detect.append(face)
                            for color in info['saved color']: saved_color.append(color)
                            for video in info['record video']: record_video.append(video)
                            for smile in info['smiley face']: smiley_face.append(smile)
                            for email in info['email address']: email_address.append(email)
                            for screen in info['capture screen']: cap_screen.append(screen)
                            for email_b in info['send email']: send_email.append(email_b)
                            for email_d in info['email delay']: email_delay.append(email_d)
                            for picture in info['picture delay']: picture_delay.append(picture)
                            for autostart in info['server auto start']: auto_start_server.append(autostart)
                            for ipaddress in info['host address']: ip.append(ipaddress)
                    
                    self.setIP.setStatusTip(f'The server will connect to the current IP address - {ip[0]}')
                    return
                else:  return
            except ValueError:
                button = QMessageBox.critical(self, "Attention", f"The IP address: \"{inputIP}\" is not a valid IP address.\n\nWould you like to try again?", QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Yes)
                if button == QMessageBox.Yes: self.change_ip_address(inputIP)
                else: return  
        else: return
    def verifyEmailAddress(self, s, add):
        global saved_color, auto_start_server, ip, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, button_css, selected_data_index, face_detect, email_address
        rx = re.compile(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$")
        email, done1 = QInputDialog.getText(self, 'Add Email', 'Email Address:', echo=QLineEdit.Normal, text=s)
        if done1:
            t = email
            if rx.match(email):
                if add:
                    temp = email_address
                    temp.append(email)
                    temp = ", ".join(email_address)
                    if temp[0] == ",":
                        temp = temp[2:]
                    email = temp
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
                    "selected data index": [int(self.cascadeList.currentIndex())],
                    "face detect":[face_detect[0]],
                    "email address": [email],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
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
                    auto_start_server.clear()
                    ip.clear()
                    settings_json = json.load(file)
                    for info in settings_json:
                        for ind in info['selected data index']: selected_data_index.append(ind)
                        for dark in info['dark mode']: dark_mode.append(dark)
                        for face in info['face detect']: face_detect.append(face)
                        for color in info['saved color']: saved_color.append(color)
                        for video in info['record video']: record_video.append(video)
                        for smile in info['smiley face']: smiley_face.append(smile)
                        for email in info['email address']: email_address.append(email)
                        for screen in info['capture screen']: cap_screen.append(screen)
                        for email_b in info['send email']: send_email.append(email_b)
                        for email_d in info['email delay']: email_delay.append(email_d)
                        for picture in info['picture delay']: picture_delay.append(picture)
                        for autostart in info['server auto start']: auto_start_server.append(autostart)
                        for ipaddress in info['host address']: ip.append(ipaddress)
                self.email.setText(f'Add Email')
                self.email.setStatusTip(f'Your email address\'s is currently set too: {email_address[0]}')
                self.removeEmail.setStatusTip(f'Remove an email address from {email_address[0]}.')
                self.settingsMenu.addAction(self.removeEmail)
                self.sendEmails.setChecked(True if send_email[0] == 'True' else False)
            else:
                button = QMessageBox.critical(self, "Wrong Email address.", f"\"{email}\" is an Invalid email address, please try again.", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if button == QMessageBox.Yes:
                    self.verifyEmailAddress(t, add)
                else:
                    return
    def removeEmailAddress(self):
        global saved_color, auto_start_server, ip, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, button_css, selected_data_index, face_detect, email_address
        email_typed = ''
        email_typed, done1 = QInputDialog.getText(self, 'Remove Email', f'Which email would you like to remve?\n\n{email_address[0]}', echo=QLineEdit.Normal, text='')
        found = False
        if done1:
            temp = email_address[0].split(', ')
            for i, j in enumerate(temp):
                if email_typed == j and not found:
                    temp.pop(i)
                    found = True
                    continue
                if found:
                    continue
            if not found:
                button = QMessageBox.critical(self, "Email address not found.", f"\"{email_typed}\" is an Invalid email address, please try again.", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if button == QMessageBox.Yes:
                    self.removeEmailAddress()
                else:
                    return
            if found:
                print(temp)
                temp = ", ".join(temp)
                print(temp)
                if any((c in temp) for c in temp) and temp[0] == ",":
                    temp = temp[2:]
                email = temp
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
                    "email address": [email],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
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
                    auto_start_server.clear()
                    ip.clear()
                    settings_json = json.load(file)
                    for info in settings_json:
                        for ind in info['selected data index']: selected_data_index.append(ind)
                        for dark in info['dark mode']: dark_mode.append(dark)
                        for face in info['face detect']: face_detect.append(face)
                        for color in info['saved color']: saved_color.append(color)
                        for video in info['record video']: record_video.append(video)
                        for smile in info['smiley face']: smiley_face.append(smile)
                        for email in info['email address']: email_address.append(email)
                        for screen in info['capture screen']: cap_screen.append(screen)
                        for email_b in info['send email']: send_email.append(email_b)
                        for email_d in info['email delay']: email_delay.append(email_d)
                        for picture in info['picture delay']: picture_delay.append(picture)
                        for autostart in info['server auto start']: auto_start_server.append(autostart)
                        for ipaddress in info['host address']: ip.append(ipaddress)
                self.email.setText(f'Add Email')
                self.email.setStatusTip(f'Your email address is currently set too: {email_address[0]}')
                self.removeEmail.setStatusTip(f'Remove an email address from {email_address[0]}.')
                self.settingsMenu.addAction(self.removeEmail)
    def ComboBox(self):
        global selected_data_index
        groupBox = QGroupBox("Recognition type")

        self.cascadeList = QComboBox()
        for i, j in enumerate(cascade_files):
            j = j.replace('haarcascade_', '')
            j = j.replace('.xml', '')
            j = j.replace('_', ' ')
            j = list(j)
            j[0] = j[0].capitalize()
            j = ''.join(j)
            self.cascadeList.addItem(j)
        self.cascadeList.setCurrentIndex(int(selected_data_index[0]))
        self.cascadeList.setToolTip('A list of diffrent recognition types.')
        self.cascadeList.currentTextChanged.connect(self.comboBoxChanged)
        vbox = QVBoxLayout()
        vbox.addWidget(self.cascadeList)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)
        return groupBox
    def comboBoxChanged(self):
        global saved_color, send_email, ip, auto_start_server, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, button_css, selected_data_index, face_detect, email_address
        self.motionDetection.setStatusTip(f'Enable: Motion detection. Disable: {self.cascadeList.currentText()} detection.')
        self.faceDetection.setStatusTip(f'Enable: {self.cascadeList.currentText()} detection. Disable: Motion detection.')
        self.faceDetection.setText(f'{self.cascadeList.currentText()} Detection')
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
            "email address": [email_address[0]],
            "server auto start": [auto_start_server[0]],
            "host address": [ip[0]]
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
            auto_start_server.clear()
            ip.clear()
            settings_json = json.load(file)
            for info in settings_json:
                for ind in info['selected data index']: selected_data_index.append(ind)
                for dark in info['dark mode']: dark_mode.append(dark)
                for face in info['face detect']: face_detect.append(face)
                for color in info['saved color']: saved_color.append(color)
                for video in info['record video']: record_video.append(video)
                for smile in info['smiley face']: smiley_face.append(smile)
                for email in info['email address']: email_address.append(email)
                for screen in info['capture screen']: cap_screen.append(screen)
                for email_b in info['send email']: send_email.append(email_b)
                for email_d in info['email delay']: email_delay.append(email_d)
                for picture in info['picture delay']: picture_delay.append(picture)
                for autostart in info['server auto start']: auto_start_server.append(autostart)
                for ipaddress in info['host address']: ip.append(ipaddress)
    def verifyEmailDelay(self):
        global saved_color, auto_start_server, ip, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, button_css, selected_data_index, face_detect, email_address
        delay, done1 = QInputDialog.getDouble(self, "Get double","Value:", int(email_delay[0]), 10, 999999, 0)
        if done1:
            if delay >= 10:
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": [dark_mode[0]],
                    "send email": [send_email[0]],
                    "email delay": [delay],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [int(self.cascadeList.currentIndex())],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
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
                    auto_start_server.clear()
                    ip.clear()
                    settings_json = json.load(file)
                    for info in settings_json:
                        for ind in info['selected data index']: selected_data_index.append(ind)
                        for dark in info['dark mode']: dark_mode.append(dark)
                        for face in info['face detect']: face_detect.append(face)
                        for color in info['saved color']: saved_color.append(color)
                        for video in info['record video']: record_video.append(video)
                        for smile in info['smiley face']: smiley_face.append(smile)
                        for email in info['email address']: email_address.append(email)
                        for screen in info['capture screen']: cap_screen.append(screen)
                        for email_b in info['send email']: send_email.append(email_b)
                        for email_d in info['email delay']: email_delay.append(email_d)
                        for picture in info['picture delay']: picture_delay.append(picture)
                        for autostart in info['server auto start']: auto_start_server.append(autostart)
                        for ipaddress in info['host address']: ip.append(ipaddress)
                # button = QMessageBox.information(self, "Success", f"The email: \"{email}\" has been successfully saved!", QMessageBox.Ok, QMessageBox.Ok)
                self.emailDelay.setText(f'Set Email send delay - {email_delay[0]}')
                self.emailDelay.setStatusTip(f'Your email send delay is currently set too: {email_delay[0]}')
    @pyqtSlot()
    def Open_Color_Dialog(self):
        global saved_color, auto_start_server, ip, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, button_css, selected_data_index, face_detect, email_address
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
                "email address": [email_address[0]],
                "server auto start": [auto_start_server[0]],
                "host address": [ip[0]]
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
                auto_start_server.clear()
                ip.clear()
                settings_json = json.load(file)
                for info in settings_json:
                    for ind in info['selected data index']: selected_data_index.append(ind)
                    for dark in info['dark mode']: dark_mode.append(dark)
                    for face in info['face detect']: face_detect.append(face)
                    for color in info['saved color']: saved_color.append(color)
                    for video in info['record video']: record_video.append(video)
                    for smile in info['smiley face']: smiley_face.append(smile)
                    for email in info['email address']: email_address.append(email)
                    for screen in info['capture screen']: cap_screen.append(screen)
                    for email_b in info['send email']: send_email.append(email_b)
                    for email_d in info['email delay']: email_delay.append(email_d)
                    for picture in info['picture delay']: picture_delay.append(picture)
                    for autostart in info['server auto start']: auto_start_server.append(autostart)
                    for ipaddress in info['host address']: ip.append(ipaddress)
        button_css = 'background-color: rgb(' + str(saved_color[0]) + ', ' + str(saved_color[1]) + ', ' + str(saved_color[2]) + ');'
    def checkboxClicked(self, b, name, m):
        global auto_start_server, saved_color, ip, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, selected_data_index, face_detect, email_address
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
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
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
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
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
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
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
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == "Send Emails":
            if b.isChecked() == True:
                if not email_address[0] == '':
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
                        "email address": [email_address[0]],
                        "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
                    })
                    with open(settings_file, mode='w+', encoding='utf-8') as file:
                        json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
                if email_address[0] == '':
                    self.verifyEmailAddress('@gmail.com', False)
                    # self.sendEmails.setChecked(False)

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
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == "Smiley Face Addon":
            if b.isChecked() == True:
                if face_detect[0] == 'False' or not self.cascadeList.currentText() == 'frontalface alt tree' and not self.cascadeList.currentText() == 'frontalface default' and not self.cascadeList.currentIndex() == 'frontalface alt2' and not self.cascadeList.currentIndex() == 'profileface':
                    buttonReply = QMessageBox.question(self, "Enable 'face detection'", "You currently do not have 'face detection' enabled, if you want to get the best result, I would suggest you enable it.\nDo you want to enable 'face detection'?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    if buttonReply == QMessageBox.Yes:
                        for i, j in enumerate(cascade_files):
                            if j == 'haarcascade_frontalface_default.xml':
                                self.cascadeList.setCurrentIndex(i)
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
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
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
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == "Dark mode":
            if b.isChecked() == True:
                self.lightmode.setChecked(False)
                self.systemmode.setChecked(False)
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
                    "dark mode": ['1'],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                self.lightmode.setChecked(False)
                self.systemmode.setChecked(True)
                app.setPalette(QApplication.style().standardPalette())
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": ['0'],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == "Light mode":
            if b.isChecked() == True:
                self.darkmode.setChecked(False)
                self.systemmode.setChecked(False)
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
                    "dark mode": ['2'],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                self.darkmode.setChecked(False)
                self.systemmode.setChecked(True)
                app.setPalette(QApplication.style().standardPalette())
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": ['0'],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == "System mode":
            if b.isChecked() == True:
                self.darkmode.setChecked(False)
                self.lightmode.setChecked(False)
                app.setPalette(QApplication.style().standardPalette())
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": ['0'],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                self.darkmode.setChecked(False)
                self.lightmode.setChecked(False)
                self.systemmode.setChecked(True)
                app.setPalette(QApplication.style().standardPalette())
                settings_json.pop(0)
                settings_json.append({
                    "saved color": [saved_color[0], saved_color[1], saved_color[2]],
                    "capture screen": [cap_screen[0]],
                    "record video": [record_video[0]],
                    "smiley face": [smiley_face[0]],
                    "dark mode": ['0'],
                    "send email": [send_email[0]],
                    "email delay": [email_delay[0]],
                    "picture delay": [picture_delay[0]],
                    "selected data index": [selected_data_index[0]],
                    "face detect":[face_detect[0]],
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == "Face Detection":
            if b.isChecked() == True:
                self.motionDetection.setChecked(False)
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
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                self.motionDetection.setChecked(True)
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
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if name == 'Motion Detection':
            if b.isChecked() == True:
                self.faceDetection.setChecked(False)
                self.faceDetection.setChecked(False)
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
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                self.faceDetection.setChecked(True)
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
                    "email address": [email_address[0]],
                    "server auto start": [auto_start_server[0]],
                    "host address": [ip[0]]
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
            auto_start_server.clear()
            ip.clear()
            settings_json = json.load(file)
            for info in settings_json:
                for ind in info['selected data index']: selected_data_index.append(ind)
                for dark in info['dark mode']: dark_mode.append(dark)
                for face in info['face detect']: face_detect.append(face)
                for color in info['saved color']: saved_color.append(color)
                for video in info['record video']: record_video.append(video)
                for smile in info['smiley face']: smiley_face.append(smile)
                for email in info['email address']: email_address.append(email)
                for screen in info['capture screen']: cap_screen.append(screen)
                for email_b in info['send email']: send_email.append(email_b)
                for email_d in info['email delay']: email_delay.append(email_d)
                for picture in info['picture delay']: picture_delay.append(picture)
                for autostart in info['server auto start']: auto_start_server.append(autostart)
                for ipaddress in info['host address']: ip.append(ipaddress)
    def auto_start(self):
        global auto_start_server, ip, saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, selected_data_index, face_detect, email_address
        button = QMessageBox.information(self, "Attention", "You must restart the program for this effect to take place.\n\n Are you sure you want to continue?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if button == QMessageBox.Yes:        
            checked = str(self.autoStartServer.isChecked())
            checked = list(checked)
            checked[0] = checked[0].capitalize()
            checked = "".join(checked)
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
                "email address": [email_address[0]],
                "server auto start": [checked],
                "host address": [ip[0]]
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
                auto_start_server.clear()
                ip.clear()
                settings_json = json.load(file)
                for info in settings_json:
                    for ind in info['selected data index']: selected_data_index.append(ind)
                    for dark in info['dark mode']: dark_mode.append(dark)
                    for face in info['face detect']: face_detect.append(face)
                    for color in info['saved color']: saved_color.append(color)
                    for video in info['record video']: record_video.append(video)
                    for smile in info['smiley face']: smiley_face.append(smile)
                    for email in info['email address']: email_address.append(email)
                    for screen in info['capture screen']: cap_screen.append(screen)
                    for email_b in info['send email']: send_email.append(email_b)
                    for email_d in info['email delay']: email_delay.append(email_d)
                    for picture in info['picture delay']: picture_delay.append(picture)
                    for autostart in info['server auto start']: auto_start_server.append(autostart)
                    for ipaddress in info['host address']: ip.append(ipaddress)
        else:        
            self.autoStartServer.setChecked(True if auto_start_server[0] == 'True' else False)
            return
        exit_handler()
    def visitServer(self):
        a_website = "http://" + str(ip[0]) + ":5000"
        # Open url in a new window of the default browser, if possible
        webbrowser.open_new(a_website)
        # Open url in a new page (“tab”) of the default browser, if possible
        # webbrowser.open_new_tab(a_website)
        # webbrowser.open(a_website, 1) # Equivalent to: webbrowser.open_new(a_website)
        # webbrowser.open(a_website, 2) # Equivalent to: webbrowser.open_new_tab(a_website)
class Thread(QThread):
    try:
        changePixmap = pyqtSignal(QImage)
        def run(self):
            start_time = time.time()
            x = 1 # displays the frame rate every 1 second
            counter = 0
            n = 0
            while running:
                global outputFrame, ret, isTimeToSendEmail
                counter+=1
                try:
                    isTimeToSendEmail = camera.timeToSend
                    if running: ret, frame = camera.camRun()
                except:
                    n += 1
                    if n >= 2: exit_handler()
                if ret:
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    self.changePixmap.emit(convertToQtFormat)
                if (time.time() - start_time) > x :
                    global framesPerSecond
                    framesPerSecond = counter / (time.time() - start_time)
                    counter = 0
                    start_time = time.time()
                with lock:
                    outputFrame = frame.copy()
                    outputFrame = imutils.resize(outputFrame, width=360)
    except: unning = False
    finally: running = False
@appWeb.route("/")
def index():
	return render_template("index.html")
@appWeb.before_request
def before_request():
    g.request_time = lambda: datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
def generate():
    global outputFrame, lock, frame
    while running:
        with lock:
            if outputFrame is None: continue
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            if not flag: continue
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
@appWeb.route("/video_feed")
def video_feed():
        return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")
class CycleMenu(QMainWindow):
    def __init__(self, parent = None):
        super(CycleMenu, self).__init__(parent)
        global cycles, alwaysOn, OffFromList, OffToList, OnToList, OnFromList
        OffFromList.clear()
        OffToList.clear()
        OnFromList.clear()
        OnToList.clear()
        alwaysOn.clear()
        with open(cycles_file) as file:
            cycles_json = json.load(file)
            for info in cycles_json:
                for c in info['cycles']: cycles = int(c)
                for on in info['always on']: alwaysOn.append(on)
                for OnTo in info['OnTo']: OnToList.append(OnTo)
                for OnFrom in info['OnFrom']: OnFromList.append(OnFrom)
                for OffTo in info['OffTo']: OffToList.append(OffTo)
                for OffFrom in info['OffFrom']: OffFromList.append(OffFrom)
        regexp = QtCore.QRegExp('[a-z-A-Z-0-9-:_]{0,7}')
        self.validator = QtGui.QRegExpValidator(regexp)
        self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))
        mainlay = QWidget(self)
        mainlay.setContentsMargins(5, 5, 5, 5)
        self.currentTime = str(QTime.currentTime().toString(Qt.DefaultLocaleLongDate))
        self.grid = QGridLayout()
        self.grid.addWidget(self.lay(), 1, 0)
        mainlay.setLayout(self.grid)
        self.setCentralWidget(mainlay)  
    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None: idget.deleteLater()
                else: self.clearLayout(item.layout())
    def lay(self):
        global selected_data_index, cycles, all_textboxes, OnTo_textboxes, OnFrom_textboxes, OffTo_textboxes, OffFrom_textboxes
        self.scroll = QScrollArea(self)
        self.scroll.move(7, 80)
        self.scroll.setWidgetResizable(True)
        self.content = QWidget()
        self.scroll.setWidget(self.content)
        grid = QGridLayout(self.content)
        
        if isTimeToSendEmail: self.setWindowTitle(f'Cycle Menu - {cycles} - Cycles - Currenly is Active')
        else: self.setWindowTitle(f'Cycle Menu - {cycles} - Cycles - Currenly is not Active')
        
        self.radAlwaysOn = QCheckBox('Always on?')
        self.radAlwaysOn.clicked.connect(self.delete_save_saveCycles)
        self.radAlwaysOn.setChecked(True if alwaysOn[0] == 'True' else False)
        grid.addWidget(self.radAlwaysOn, 0, 0) 
        
        addCycle = QPushButton('&Add')
        addCycle.clicked.connect(self.btnAdd)
        
        btnSubmit = QPushButton('&Submit')
        btnSubmit.clicked.connect(self.save_cycles)
        btnSubmit.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogApplyButton')))
        btnSubmit.clicked.connect(self.submit)
        
        all_textboxes.clear()
        OnTo_textboxes.clear()
        OnFrom_textboxes.clear()
        OffTo_textboxes.clear()
        OffFrom_textboxes.clear()
        for i in range(cycles):
            subCycle = QPushButton('x')
            subCycle.clicked.connect(partial(self.delete_cycle, i))
            
            btnUp = QPushButton()
            btnUp.clicked.connect(partial(self.up_arrow, i))
            btnUp.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_ArrowUp')))
            
            btnDown = QPushButton()
            btnDown.clicked.connect(partial(self.down_arrow, i))
            btnDown.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_ArrowDown')))
            
            OnFrom = QLineEdit()
            OnTo = QLineEdit()
            OffFrom = QLineEdit()
            OffTo = QLineEdit()
            
            lblOnTo = QLabel(f'{i + 1}. On:')
            lblOnFrom = QLabel('to:')
            OnFrom.setValidator(self.validator)
            OnFrom.setText(str(OnFromList[i]))
            OnFrom.textChanged.connect(partial(self.save_cycles))
            OnTo.setValidator(self.validator)
            OnTo.setText(str(OnToList[i]))
            OnTo.textChanged.connect(partial(self.save_cycles))
        
            lblOffTo = QLabel('Off:')
            lblOffFrom = QLabel('to:')
            OffFrom.setValidator(self.validator)
            OffFrom.setText(str(OffFromList[i]))
            OffFrom.textChanged.connect(partial(self.save_cycles))
            OffTo.setValidator(self.validator)
            OffTo.setText(str(OffToList[i]))
            OffTo.textChanged.connect(partial(self.save_cycles))
            
            grid.addWidget(lblOnTo, i + 1, 0)
            grid.addWidget(lblOnFrom, i + 1, 2)
            grid.addWidget(OnTo, i + 1, 1)
            grid.addWidget(OnFrom, i + 1, 3)
            
            grid.addWidget(lblOffTo, i + 1, 4)
            grid.addWidget(lblOffFrom, i + 1, 6)
            grid.addWidget(OffTo, i + 1, 5)
            grid.addWidget(OffFrom, i + 1, 7)
            
            grid.addWidget(subCycle, i + 1, 8) 
            if not i == 0: grid.addWidget(btnUp, i + 1, 9) 
            if not i == cycles - 1: grid.addWidget(btnDown, i + 1, 10) 

            OnTo_textboxes.append(OnTo)
            OnFrom_textboxes.append(OnFrom)
            OffTo_textboxes.append(OffTo)
            OffFrom_textboxes.append(OffFrom)
            all_textboxes.append(OnTo)
            all_textboxes.append(OnFrom)
            all_textboxes.append(OffTo)
            all_textboxes.append(OffFrom)
        
        grid.addWidget(addCycle, cycles + 3, 8) 
        grid.addWidget(btnSubmit, cycles + 4, 8) 
        return self.scroll
    def up_arrow(self, key):
        global cycles, OffFromList, OffToList, OnFromList, onToList, OnTo_textboxes, OnFrom_textboxes, OffTo_textboxes, OffFrom_textboxes
        up = key - 1
        OffTo_textboxes[key], OffTo_textboxes[up] = OffTo_textboxes[up], OffTo_textboxes[key]
        OffFrom_textboxes[key], OffFrom_textboxes[up] = OffFrom_textboxes[up], OffFrom_textboxes[key]
        OnTo_textboxes[key], OnTo_textboxes[up] = OnTo_textboxes[up], OnTo_textboxes[key]
        OnFrom_textboxes[key], OnFrom_textboxes[up] = OnFrom_textboxes[up], OnFrom_textboxes[key]
        self.delete_save_saveCycles()
        self.clearLayout(self.grid)
        self.grid.addWidget(self.lay(), 1, 0)
    def down_arrow(self, key):
        global cycles, OffFromList, OffToList, OnFromList, onToList, OnTo_textboxes, OnFrom_textboxes, OffTo_textboxes, OffFrom_textboxes
        down = key + 1
        OffTo_textboxes[key], OffTo_textboxes[down] = OffTo_textboxes[down], OffTo_textboxes[key]
        OffFrom_textboxes[key], OffFrom_textboxes[down] = OffFrom_textboxes[down], OffFrom_textboxes[key]
        OnTo_textboxes[key], OnTo_textboxes[down] = OnTo_textboxes[down], OnTo_textboxes[key]
        OnFrom_textboxes[key], OnFrom_textboxes[down] = OnFrom_textboxes[down], OnFrom_textboxes[key]
        self.delete_save_saveCycles()
        self.clearLayout(self.grid)
        self.grid.addWidget(self.lay(), 1, 0)
    def save_cycles(self):
        global cycles, OffFromList, OffToList, OnFromList, onToList, cycles_json, all_textboxes
        for i, j in enumerate(all_textboxes):
            temp = j.text()
            temp = temp.replace(' ', '')
            temp = temp.lower()
            rx = re.compile(r"^((2[0-3]|[01][1-9]|10):([0-5][0-9]))$")
            if not rx.match(temp): return
        self.delete_save_saveCycles()
    def delete_cycle(self, key):
        global cycles, OnTo_textboxes, OnFrom_textboxes, OffTo_textboxes, OffFrom_textboxes
        cycles -= 1
        del OnTo_textboxes[key]
        del OnFrom_textboxes[key]
        del OffTo_textboxes[key]
        del OffFrom_textboxes[key]
        self.delete_save_saveCycles()
        self.clearLayout(self.grid)
        self.grid.addWidget(self.lay(), 1, 0)      
    def delete_save_saveCycles(self):
        global cycles, alwaysOn, OffFromList, OffToList, OnFromList, onToList, OnTo_textboxes, OnFrom_textboxes, OffTo_textboxes, OffFrom_textboxes
        OffFromList.clear()
        OffToList.clear()
        OnFromList.clear()
        OnToList.clear()
        # alwaysOn.clear()
        
        with open(cycles_file) as file:
            cycles_json = json.load(file)
        for i, j in enumerate(OnTo_textboxes):
            temp = j.text()
            temp = temp.replace(' ', '')
            temp = temp.upper()
            OnToList.append(temp)
        for i, j in enumerate(OnFrom_textboxes):
            temp = j.text()
            temp = temp.replace(' ', '')
            temp = temp.upper()
            OnFromList.append(temp)
        for i, j in enumerate(OffTo_textboxes):
            temp = j.text()
            temp = temp.replace(' ', '')
            temp = temp.upper()
            OffToList.append(temp)
        for i, j in enumerate(OffFrom_textboxes):
            temp = j.text()
            temp = temp.replace(' ', '')
            temp = temp.upper()
            OffFromList.append(temp)  
        cycles_json.pop(0)
        cycles_json.append({
            "cycles": [str(cycles)],
            "always on": [str(self.radAlwaysOn.isChecked())],
            "OnTo": OnToList,
            "OnFrom": OnFromList,
            "OffTo": OffToList,
            "OffFrom": OffFromList
        })
        with open(cycles_file, mode='w+', encoding='utf-8') as file:
            json.dump(cycles_json, file, ensure_ascii=True, indent=4)
        OffFromList.clear()
        OffToList.clear()
        OnFromList.clear()
        OnToList.clear()
        alwaysOn.clear()
        with open(cycles_file) as file:
            cycles_json = json.load(file)
            for info in cycles_json:
                for c in info['cycles']: cycles = int(c)
                for on in info['always on']: alwaysOn.append(on)
                for OnTo in info['OnTo']: nToList.append(OnTo)
                for OnFrom in info['OnFrom']: OnFromList.append(OnFrom)
                for OffTo in info['OffTo']: OffToList.append(OffTo)
                for OffFrom in info['OffFrom']: OffFromList.append(OffFrom)
    def btnAdd(self):
        global cycles, OffFromList, OffToList, OnFromList, cycles_json
        OffFromList.clear()
        OffToList.clear()
        OnFromList.clear()
        OnToList.clear()
        alwaysOn.clear()
        with open(cycles_file) as file:
            cycles_json = json.load(file)
            for info in cycles_json:
                for c in info['cycles']: cycles = int(c)
                for on in info['always on']: alwaysOn.append(on)
                for OnTo in info['OnTo']: OnToList.append(OnTo)
                for OnFrom in info['OnFrom']: OnFromList.append(OnFrom)
                for OffTo in info['OffTo']: OffToList.append(OffTo)
                for OffFrom in info['OffFrom']: OffFromList.append(OffFrom)
        cycles_json.pop(0)
        OnToList.append('00:00')
        OnFromList.append('00:00')
        OffToList.append('00:00')
        OffFromList.append('00:00')
        cycles +=1
        cycles_json.append({
            "cycles": [str(cycles)],
            "always on": [alwaysOn[0]],
            "OnTo": OnToList,
            "OnFrom": OnFromList,
            "OffTo": OffToList,
            "OffFrom": OffFromList
        })
        with open(cycles_file, mode='w+', encoding='utf-8') as file:
            json.dump(cycles_json, file, ensure_ascii=True, indent=4)
        OffFromList.clear()
        OffToList.clear()
        OnFromList.clear()
        OnToList.clear()
        alwaysOn.clear()
        with open(cycles_file) as file:
            cycles_json = json.load(file)
            for info in cycles_json:
                for c in info['cycles']: ycles = int(c)
                for on in info['always on']: alwaysOn.append(on)
                for OnTo in info['OnTo']: OnToList.append(OnTo)
                for OnFrom in info['OnFrom']: nFromList.append(OnFrom)
                for OffTo in info['OffTo']: OffToList.append(OffTo)
                for OffFrom in info['OffFrom']: OffFromList.append(OffFrom)
        self.clearLayout(self.grid)
        self.grid.addWidget(self.lay(), 1, 0)
    def submit(self):
        global cycles, OffFromList, OffToList, OnFromList, onToList, cycles_json, all_textboxes
        for i, j in enumerate(all_textboxes):
            temp = j.text()
            temp = temp.replace(' ', '')
            temp = temp.lower()
            rx = re.compile(r"^((2[0-3]|[01][1-9]|10):([0-5][0-9]))$")
            if not rx.match(j.text()):
                QMessageBox.warning(self, 'Format error!', f"Text box number: {i}\n\"{j.text()}\" is incorrect\n\nYou don't have the correct format!\n\nThe correct format should look like:\n02:57 or 23:01.", QMessageBox.Ok, QMessageBox.Ok)
                return
        self.delete_save_saveCycles()
        self.close()
def exit_handler():
    running = False
    camera.end_cam()
    camera.cap.release()
    cv2.destroyAllWindows()
    sys.exit()
def start_server():
    appWeb.run(host=str(ip[0]), port='5000', debug=True, threaded=True, use_reloader=False)
    threading.Thread(target=generate).start()
if __name__ == '__main__':
    atexit.register(exit_handler)
    if not os.path.exists('Pics'):
        os.mkdir('Pics')
    if not os.path.exists(cycles_file) or os.stat(settings_file).st_size == 0:
        file = open(cycles_file, "w+")
        file.write('''[{
        "cycles": [
            "5"
        ],
        "always on": [
            "False"
        ],
        "OnTo": [
            "01:01",
            "11:30",
            "15:05",
            "17:45",
            "20:15"
        ],
        "OnFrom": [
            "08:30",
            "12:55",
            "15:30",
            "19:30",
            "23:59"
        ],
        "OffTo": [
            "08:30",
            "12:55",
            "15:30",
            "19:30",
            "01:00"
        ],
        "OffFrom": [
            "11:30",
            "15:05",
            "17:45",
            "20:15",
            "01:01"
        ]
    }]''')
        file.close()
    with open(cycles_file) as file:
        cycles_json = json.load(file)
        for info in cycles_json:
            for c in info['cycles']: cycles = int(c)
            for on in info['always on']: alwaysOn.append(on)
            for OnTo in info['OnTo']: OnToList.append(OnTo)
            for OnFrom in info['OnFrom']: OnFromList.append(OnFrom)
            for OffTo in info['OffTo']: OffToList.append(OffTo)
            for OffFrom in info['OffFrom']: OffFromList.append(OffFrom)
    if not os.path.exists(settings_file) or os.stat(settings_file).st_size == 0:
        file = open(settings_file, "w+")
        file.write('''[{
        "saved color":["0", "0", "255"],
        "capture screen": ["False"],
        "record video": ["False"],
        "smiley face": ["False"],
        "dark mode": ["0"],
        "send email": ["False"],
        "email delay": ["50"],
        "picture delay": ["5"],
        "selected data index": ["7"],
        "face detect": ["True"],
        "email address": [""],
        "server auto start":["False"],
        "host address": ["''' + str(socket.gethostbyname(socket.gethostname())) + '''"]
    }]''')
        file.close()
    with open(settings_file) as file:
        settings_json = json.load(file)
        for info in settings_json:
            for ind in info['selected data index']: selected_data_index.append(ind)
            for dark in info['dark mode']: dark_mode.append(dark)
            for face in info['face detect']: face_detect.append(face)
            for color in info['saved color']: saved_color.append(color)
            for video in info['record video']: record_video.append(video)
            for smile in info['smiley face']: smiley_face.append(smile)
            for email in info['email address']: email_address.append(email)
            for screen in info['capture screen']: cap_screen.append(screen)
            for email_b in info['send email']: send_email.append(email_b)
            for email_d in info['email delay']: email_delay.append(email_d)
            for picture in info['picture delay']: picture_delay.append(picture)
            for autostart in info['server auto start']: auto_start_server.append(autostart)
            for ipaddress in info['host address']: ip.append(ipaddress)
    button_css = 'background-color: rgb(' + str(saved_color[0]) + ', ' + str(saved_color[1]) + ', ' + str(saved_color[2]) + ')'

    app = QApplication(sys.argv)
    if dark_mode[0] == '1':
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
    elif dark_mode[0] == '2':
        app.setStyle("Fusion")
        app.setPalette(QApplication.style().standardPalette())
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0.0, QColor(240, 240, 240))
        gradient.setColorAt(1.0, QColor(215, 215, 215))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setBrush(QPalette.Window, QBrush(gradient))
        app.setPalette(palette)
    if auto_start_server[0] == "True":
        threading.Thread(target=start_server).start()
    main = MainMenu()
    main.show()
    sys.exit(app.exec_())
