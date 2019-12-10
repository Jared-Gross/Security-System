from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import *
import sys, os, shutil, json, multiprocessing
settings_file = os.path.dirname(os.path.realpath(__file__)) + '/settings.json'
settings_json = []

saved_color = []
send_email = []
cap_screen = []
record_video = []
smiley_face = []
dark_mode = []

email_delay = []
picture_delay = []
class MainMenu(QWidget):
    def __init__(self, parent = None):
        super(MainMenu, self).__init__(parent)
        self.setWindowTitle('Control Panel')
        grid = QGridLayout()
        grid.addWidget(self.DelayGroup(), 0, 0)
        grid.addWidget(self.ComboBox(), 1, 0)
        grid.addWidget(self.CheckGroup(), 0, 1)
        grid.addWidget(self.Controll(), 1, 1)
        self.setLayout(grid)

        self.setMinimumSize(400, 270)

    def ComboBox(self):
        groupBox = QGroupBox("Recognition type")

        cascadeList = QComboBox()

        vbox = QVBoxLayout()
        vbox.addWidget(cascadeList)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox
    def CheckGroup(self):
        global saved_color, send_email, cap_screen, record_video, smiley_face, dark_mode
        groupBox = QGroupBox("Controlls")

        captureScreen = QCheckBox('Capture Screen')
        captureScreen.setChecked(True if cap_screen[0] == 'True' else False)
        captureScreen.toggled.connect(lambda:self.checkboxClicked(captureScreen))

        RecordVideo = QCheckBox('Record Video')
        RecordVideo.setChecked(True if record_video[0] == 'True' else False)
        RecordVideo.toggled.connect(lambda:self.checkboxClicked(RecordVideo))

        EmailPictures = QCheckBox('Email')
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
        EmailDelay = QLineEdit(email_delay[0])
        Labe2 = QLabel('Snap Picture Delay:')
        ImageDelay = QLineEdit(picture_delay[0])

        Labe3 = QLabel('Box Color:')

        button_css = 'QPushButton {background-color: rgb(' + saved_color[0] + ', ' + saved_color[1] + ', ' + saved_color[2] + ');}'
        self.ColorDialog = QPushButton('Color')
        self.ColorDialog.setStyleSheet(f"{button_css}")
        self.ColorDialog.clicked.connect(self.Open_Color_Dialog)

        vbox = QVBoxLayout()
        vbox.addWidget(Label1)
        vbox.addWidget(EmailDelay)
        vbox.addWidget(Labe2)
        vbox.addWidget(ImageDelay)
        vbox.addWidget(Labe3)
        vbox.addWidget(self.ColorDialog)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox
    def Controll(self):
        groupBox = QGroupBox("Start")

        button = QPushButton('Start')

        vbox = QVBoxLayout()
        vbox.addWidget(button)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox
    @pyqtSlot()
    def Open_Color_Dialog(self):
        self.openColorDialog()

    def openColorDialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            print(color.red())
            print(color.green())
            print(color.blue())
    def checkboxClicked(self,b):
        if b.text() == "Capture Screen":
            if b.isChecked() == True:
                print (b.text()+" is selected")
            else:
                print( b.text()+" is deselected")
        if b.text() == "Record Video":
            if b.isChecked() == True:
                print( b.text()+" is selected")
            else:
                print( b.text()+" is deselected")
        if b.text() == "Email":
            if b.isChecked() == True:
                print( b.text()+" is selected")
            else:
                print( b.text()+" is deselected")
        if b.text() == "Smiley Face Addon":
            if b.isChecked() == True:
                print( b.text()+" is selected")
            else:
                print( b.text()+" is deselected")
        if b.text() == "Dark mode":
            if b.isChecked() == True:
                print( b.text()+" is selected")
            else:
                print( b.text()+" is deselected")
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
        \"picture delay\": [\"5\"]
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
                    record_video.append(email)
                for smile in info['smiley face']:
                    smiley_face.append(smile)
                for dark in info['dark mode']:
                    dark_mode.append(dark)
                for send_email in info['email delay']:
                    email_delay.append(email)
                for picture in info['picture delay']:
                    picture_delay.append(picture)

    app = QApplication(sys.argv)
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
    main = MainMenu()
    main.show()
    START_CAMERA = multiprocessing.Process(target=MainMenu).start()
    sys.exit(app.exec_())
