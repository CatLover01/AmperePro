from PySide6.QtWidgets import QApplication, QToolTip, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFrame, \
    QGridLayout, QSizePolicy
from PySide6.QtCore import Qt, QTimer, QFile, QTextStream, QPoint
from PySide6.QtGui import QPixmap


class Popup(QWidget):
    def __init__(self):
        super().__init__()

        style_poppup = QFile("StyleSheet/StylePoppup.qss")
        if style_poppup.open(QFile.OpenModeFlag.ReadOnly):
            stream = QTextStream(style_poppup)
            self.setStyleSheet(stream.readAll())
            style_poppup.close()

        self.setWindowFlag(Qt.ToolTip)
        self.setFixedSize(400, 300)

        mainlayout = QGridLayout()
        self.setLayout(mainlayout)

        # apercu niveau
        image_niveau = QLabel(pixmap=QPixmap("images/Interface/AmperePro_logo.png"))  #changer la photo
        image_niveau.setFixedSize(300, 150)
        mainlayout.addWidget(image_niveau, 0, 0)

        # desscription niveau
        description = QLabel("description simple du niveau")
        mainlayout.addWidget(description, 0, 1)



        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

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
