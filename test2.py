from PySide6.QtCore import QSize, QPointF, QRect
from PySide6.QtGui import QColorConstants, QPen, Qt, QBrush, QAction, QIcon
from PySide6.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsView, QPushButton
import math
import numpy as np


class Fil:
    def __init__(self, main_window, lignes):
        self.main_window = main_window
        self.lignes = lignes

    def enlever_lignes(self, index_max):
        for i in range(index_max):
            self.main_window.scene.removeItem(self.lignes[i])
        self.lignes = self.lignes[:index_max]


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test")
        self.scene_size = QSize(500, 500)
        self.scene = QGraphicsScene()
        self.graphics_view = GraphicsView(self.scene, self)
        self.setCentralWidget(self.graphics_view)
        self.graphics_view.setMinimumSize(self.scene_size)
        self.graphics_view.setScene(self.scene)

        self.largeur = self.scene_size.width()
        self.hauteur = self.scene_size.height()
        #La distance entre chaque ligne dans le grid
        self.taille_grid = 14

        self.mat_i0 = 0
        self.mat_j0 = 0
        self.dessiner_fond_grid()

        largeur_fil_base = 200
        hauteur_fil_base = 100
        fil_base, self.mat_points = self.dessiner_circuit_base(largeur_fil_base, hauteur_fil_base)

        self.debut_matrice_i = None
        self.debut_matrice_j = None

        self.dessine = False
        self.dernier_point = None

        sauvegarder = Sauvegarder(self)

        #Menubar
        barre_menu = self.menuBar()

        #sauvegarder
        sauvegarder = QAction("Sauvegarder")
        sauvegarder.setShortcut("Ctrl+S")
        sauvegarder.setIcon(QIcon("images/menubar/disquette.png"))
        barre_menu.addAction(sauvegarder)
        #sauvegarder.triggered.connect(sauvegarder)

        #rollback
        annuler_action = QAction("RollBack")
        annuler_action.setShortcut("Ctrl+R")
        #annuler_action.setIcon(QIcon("images/menubar/rollback.png"))
        barre_menu.addAction(annuler_action)

        #Quitter
        quitter = QAction("Quitter")
        quitter.setShortcut("Ctrl+Q")
        quitter.triggered.connect(self.close)
        barre_menu.addAction(quitter)



    def dessiner_fond_grid(self):
        self.scene.setBackgroundBrush(QColorConstants.White)
        self.scene.setSceneRect(0, 0, self.largeur, self.hauteur)

        largeur_crayon = 1

        pen = QPen()
        pen.setWidthF(largeur_crayon)
        pen.setColor(QColorConstants.Gray)

        #Lignes horizontales
        for i in range(math.ceil(self.hauteur/self.taille_grid) + 1):
            x1 = 0
            x2 = self.largeur
            y = i*self.taille_grid

            self.scene.addLine(x1, y, x2, y, pen)

        #Lignes verticales
        for i in range(math.ceil(self.largeur/self.taille_grid) + 1):
            y1 = 0
            y2 = self.hauteur
            x = i*self.taille_grid

            self.scene.addLine(x, y1, x, y2, pen)

    def ajouter_ligne(self, xi, yi, x, y):
        pen = QPen(QColorConstants.Black)
        largeur_crayon = 3
        pen.setWidthF(largeur_crayon)
        ligne = self.scene.addLine(xi, yi, x, y, pen)

        return ligne

    def dessiner_circuit_base(self, largeur_circuit, hauteur_circuit):
        gauche = self.largeur/2 - largeur_circuit/2
        droite = self.largeur/2 + largeur_circuit/2
        haut = self.hauteur/2 - hauteur_circuit/2
        bas = self.hauteur/2 + hauteur_circuit/2

        gauche, haut = self.pos_selon_grid(QPointF(gauche, haut))
        droite, bas = self.pos_selon_grid(QPointF(droite, bas))

        lignes_haut = []
        lignes_droite = []
        lignes_bas = []
        lignes_gauche = []

        nb_points_x = round((droite - gauche) / self.taille_grid) + 1
        nb_points_y = round((bas - haut) / self.taille_grid) + 1

        self.mat_i0 = haut
        self.mat_j0 = gauche
        matrice_points = np.zeros((nb_points_y, nb_points_x))

        # lignes verticales
        for i in range(nb_points_y - 1):
            yi = haut + i * self.taille_grid
            y = yi + self.taille_grid
            lignes_droite.append(self.ajouter_ligne(droite, yi, droite, y))

            mat_i, mat_j = self.pos_i_j(droite, y)
            matrice_points[mat_i, mat_j] = 1

            yi = bas - i * self.taille_grid
            y = yi - self.taille_grid
            lignes_gauche.append(self.ajouter_ligne(gauche, yi, gauche, y))

            mat_i, mat_j = self.pos_i_j(gauche, y)
            matrice_points[mat_i, mat_j] = 1

        # lignes horizontales
        for i in range(nb_points_x - 1):
            xi = gauche + i * self.taille_grid
            x = xi + self.taille_grid
            lignes_haut.append(self.ajouter_ligne(xi, haut, x, haut))

            mat_i, mat_j = self.pos_i_j(x, haut)
            matrice_points[mat_i, mat_j] = 1

            xi = droite - i * self.taille_grid
            x = xi - self.taille_grid
            lignes_bas.append(self.ajouter_ligne(xi, bas, x, bas))

            mat_i, mat_j = self.pos_i_j(x, bas)
            matrice_points[mat_i, mat_j] = 1

        lignes_fil = lignes_haut + lignes_droite + lignes_bas + lignes_gauche
        fil_base = Fil(self, lignes_fil)
        return fil_base, matrice_points

    def verifier_collision_fil(self, pos):
        x, y = self.pos_selon_grid(pos)
        mat_i, mat_j = self.pos_i_j(x, y)

        max_i = self.mat_points.shape[0] - 1
        max_j = self.mat_points.shape[1] - 1

        if mat_i <= max_i and mat_i >= 0 and mat_j <= max_j and mat_j >= 0:
            return round(self.mat_points[mat_i, mat_j])
        else:
            return 0

    def demarrer_ligne(self, pos):
        fil = self.verifier_collision_fil(pos)
        if fil != 0:
            self.dessine = True
            x, y = self.pos_selon_grid(pos)
            mat_i, mat_j = self.pos_i_j(x, y)

            #TODO débuter le dessin

    def pos_i_j(self, x, y):
        mat_i = round((y - self.mat_i0) / self.taille_grid)
        mat_j = round((x - self.mat_j0) / self.taille_grid)

        return mat_i, mat_j

    def pos_selon_grid(self, pos):
        x = round(pos.x() / self.taille_grid) * self.taille_grid
        x = max(min(x, math.floor(self.scene_size.width()/self.taille_grid)*self.taille_grid), 0)
        y = round(pos.y() / self.taille_grid) * self.taille_grid
        y = max(min(y, math.floor(self.scene_size.height()/self.taille_grid)*self.taille_grid), 0)

        return x, y


class GraphicsView(QGraphicsView):
    def __init__(self, scene, main_window):
        super().__init__(scene)
        self.main_window = main_window
        self.viewport().setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.main_window.demarrer_ligne(event.position())

    """
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.main_window.dessine:
            self.main_window.dessiner_fil(event.position())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.main_window.dessine:
            self.main_window.confirmer_fil()
            self.main_window.points = []
            self.main_window.lignes = []
    """

class Sauvegarder():
    def __init__(self, MainWindow):
        window = MainWindow
        mat_i = window.mat_i0
        mat_j = window.mat_j0
        self.liste_composantes = []
        self.infos_circuit = []


app = QApplication()
window = Window()
window.show()
app.exec()
