from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import *
import sys, os, shutil, json

class MainMenu(QWidget):
    def __init__(self, parent = None):
        super(MainMenu, self).__init__(parent)
        self.setWindowTitle('Control Panel')
        grid = QGridLayout()
        grid.addWidget(self.ComboBox(), 1, 0)
        grid.addWidget(self.CheckGroup(), 0, 1)
        grid.addWidget(self.DelayGroup(), 0, 0)
        # grid.addWidget(self.createExampleGroup(), 1, 1)
        self.setLayout(grid)

        self.setMinimumSize(400, 300)

    def ComboBox(self):
        groupBox = QGroupBox("Recognition type")

        cascadeList = QComboBox()

        vbox = QVBoxLayout()
        vbox.addWidget(cascadeList)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox
    def CheckGroup(self):
        groupBox = QGroupBox("Controlls")

        captureScreen = QCheckBox('Capture Screen')
        RecordVideo = QCheckBox('Record Video')
        EmailPictures = QCheckBox('Email')
        SmileyFace = QCheckBox('Smiley Face Addon')
        DarkTheme = QCheckBox('Dark mode')

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
        groupBox = QGroupBox("Delays")

        Label1 = QLabel('Email Sending Delay:')
        EmailDelay = QLineEdit('10')
        Labe2 = QLabel('Snap Picture Delay:')
        ImageDelay = QLineEdit('5')

        Labe3 = QLabel('Box Color:')
        ColorDialog = QPushButton('Color')
        ColorDialog.clicked.connect(self.Open_Color_Dialog)

        vbox = QVBoxLayout()
        vbox.addWidget(Label1)
        vbox.addWidget(EmailDelay)
        vbox.addWidget(Labe2)
        vbox.addWidget(ImageDelay)
        vbox.addWidget(Labe3)
        vbox.addWidget(ColorDialog)
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
if __name__ == '__main__':
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
    sys.exit(app.exec_())
