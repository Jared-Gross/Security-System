from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import *
import sys, os, shutil, json, multiprocessing, cv2, threading
from os import listdir
from os.path import isfile, join
# CAMERA SCRIPT
import live
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

email_delay = []
picture_delay = []
selected_data_index = []
button_css = ''

class MainMenu(QWidget):
    def __init__(self, parent = None):
        super(MainMenu, self).__init__(parent)
        self.setWindowTitle('Control Panel')
        self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogNoButton')))
        grid = QGridLayout()
        grid.addWidget(self.DelayGroup(), 0, 0)
        grid.addWidget(self.ComboBox(), 1, 0)
        grid.addWidget(self.CheckGroup(), 0, 1)
        grid.addWidget(self.Controll(), 1, 1)
        self.setLayout(grid)

        self.setMinimumSize(400, 260)
    def ComboBox(self):
        global selected_data_index
        groupBox = QGroupBox("Recognition type")

        self.cascadeList = QComboBox()
        for i, j in enumerate(cascade_files):
            j = j.replace('haarcascade_', '')
            j = j.replace('.xml', '')
            self.cascadeList.addItem(j)
        self.cascadeList.setCurrentIndex(int(selected_data_index[0]))
        self.cascadeList.currentTextChanged.connect(self.comboBoxChanged)
        vbox = QVBoxLayout()
        vbox.addWidget(self.cascadeList)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox
    def CheckGroup(self):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode
        groupBox = QGroupBox("Configuration")

        captureScreen = QCheckBox('Capture Screen')
        captureScreen.setChecked(True if cap_screen[0] == 'True' else False)
        captureScreen.toggled.connect(lambda:self.checkboxClicked(captureScreen))

        RecordVideo = QCheckBox('Record Video')
        RecordVideo.setChecked(True if record_video[0] == 'True' else False)
        RecordVideo.toggled.connect(lambda:self.checkboxClicked(RecordVideo))

        EmailPictures = QCheckBox('Send Emails')
        EmailPictures.setChecked(True if send_email[0] == 'True' else False)
        EmailPictures.toggled.connect(lambda:self.checkboxClicked(EmailPictures))

        SmileyFace = QCheckBox('Smiley Face Addon')
        SmileyFace.setChecked(True if smiley_face[0] == 'True' else False)
        SmileyFace.toggled.connect(lambda:self.checkboxClicked(SmileyFace))

        DarkTheme = QCheckBox('Dark mode')
        DarkTheme.setChecked(True if dark_mode[0] == 'True' else False)
        DarkTheme.toggled.connect(lambda:self.checkboxClicked(DarkTheme))

        vbox = QVBoxLayout()
        vbox.addWidget(captureScreen)
        vbox.addWidget(RecordVideo)
        vbox.addWidget(EmailPictures)
        vbox.addWidget(SmileyFace)
        vbox.addWidget(DarkTheme)
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
        Labe2 = QLabel('Snap Picture Delay:')
        self.ImageDelay = QLineEdit(str(picture_delay[0]))
        self.ImageDelay.setValidator(QIntValidator())
        self.ImageDelay.textChanged.connect(self.lineEditChanged)

        Labe3 = QLabel('Box Color:')

        self.ColorDialog = QPushButton('Color')
        self.ColorDialog.setStyleSheet(f"{button_css}")
        self.ColorDialog.clicked.connect(self.Open_Color_Dialog)

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
        self.start.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaPlay')))
        self.start.clicked.connect(self.startCamera)
        vbox = QVBoxLayout()
        vbox.addWidget(self.start)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox
    def comboBoxChanged(self):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, button_css, selected_data_index
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
            "selected data index": [int(self.cascadeList.currentIndex())]
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
    def lineEditChanged(self):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, selected_data_index

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
                "selected data index": [selected_data_index[0]]
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
    @pyqtSlot()
    def Open_Color_Dialog(self):
        # threading.Thread(target = self.openColorDialog).start()
        self.openColorDialog()
    def openColorDialog(self):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, button_css, selected_data_index
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
                "selected data index": [selected_data_index[0]]
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

        button_css = 'QPushButton {background-color: rgb(' + str(saved_color[0]) + ', ' + str(saved_color[1]) + ', ' + str(saved_color[2]) + ');}'
        self.ColorDialog.setStyleSheet(button_css)
    def checkboxClicked(self,b):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode, email_delay, picture_delay, saved_color, settings_json, selected_data_index
        if b.text() == "Capture Screen":
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
                    "selected data index": [selected_data_index[0]]
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
                    "selected data index": [selected_data_index[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if b.text() == "Record Video":
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
                    "selected data index": [selected_data_index[0]]
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
                    "selected data index": [selected_data_index[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if b.text() == "Send Emails":
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
                    "selected data index": [selected_data_index[0]]
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
                    "selected data index": [selected_data_index[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if b.text() == "Smiley Face Addon":
            if b.isChecked() == True:
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
                    "selected data index": [selected_data_index[0]]
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
                    "selected data index": [selected_data_index[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
        if b.text() == "Dark mode":
            if b.isChecked() == True:
                app.setStyle("Fusion")
                palette = QPalette()
                gradient = QLinearGradient(0, 0, 0, 400)
                gradient.setColorAt(0.0, QColor(40, 40, 40))
                gradient.setColorAt(1.0, QColor(30, 30, 30))
                palette.setBrush(QPalette.Window, QBrush(gradient))
                # palette.setColor(QPalette.Window, QColor(53, 53, 53))
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
                    "selected data index": [selected_data_index[0]]
                })
                with open(settings_file, mode='w+', encoding='utf-8') as file:
                    json.dump(settings_json, file, ensure_ascii=True, indent=4, sort_keys=False)
            else:
                app.setStyle("Fusion")
                app.setPalette(QApplication.style().standardPalette())
                palette = QPalette()
                gradient = QLinearGradient(0, 0, 0, 400)
                gradient.setColorAt(0.0, QColor(240, 240, 240))
                gradient.setColorAt(1.0, QColor(215, 215, 215))
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
                    "selected data index": [selected_data_index[0]]
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
    def startCamera(self):
        global isActive
        isActive = not isActive
        if not isActive:
            self.start.setText('Start')
            self.start.setStyleSheet('background-color: hsl(126, 81%, 29%)')
            self.start.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaPlay')))
            self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogNoButton')))
            # multiprocessing.Process(target=live.end_cam).start()
            # live.end_cam()linear-gradient(to right, black 0%, white 100%)
        else:
            self.start.setStyleSheet('background-color: rgb(106, 11, 11)')
            self.start.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaStop')))
            self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogYesButton')))
            self.start.setText('Stop')
            print('closed capture')
            cv2.destroyAllWindows()
            # live.start_cam()
            # multiprocessing.Process(target=live.start_cam).start()
        # print(isActive)
def getBool():
    print(isActive)
    return isActive
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
                    print(selected_data_index)
    elif not os.path.exists(settings_file):
        file = open(settings_file, "w+")
        file.write("""[
    {
        \"saved color\":[\"0\", \"255\", \"0\"],
        \"capture screen\": [\"False\"],
        \"record video\": [\"False\"],
        \"smiley face\": [\"False\"],
        \"dark mode\": [\"True\"],
        \"send email\": [\"True\"],
        \"email delay\": [\"10\"],
        \"picture delay\": [\"5\"],
        \"selected data index\": [\"7\"]
    }
]""")
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
    button_css = 'QPushButton {background-color: rgb(' + str(saved_color[0]) + ', ' + str(saved_color[1]) + ', ' + str(saved_color[2]) + ');}'
    
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
        palette.setBrush(QPalette.Window, QBrush(gradient))
        app.setPalette(palette)
    main = MainMenu()
    main.show()
    # START_CAMERA = multiprocessing.Process(target=MainMenu)
    sys.exit(app.exec_())
    # START_CAMERA.start()
