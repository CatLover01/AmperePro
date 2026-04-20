from PySide6.QtWidgets import QApplication, QToolTip, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFrame, \
    QGridLayout, QSizePolicy
from PySide6.QtCore import Qt, QTimer, QFile, QTextStream, QPoint
from PySide6.QtGui import QPixmap


class Popup(QWidget):
    def __init__(self, callback_commencer=None):
        super().__init__()
        # code de raf
        self.callback_commencer = callback_commencer

        style_poppup = QFile("StyleSheet/StylePoppup.qss")
        if style_poppup.open(QFile.OpenModeFlag.ReadOnly):
            stream = QTextStream(style_poppup)
            self.setStyleSheet(stream.readAll())
            style_poppup.close()

        self.setWindowFlag(Qt.WindowType.ToolTip)
        self.setFixedSize(400, 300)

        mainlayout = QGridLayout()
        self.setLayout(mainlayout)




        # desscription niveau
        description = QLabel("description simple du niveau")
        mainlayout.addWidget(description, 0, 0,0,2)

        #code de raf
        bouton_commencer = QPushButton("Commencer")
        bouton_commencer.clicked.connect(self.commencer)
        mainlayout.addWidget(bouton_commencer, 0,0,0,2)



        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

    def commencer(self):
        self.hide()
        if self.callback_commencer is not None:
            self.callback_commencer()


    def enterEvent(self, event):
        self.timer.stop()

    def leaveEvent(self, event):
        self.timer.start(100)


class OuvertureFenetre(QPushButton):
    def __init__(self, niveau, popup):
        super().__init__(niveau)
        self.popup = popup

    def enterEvent(self, event):
        pos = self.mapToGlobal(QPoint(250,20))
        #self.rect().bottomRight()
        self.popup.move(pos)
        self.popup.show()
        self.popup.timer.stop()

    def leaveEvent(self, event):
        self.popup.timer.start(100)
