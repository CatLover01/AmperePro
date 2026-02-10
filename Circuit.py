from PySide6.QtCore import QSize, QPoint, QPointF
from PySide6.QtGui import QIcon, QPixmap, QColorConstants, QPainter, QPen, Qt, QPainterPath, QBrush
from PySide6.QtWidgets import QMainWindow, QToolBar, QWidget, QApplication, QPushButton, QVBoxLayout, QLabel, \
    QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QGraphicsPathItem, QGraphicsEllipseItem

from Dispositifs import toolbar_dispositifs


class Circuit(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Circuit")

        self.selection = None

        self.scene_size = QSize(500, 500)

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        for dispositif in toolbar_dispositifs.values():
            nom = dispositif.nom
            bouton = QPushButton()
            bouton.setIcon(QIcon(dispositif.image_toolbar))
            bouton.setIconSize(QSize(45, 45))

            bouton.clicked.connect(lambda _, x=dispositif: self.toolbar_clicked(x))

            toolbar.addWidget(bouton)

        # Fenetre de jeu
        self.vue = QGraphicsView()
        self.scene = QGraphicsScene()
        self.vue.setScene(self.scene)
        self.setCentralWidget(self.vue)

        self.dessiner_fond()
        self.dessiner_circuit_base()

    def toolbar_clicked(self, dispositif):
        self.selection = dispositif

    def dessiner_fond(self):
        self.scene.setBackgroundBrush(QColorConstants.White)
        self.scene.setSceneRect(0, 0, self.scene_size.width(), self.scene_size.height())

    def dessiner_circuit_base(self):
        center_x = self.scene.width() / 2
        center_y = self.scene.height() / 2

        largeur = 400
        hauteur = 200

        circuit_fil = QGraphicsPathItem()
        self.scene.addItem(circuit_fil)

        pen = QPen()
        pen.setColor(QColorConstants.Black)
        pen.setWidth(2)
        circuit_fil.setPen(pen)

        path = QPainterPath()

        def trouver_point(x, y):
            return QPointF(center_x + x * largeur / 2, center_y + y * hauteur / 2)

        #Prépare le path en haut à gauche
        path.moveTo(trouver_point(-1, -1))

        path.lineTo(trouver_point(1, -1))
        path.lineTo(trouver_point(1, 1))
        path.lineTo(trouver_point(-1, 1))
        path.lineTo(trouver_point(-1, -1))

        path.closeSubpath()

        circuit_fil.setPath(path)

        batterie = toolbar_dispositifs["Batterie"]
        self.ajouter_img_circuit(batterie.image_circuit, center_x, center_y - hauteur / 2, batterie.scale)

        pen = QPen()
        pen.setColor(QColorConstants.Black)
        pen.setWidth(4)
        brush = QBrush()
        brush.setColor(QColorConstants.White)
        brush.setStyle(Qt.SolidPattern)

        diametre = 25
        
        circle = CercleCliquable(center_x, center_y + hauteur/2, diametre, self)
        circle.setPen(pen)
        circle.setBrush(brush)

        self.scene.addItem(circle)

    def ajouter_img_circuit(self, image, pos_x, pos_y, scale):

        pixmap = QPixmap(image)
        pixmap_scaled = pixmap.scaled(scale, scale, Qt.AspectRatioMode.KeepAspectRatio)

        pixmap_item = QGraphicsPixmapItem(pixmap_scaled)
        pixmap_item.setPos(QPointF(pos_x - pixmap_scaled.width()/2, pos_y - pixmap_scaled.height()/2))

        self.scene.addItem(pixmap_item)

    def bouton_cercle_click(self, cercle):
        if self.selection is not None:
            self.scene.removeItem(cercle)
            self.ajouter_img_circuit(self.selection.image_circuit, cercle.x, cercle.y, self.selection.scale)


class CercleCliquable(QGraphicsEllipseItem):
    def __init__(self, x, y, diametre, main_window):
        super().__init__(x - diametre/2, y - diametre/2, diametre, diametre)
        self.main_window = main_window
        self.x = x
        self.y = y

    def mousePressEvent(self, event):
        self.main_window.bouton_cercle_click(self)


if __name__ == "__main__":
    app = QApplication()
    window = Circuit()
    window.show()
    app.exec()
