from PySide6.QtCore import QSize, QPoint, QPointF
from PySide6.QtGui import QIcon, QPixmap, QColorConstants, QPainter, QPen, Qt, QPainterPath, QBrush, QColor
from PySide6.QtWidgets import QMainWindow, QToolBar, QWidget, QApplication, QPushButton, QVBoxLayout, QLabel, \
    QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QGraphicsPathItem, QGraphicsEllipseItem

import Dispositifs
from Dispositifs import toolbar_dispositifs, LED


class Circuit(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Circuit")

        self.selection = None

        self.scene_size = QSize(500, 500)

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        icon_main = QIcon("images/toolbar/main.png")
        bouton_main = QPushButton()
        bouton_main.setIcon(icon_main)
        bouton_main.setIconSize(QSize(45, 45))
        bouton_main.clicked.connect(self.main_clicked)
        toolbar.addWidget(bouton_main)


        for dispositif in toolbar_dispositifs.values():
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

        batterie = toolbar_dispositifs['Batterie']

        batterie.item_instance = self.ajouter_pixmap(batterie)
        batterie.cote = "haut"

        self.diametre_cercle = 25
        self.elements = [batterie,
                         CercleCliquable(0, 0, self.diametre_cercle, self, "haut"),
                         CercleCliquable(0, 0, self.diametre_cercle, self, "droite"),
                         CercleCliquable(0, 0, self.diametre_cercle, self, "bas"),
                         CercleCliquable(0, 0, self.diametre_cercle, self, "gauche")]
        elements_sans_points = self.retire_cercles()

        self.circuit_fil = QGraphicsPathItem()
        self.dessiner_fond()
        self.dessiner_circuit(elements_sans_points)

    def retire_cercles(self):
        liste_clean = []
        for element in self.elements:
            if not isinstance(element, CercleCliquable):
                liste_clean.append(element)
            else:
                element.hide()
        return liste_clean

    def afficher_cercles(self):
        for element in self.elements:
            if isinstance(element, CercleCliquable):
                element.show()

    def main_clicked(self):
        if self.selection is not None:
            self.selection = None
            elements_sans_points = self.retire_cercles()
            self.dessiner_fond()
            self.dessiner_circuit(elements_sans_points)


    def toolbar_clicked(self, dispositif):
        if self.selection == None:
            self.afficher_cercles()
            self.dessiner_fond()
            self.dessiner_circuit(self.elements)

        self.selection = dispositif

    def dessiner_fond(self):
        self.circuit_fil.setPath(QPainterPath())
        self.scene.setBackgroundBrush(QColorConstants.White)
        self.scene.setSceneRect(0, 0, self.scene_size.width(), self.scene_size.height())

    def dessiner_circuit(self, elements):
        marge_element = 100
        marge_coins = 50
        milieu = QPointF(self.scene.width()/2, self.scene_size.height()/2)
        epaisseur_fil = 4
        largeur_min = 200
        hauteur_min = 100

        centre_x = self.scene_size.width()/2
        centre_y = self.scene_size.height()/2

        self.scene.addItem(self.circuit_fil)
        path = QPainterPath()

        pen = QPen()
        pen.setColor(QColorConstants.Black)
        pen.setWidth(epaisseur_fil)
        self.circuit_fil.setPen(pen)

        nb_elements_cotes = {"haut": 0,
                             "droite": 0,
                             "bas": 0,
                             "gauche": 0}
        for element in elements:
            nb_elements_cotes[element.cote] += 1

        hauteur = marge_element * (max(nb_elements_cotes["gauche"], nb_elements_cotes["droite"]) - 1) + 2 * marge_coins
        largeur = marge_element * (max(nb_elements_cotes["haut"], nb_elements_cotes["bas"]) - 1) + 2 * marge_coins

        hauteur = max(hauteur, hauteur_min)
        largeur = max(largeur, largeur_min)

        def trouver_pos(cote, index):
            mult = -1
            angle = 0
            nombres = list(nb_elements_cotes.values())
            for i in range(4):
                if nombres[i] > index:
                    break
                else:
                    index -= nombres[i]
                    angle += 90

            if cote == "haut" or cote == "bas":
                if cote == "bas":
                    mult = 1
                pos = QPointF(centre_x + mult * (nb_elements_cotes[cote]-1)/2 * marge_element - mult * index * marge_element,
                              centre_y + mult * hauteur/2)
            else:
                if cote == "gauche":
                    mult = 1
                pos = QPointF(centre_x - mult * largeur/2,
                              centre_y + mult * (nb_elements_cotes[cote]-1)/2 * marge_element - mult * index * marge_element)

            return pos, angle

        for i in range(len(elements)):
            element = elements[i]

            position, angle = trouver_pos(element.cote, i)

            if not isinstance(element, CercleCliquable):
                self.placer_pixmap(element, position, angle)
            else:
                element.setPos(position)

        path.moveTo(QPointF(centre_x - largeur/2, centre_y + hauteur/2))
        path.lineTo(QPointF(centre_x + largeur/2, centre_y + hauteur/2))
        path.lineTo(QPointF(centre_x + largeur/2, centre_y - hauteur/2))
        path.lineTo(QPointF(centre_x - largeur/2, centre_x - hauteur/2))
        path.closeSubpath()

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

        pixmap_item = Dispositifs.Item(element)
        pixmap_item.setPixmap(pixmap_scaled)

        pixmap_item.setZValue(1)

        self.scene.addItem(pixmap_item)

        return pixmap_item

    def bouton_cercle_click(self, cercle):
        if self.selection is not None:
            cote = cercle.cote
            index_cercle = self.elements.index(cercle)
            element = self.selection
            self.elements[index_cercle] = element
            self.scene.removeItem(cercle)

            element.item_instance = self.ajouter_pixmap(element)
            element.cote = cote

            element_suivant = self.elements[(index_cercle + 1) % len(self.elements)]
            if element_suivant.cote != element.cote or not isinstance(element_suivant, CercleCliquable):
                self.elements.insert(index_cercle + 1, CercleCliquable(0, 0, self.diametre_cercle, self, cote))

            element_precedant = self.elements[index_cercle - 1]
            if element_precedant.cote != element.cote or not isinstance(element_precedant, CercleCliquable):
                self.elements.insert(index_cercle, CercleCliquable(0, 0, self.diametre_cercle, self, cote))


            self.dessiner_fond()
            self.dessiner_circuit(self.elements)


class CercleCliquable(QGraphicsEllipseItem):
    def __init__(self, x, y, diametre, main_window, cote):
        super().__init__(x - diametre/2, y - diametre/2, diametre, diametre)
        self.main_window = main_window
        self.diametre = diametre
        self.setZValue(1)
        self.main_window.scene.addItem(self)

        self.setAcceptHoverEvents(True)
        self.cote = cote

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
