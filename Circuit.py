from PySide6.QtCore import QSize, QPoint
from PySide6.QtGui import QIcon, QPixmap, QColorConstants, QPainter, QPen, Qt
from PySide6.QtWidgets import QMainWindow, QToolBar, QWidget, QApplication, QPushButton, QVBoxLayout, QLabel, \
    QGraphicsPixmapItem, QGraphicsScene

from Dispositifs import toolbar_dispositifs


class Circuit(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Circuit")

        self.selection = None

        self.scene_size = QSize(500, 500)

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        for dispositif in toolbar_dispositifs:
            nom = dispositif.nom
            bouton = QPushButton()
            bouton.setIcon(QIcon(dispositif.image_toolbar))
            bouton.setIconSize(QSize(45, 45))
            toolbar.addWidget(bouton)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.scene = QLabel()
        self.layout.addWidget(self.scene)

        self.dessiner_fond()
        self.dessiner_circuit_base()

    def dessiner_fond(self):
        self.canevas = QPixmap(self.scene_size)
        self.canevas.fill(QColorConstants.White)
        self.scene.setPixmap(self.canevas)

    def dessiner_circuit_base(self):
        painter = QPainter(self.canevas)
        crayon = QPen()
        crayon.setWidth(5)
        crayon.setColor(QColorConstants.Black)
        painter.setPen(crayon)

        largeur = 300
        hauteur = 200

        hautgauche = QPoint(250 - round(largeur / 2), 250 - round(hauteur / 2))
        hautdroite = QPoint(250 + round(largeur / 2), 250 - round(hauteur / 2))
        basgauche = QPoint(250 - round(largeur / 2), 250 + round(hauteur / 2))
        basdroite = QPoint(250 + round(largeur / 2), 250 + round(hauteur / 2))

        painter.drawLine(hautgauche, hautdroite)
        painter.drawLine(hautdroite, basdroite)
        painter.drawLine(basdroite, basgauche)
        painter.drawLine(basgauche, hautgauche)

        # faire en sorte quon peut aller le chercher comme dans une bibliotheque (toolbar_dispositif["Batterie"])
        batterie_pixmap = QPixmap(toolbar_dispositifs[0].image_circuit)
        scaled_batterie_pixmap = batterie_pixmap.scaled(QSize(64, 64), aspectMode=Qt.AspectRatioMode.KeepAspectRatio)

        center_pix = QPoint(round(self.scene_size.width() / 2 - scaled_batterie_pixmap.width() / 2),
                            round(250 - round(hauteur / 2) - scaled_batterie_pixmap.height() / 2))

        painter.drawPixmap(center_pix, scaled_batterie_pixmap)

        painter.end()

        self.scene.setPixmap(self.canevas)


if __name__ == "__main__":
    app = QApplication()
    window = Circuit()
    window.show()
    app.exec()
