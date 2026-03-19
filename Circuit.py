from enum import Enum
from PySide6.QtCore import QSize, QPoint, QPointF
from PySide6.QtGui import QIcon, QPixmap, QColorConstants, QPen, Qt, QPainterPath, QBrush, QColor
from PySide6.QtWidgets import QMainWindow, QToolBar, QWidget, QApplication, QPushButton, QVBoxLayout, QLabel, \
    QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QGraphicsPathItem, QGraphicsEllipseItem, QGraphicsLineItem

from Composantes import Type, Composante, ComposanteBase, Cote


class Noeud:
    def __init__(self):
        self.voltage = 0
        self.info_voisins = []

    def ajouter_info(self, serie, noeud_voisin):
        self.info_voisins.append([serie, noeud_voisin])


class Serie:
    def __init__(self, composantes, main_window):
        self.resistance, self.tension = self.calculs()
        self.coins = []
        self.main_window = main_window

        self.composantes = []
        for i in range(composantes):
            composantes[i].serie_parente = self
            self.composantes.append(composantes[i])
            cercle = CercleCliquable(self, main_window)
            self.composantes.append(cercle)

    def calculs(self):
        res = 0
        tension = 0
        for composante in self.composantes:
            if hasattr(composante, 'resistance'):
                res += composante.resistance
            if hasattr(composante, 'tension'):
                tension += composante.tension
        return res, tension

    def ajouter_noeud(self, cercle):
        if isinstance(cercle, CercleCliquable):
            index_point = self.composantes.index(cercle)
            nouveau_noeud = Noeud()
            self.composantes[index_point] = nouveau_noeud

            composantes_gauche = self.composantes[:index_point + 1]
            serie_gauche = Serie(composantes_gauche)
            composantes_gauche[0].info_voisins.remove([self, self.composantes[-1]])
            composantes_gauche[0].ajouter_info(serie_gauche, composantes_gauche[-1])

            self.composantes = self.composantes[index_point:]
            self.resistance, self.tension = self.calculs()

            nouveau_noeud.ajouter_info(serie_gauche, composantes_gauche[0])

            return nouveau_noeud

        # Si on a recu liste de deux cercles puisque c'est la serie de base sans noeud
        else:
            index_min = min(self.composantes.index(cercle[0]), self.composantes.index(cercle[1]))
            index_max = max(self.composantes.index(cercle[0]), self.composantes.index(cercle[1]))
            noeud_min = Noeud()
            noeud_max = Noeud()
            self.composantes[index_min] = noeud_min
            self.composantes[index_max] = noeud_max

            composantes_milieu = self.composantes[index_min:index_max + 1]
            serie_milieu = Serie(composantes_milieu, self.main_window)

            self.composantes = self.composantes[index_max:] + self.composantes[:index_min + 1]
            self.resistance, self.tension = self.calculs()

            nouvelle_serie = Serie([noeud_min, noeud_max], self.main_window)

            noeud_min.ajouter_info(self, noeud_max)
            noeud_min.ajouter_info(serie_milieu, noeud_max)
            noeud_min.ajouter_info(nouvelle_serie, noeud_max)

            noeud_max.ajouter_info(serie_milieu, noeud_min)
            noeud_max.ajouter_info(self, noeud_min)
            noeud_max.ajouter_info(nouvelle_serie, noeud_min)

            return [noeud_min, noeud_max]


class CercleCliquable(QGraphicsEllipseItem):
    def __init__(self, serie: "Serie", main_window: "Circuit"):
        super().__init__(0, 0, 0, 0)
        self.main_window = main_window
        self.diametre = 25
        self.setZValue(1)
        self.main_window.scene.addItem(self)
        self.serie_parente = serie

        self.setAcceptHoverEvents(True)

        crayon = QPen()
        crayon.setColor(QColorConstants.Black)
        crayon.setWidth(3)
        self.setPen(crayon)

        self.selectionne = False

        self.changer_couleur(QColorConstants.White)

    def changer_couleur(self, couleur):
        pinceau = QBrush(couleur)
        self.setBrush(pinceau)

    def mousePressEvent(self, event):
        self.main_window.bouton_cercle_click(self)

    def hoverEnterEvent(self, event):
        if not self.selectionne:
            self.changer_couleur(QColorConstants.Gray)

    def hoverLeaveEvent(self, event):
        if not self.selectionne:
            self.changer_couleur(QColorConstants.White)


