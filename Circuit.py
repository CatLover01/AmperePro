import math

from PySide6.QtCore import QSize, QPoint, QPointF
from PySide6.QtGui import QIcon, QPixmap, QColorConstants, QPainter, QPen, Qt, QPainterPath, QBrush, QColor
from PySide6.QtWidgets import QMainWindow, QToolBar, QWidget, QApplication, QPushButton, QVBoxLayout, QLabel, \
    QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QGraphicsPathItem, QGraphicsEllipseItem

from Dispositifs import toolbar_dispositifs, LED


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

        batterie = toolbar_dispositifs['Batterie'].__class__()

        batterie.item_instance = self.ajouter_pixmap(batterie)

        self.diametre_cercle = 25
        self.elements = [batterie,
                         CercleCliquable(0, 0, self.diametre_cercle, self)]

        self.circuit_fil = QGraphicsPathItem()
        self.dessiner_fond()
        self.dessiner_circuit()

    def toolbar_clicked(self, dispositif):
        self.selection = dispositif

    def dessiner_fond(self):
        self.circuit_fil.setPath(QPainterPath())
        self.scene.setBackgroundBrush(QColorConstants.White)
        self.scene.setSceneRect(0, 0, self.scene_size.width(), self.scene_size.height())

    def dessiner_circuit(self):
        marge_element = 100
        marge_coins = 50
        milieu = QPointF(self.scene.width()/2, self.scene_size.height()/2)
        epaisseur_fil = 4
        largeur_min = 200
        hauteur_min = 100

        self.scene.addItem(self.circuit_fil)
        path = QPainterPath()

        pen = QPen()
        pen.setColor(QColorConstants.Black)
        pen.setWidth(epaisseur_fil)
        self.circuit_fil.setPen(pen)

        total = len(self.elements)

        def nombre_elements_cote(min_ajout):
            nombre_elements = math.floor(total / 4)
            reste = total % 4
            if reste >= min_ajout:
                nombre_elements += 1

            return nombre_elements

        haut = nombre_elements_cote(2)
        droite = nombre_elements_cote(3)
        bas = nombre_elements_cote(1)
        gauche = nombre_elements_cote(4)

        largeur = (bas - 1) * marge_element + 2 * marge_coins
        if largeur < largeur_min:
            largeur = largeur_min
        hauteur = (droite - 1) * marge_element + 2 * marge_coins
        if hauteur < hauteur_min:
            hauteur = hauteur_min

        path.moveTo(milieu.x() - largeur/2, milieu.y() - hauteur/2)
        path.lineTo(milieu.x() + largeur/2, milieu.y() - hauteur/2)
        path.lineTo(milieu.x() + largeur/2, milieu.y() + hauteur/2)
        path.lineTo(milieu.x() - largeur/2, milieu.y() + hauteur/2)
        path.lineTo(milieu.x() - largeur/2, milieu.y() - hauteur/2)

        for i in range(haut):
            position = QPointF(milieu.x() - haut/2 * marge_element + i * marge_element + marge_coins,
                               milieu.y() - hauteur/2)

            element = self.elements[i]
            if isinstance(element, CercleCliquable):
                element.setPos(position)
            else:
                self.placer_pixmap(element, position, 0)

        for i in range(droite):
            position = QPointF(milieu.x() + largeur/2,
                               milieu.y() - droite/2 * marge_element + i * marge_element + marge_coins)

            element = self.elements[i + haut]
            if isinstance(element, CercleCliquable):
                element.setPos(position)
            else:
                self.placer_pixmap(element, position, 90)

        for i in range(bas):
            position = QPointF(milieu.x() + bas/2 * marge_element - i * marge_element - marge_coins,
                               milieu.y() + hauteur/2)

            element = self.elements[i + haut + droite]
            if isinstance(element, CercleCliquable):
                element.setPos(position)
            else:
                self.placer_pixmap(element, position, 180)

        for i in range(gauche):
            position = QPointF(milieu.x() - largeur / 2,
                               milieu.y() + gauche / 2 * marge_element - i * marge_element - marge_coins)

            element = self.elements[i + haut + droite + bas]
            if isinstance(element, CercleCliquable):
                element.setPos(position)
            else:
                self.placer_pixmap(element, position, 270)

        self.circuit_fil.setPath(path)

    def placer_pixmap(self, element, pos, angle):
        item = element.item_instance
        largeur = item.pixmap().width() / 2
        hauteur = item.pixmap().height() / 2

        item.setPos(pos.x() - largeur, pos.y() - hauteur)

        if element.rotate:
            pivot = QPointF(item.pixmap().width() / 2, item.pixmap().height() / 2)
            item.setTransformOriginPoint(pivot)
            item.setRotation(angle)

    def ajouter_pixmap(self, element):
        pixmap = QPixmap(element.image_circuit)
        pixmap_scaled = pixmap.scaled(element.scale, element.scale, Qt.AspectRatioMode.KeepAspectRatio)

        pixmap_item = QGraphicsPixmapItem(pixmap_scaled)
        pixmap_item.setPixmap(pixmap_scaled)

        pixmap_item.setZValue(1)

        self.scene.addItem(pixmap_item)

        return pixmap_item

    def bouton_cercle_click(self, cercle):
        if self.selection is not None:
            index_cercle = self.elements.index(cercle)
            element = self.selection.__class__()
            self.elements[index_cercle] = element
            self.scene.removeItem(cercle)

            element.item_instance = self.ajouter_pixmap(element)

            if not isinstance(self.elements[(index_cercle + 1) % len(self.elements)], CercleCliquable):
                self.elements.insert(index_cercle + 1, CercleCliquable(0, 0, self.diametre_cercle, self))

            if not isinstance(self.elements[index_cercle - 1], CercleCliquable):
                self.elements.insert(index_cercle, CercleCliquable(0, 0, self.diametre_cercle, self))

            self.dessiner_fond()
            self.dessiner_circuit()


class CercleCliquable(QGraphicsEllipseItem):
    def __init__(self, x, y, diametre, main_window):
        super().__init__(x - diametre/2, y - diametre/2, diametre, diametre)
        self.main_window = main_window
        self.diametre = diametre
        self.setZValue(1)
        self.main_window.scene.addItem(self)

        self.setAcceptHoverEvents(True)

        crayon = QPen()
        crayon.setColor(QColorConstants.Black)
        crayon.setWidth(3)
        self.setPen(crayon)

        pinceau = QBrush(QColorConstants.White)
        self.setBrush(pinceau)

    def mousePressEvent(self, event):
        self.main_window.bouton_cercle_click(self)

    def hoverEnterEvent(self, event):
        pinceau = QBrush(QColorConstants.Gray)
        self.setBrush(pinceau)

    def hoverLeaveEvent(self, event):
        pinceau = QBrush(QColorConstants.White)
        self.setBrush(pinceau)


if __name__ == "__main__":
    app = QApplication()
    window = Circuit()
    window.show()
    app.exec()