class Circuit:
    def __init__(self):
        self.selection: ComposanteBase | None = None

        self.scene_size = QSize(500, 500)

        # Fenêtre de jeu
        self.scene = QGraphicsScene()

        self.circuit_fil = QGraphicsPathItem()

    def fil_click(self):
        if self.selection is None:
            self.dessiner_fond()
            # TODO Ajouter cercles
            self.dessiner_circuit()

        self.selection = "fil"

    # Appelée lorsque la main est appuyé, change la selection et enlève les cercles du circuit
    def main_click(self):
        if self.selection is not None:
            self.selection = None
            # TODO Retirer cercles
            self.dessiner_fond()
            self.dessiner_circuit()

    # Appelée lorsque une composante est appuyée dans la toolbar, change la sélection
    # et affiche les cercles si ce n'est pas déjà le cas
    def toolbar_clicked(self, dispositif: ComposanteBase):
        if self.selection is None:
            self.dessiner_fond()
            # TODO Afficher cercles
            self.dessiner_circuit()

        self.selection = dispositif

    # Dessine le fond de la scène et efface le path
    def dessiner_fond(self):
        self.circuit_fil.setPath(QPainterPath())
        self.scene.setBackgroundBrush(QColorConstants.White)
        self.scene.setSceneRect(0, 0, self.scene_size.width(), self.scene_size.height())

    # Trouve la longueur et hauteur du circuit pour dessiner le path
    # Change la position des composantes et cercles du circuit en respectant leur ordre et côté
    # Faudrait peut-être casser la méthode en plusieurs méthodes plus petites
    def dessiner_circuit(self):
        marge_element = 100
        marge_coins = 50
        epaisseur_fil = 4
        largeur_min = 200
        hauteur_min = 100

        centre_x = self.scene_size.width() / 2
        centre_y = self.scene_size.height() / 2

        self.scene.addItem(self.circuit_fil)
        path = QPainterPath()

        pen = QPen()
        pen.setColor(QColorConstants.Black)
        pen.setWidth(epaisseur_fil)
        self.circuit_fil.setPen(pen)

        nb_elements_cotes = {Cote.Haut: 0,
                             Cote.Droite: 0,
                             Cote.Bas: 0,
                             Cote.Gauche: 0}
        for element in self.elements:
            nb_elements_cotes[element.cote] += 1

        hauteur = marge_element * (
                max(nb_elements_cotes[Cote.Gauche], nb_elements_cotes[Cote.Droite]) - 1) + 2 * marge_coins
        largeur = marge_element * (max(nb_elements_cotes[Cote.Haut], nb_elements_cotes[Cote.Bas]) - 1) + 2 * marge_coins

        hauteur = max(hauteur, hauteur_min)
        largeur = max(largeur, largeur_min)

        def trouver_pos(cote, index):
            mult = -1
            angle = 0
            nombres = list(nb_elements_cotes.values())

            """
            for i in range(4):
                if nombres[i] > index:
                    break
                else:
                    index -= nombres[i]
                    angle += 90

            if cote == Cote.Haut or cote == Cote.Bas:
                if cote == Cote.Bas:
                    mult = 1
                pos = QPointF(
                    centre_x + mult * (nb_elements_cotes[cote] - 1) / 2 * marge_element - mult * index * marge_element,
                    centre_y + mult * hauteur / 2)
            else:
                if cote == Cote.Gauche:
                    mult = 1
                pos = QPointF(centre_x - mult * largeur / 2,
                              centre_y + mult * (nb_elements_cotes[
                                                     cote] - 1) / 2 * marge_element - mult * index * marge_element)

            return pos, angle

        for i in range(len(elements)):
            element = elements[i]

            position, angle = trouver_pos(element.cote, i)

            if not isinstance(element, CercleCliquable):
                self.placer_pixmap(element, position, angle)
            else:
                element.setPos(position)

        path.moveTo(QPointF(centre_x - largeur / 2, centre_y + hauteur / 2))
        path.lineTo(QPointF(centre_x + largeur / 2, centre_y + hauteur / 2))
        path.lineTo(QPointF(centre_x + largeur / 2, centre_y - hauteur / 2))
        path.lineTo(QPointF(centre_x - largeur / 2, centre_y - hauteur / 2))
        path.closeSubpath()

        self.circuit_fil.setPath(path)
        # on dessine les fils ajoutés et si on a modifié autre chose, on repositionne les fils
        self.dessiner_fils()
        """

    def placer_pixmap(self, element, pos, angle):
        item = element.item_instance
        largeur = item.pixmap().width() / 2
        hauteur = item.pixmap().height() / 2

        item.setPos(pos.x() - largeur, pos.y() - hauteur)

        pivot = QPointF(item.pixmap().width() / 2, item.pixmap().height() / 2)
        item.setTransformOriginPoint(pivot)
        item.setRotation(angle)

    def ajouter_fil(self, cercle_1, cercle_2):
        # on ajoute les coordonées des cercles qui doivent être reliés
        self.fils.append((cercle_1, cercle_2))

        # on déselectionne les cercles et on réinitialise fil_debute_cercle
        cercle_1.selectionne = False
        cercle_1.changer_couleur(QColorConstants.White)
        self.fil_debute_cercle = None

        # on redessine
        self.dessiner_fils()


    def dessiner_fils(self):
        rayon = self.diametre_cercle/2

        # on veut que les fils partent du milieu des cercles. On crée alors un sous path reliant les emplacements
        for cercle_1, cercle_2 in self.fils:
            position_1 = cercle_1.scenePos()
            position_2 = cercle_2.scenePos()
            chemin = QPainterPath()
            # on créer (moveTo) le sous path à 1 et on dessine jusqu'à 2
            chemin = QPainterPath()
            chemin.moveTo(position_1)
            chemin.lineTo(position_2)

            fil = QGraphicsPathItem(chemin)
            crayon = QPen()
            crayon.setColor(QColorConstants.Black)
            crayon.setWidth(4)
            fil.setPen(crayon)
            self.scene.addItem(fil)

    def bouton_cercle_click(self, cercle):
        if self.selection != "fil":
            cote = cercle.cote
            index_cercle = self.elements.index(cercle)
            new_composante = Composante(self.selection.type)
            self.scene.addItem(new_composante.ajouter_pixmap())
            new_composante.cote = cote

            self.elements[index_cercle] = new_composante
            self.scene.removeItem(cercle)

            element_suivant = self.elements[(index_cercle + 1) % len(self.elements)]
            if element_suivant.cote != new_composante.cote or not isinstance(element_suivant, CercleCliquable):
                self.elements.insert(index_cercle + 1, CercleCliquable(0, 0, self.diametre_cercle, self, cote))

            element_precedant = self.elements[index_cercle - 1]
            if element_precedant.cote != new_composante.cote or not isinstance(element_precedant, CercleCliquable):
                self.elements.insert(index_cercle, CercleCliquable(0, 0, self.diametre_cercle, self, cote))

            self.dessiner_fond()
            self.dessiner_circuit(self.elements)

        elif not self.fil_debute_cercle:
            cercle.changer_couleur(QColorConstants.Red)
            cercle.selectionne = True
            self.fil_debute_cercle = cercle

        else:
            self.ajouter_fil(self.fil_debute_cercle, cercle)


class LoisPhysiques:
    @staticmethod
    def loi_ohm(resistance, intensite):
        tension = resistance * intensite
        return tension

    @staticmethod
    def resistance_serie(*args):
        res_eq = 0
        for arg in args:
            res_eq += arg
        return res_eq

    @staticmethod
    def resistance_parallele(*args):
        res_eq_partielle = 0
        for arg in args:
            res_eq_partielle += 1 / arg

        return 1 / res_eq_partielle
