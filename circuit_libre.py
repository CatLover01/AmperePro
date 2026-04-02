import sys

from PySide6.QtCore import QSize, QPointF, QRect, QFile, QTextStream, QLineF
from PySide6.QtGui import QColorConstants, QPen, Qt, QBrush, QAction, QIcon
from PySide6.QtWidgets import (QMainWindow, QApplication, QGraphicsScene, QGraphicsView, QPushButton, QDialog,
                               QHBoxLayout)
import math
import numpy as np
import datetime

from a_propos import AProposWindow
from docs import DocumentationWindow
from sauvegarder import Sauvegarder, CircuitLibre


class Fil:
    def __init__(self, main_window, lignes):
        self.main_window = main_window
        self.lignes = lignes

    def enlever_lignes(self, index_max):
        for i in range(index_max):
            self.main_window.scene.removeItem(self.lignes[i])
        self.lignes = self.lignes[:index_max]


class Window(QGraphicsScene):
    def __init__(self, mainwindow):
        super().__init__()
        self.main_window = mainwindow
        self.scene_size = QSize(500, 500)
        self.graphics_view = GraphicsView(self, self.main_window)
        self.main_window.setCentralWidget(self.graphics_view)
        self.graphics_view.setMinimumSize(self.scene_size)
        self.graphics_view.setScene(self)

        self.fenetre_doc = DocumentationWindow()
        self.fenetre_a_propos = AProposWindow()

        self.largeur = self.scene_size.width()
        self.hauteur = self.scene_size.height()
        # La distance entre chaque ligne dans le grid
        self.taille_grid = 20

        self.mat_i0 = 0
        self.mat_j0 = 0
        self.dessiner_fond_grid()

        largeur_fil_base = 200
        hauteur_fil_base = 100

        self.debut_matrice_i = None
        self.debut_matrice_j = None

        self.dessine = False
        self.dernier_point = None

        self.lignes = []
        self.points_apres_pivot = []
        self.points_avant_pivot = []
        self.fil_touche = None
        self.fil_complet = False

        self.save = Sauvegarder()

        fil_base, self.mat_points = self.dessiner_circuit_base(largeur_fil_base, hauteur_fil_base)
        self.fils = [fil_base]

        #Menubar
        self.barre_menu = self.main_window.menuBar()
        self.menu_options = self.barre_menu.addMenu("Options")
        self.menu_naviguer = self.barre_menu.addMenu("Naviguer")

        #sauvegarder
        sauvegarder_action = QAction("Sauvegarder", self)
        sauvegarder_action.setShortcut("Ctrl+S")
        sauvegarder_action.setIcon(QIcon("images/menubar/disquette.png"))
        self.menu_options.addAction(sauvegarder_action)
        sauvegarder_action.triggered.connect(self.sauvegarder_triggered)

        #rollback
        annuler_action = QAction("RollBack", self)
        annuler_action.setShortcut("Ctrl+R")
        annuler_action.setIcon(QIcon("images/menubar/rollback.png"))
        self.menu_options.addAction(annuler_action)

        #Quitter
        quitter_action = QAction("Quitter", self)
        quitter_action.setShortcut("Ctrl+Q")
        quitter_action.triggered.connect(self.quitter_triggered)
        self.menu_naviguer.addAction(quitter_action)


    def sauvegarder_triggered(self):
        # Id: Devrait être générer automatiquement lors de louverture du graphique
        # Nom: Devrait être rentrer par l'utilisateur
        date = int(datetime.datetime.now(datetime.UTC).timestamp())
        circuit = CircuitLibre("Id", "Nom...", self.mat_points.tolist(), date)
        self.save.ajout_circuit_libre(circuit)

    def quitter_triggered(self):
        avertissement = QDialog()
        avertissement.setWindowTitle("Voulez-vous Sauvegarder?")
        avertissement.setModal(True)

        layout_dialogue = QHBoxLayout()
        avertissement.setLayout(layout_dialogue)

        #comme si on avait jamais souhaité quitter
        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(avertissement.close)

        bouton_sauvegarder_et_quitter_total = QPushButton("Sauvegarder et Quitter")
        bouton_sauvegarder_et_quitter_total.clicked.connect(lambda: self.sauvegarder_et_quitter(avertissement))

        #ferme les deux fenêtres (dialogue et principale)
        bouton_quitter_sans_sauvegarder = QPushButton("quitter sans sauvegarder")
        bouton_quitter_sans_sauvegarder.clicked.connect(avertissement.close)
        bouton_quitter_sans_sauvegarder.clicked.connect(self.main_window.close)
        layout_dialogue.addWidget(bouton_sauvegarder_et_quitter_total)
        layout_dialogue.addWidget(bouton_quitter_sans_sauvegarder)
        layout_dialogue.addWidget(bouton_annuler)
        avertissement.exec()

    def sauvegarder_et_quitter(self, dialog):
        # sauvegarde le circuit et ferme tout
        dialog.close()
        self.sauvegarder_triggered()
        self.main_window.close()

    # première méthode non liée au menu à propos
    def dessiner_fond_grid(self):
        self.setBackgroundBrush(QColorConstants.White)
        self.setSceneRect(0, 0, self.largeur, self.hauteur)

        largeur_crayon = 1

        pen = QPen()
        pen.setWidthF(largeur_crayon)
        pen.setColor(QColorConstants.Gray)

        # Lignes horizontales
        for i in range(math.ceil(self.hauteur / self.taille_grid) + 1):
            x1 = 0
            x2 = self.largeur
            y = i * self.taille_grid

            self.addLine(x1, y, x2, y, pen)

        # Lignes verticales
        for i in range(math.ceil(self.largeur / self.taille_grid) + 1):
            y1 = 0
            y2 = self.hauteur
            x = i * self.taille_grid

            self.addLine(x, y1, x, y2, pen)

    def ajouter_ligne(self, xi, yi, x, y):
        pen = QPen(QColorConstants.Black)
        largeur_crayon = 3
        pen.setWidthF(largeur_crayon)
        ligne = self.addLine(xi, yi, x, y, pen)

        return ligne

    def dessiner_circuit_base(self, largeur_circuit, hauteur_circuit):
        gauche = self.largeur / 2 - largeur_circuit / 2
        droite = self.largeur / 2 + largeur_circuit / 2
        haut = self.hauteur / 2 - hauteur_circuit / 2
        bas = self.hauteur / 2 + hauteur_circuit / 2

        gauche, haut = self.pos_selon_grid(QPointF(gauche, haut))
        droite, bas = self.pos_selon_grid(QPointF(droite, bas))

        ligne_haut = self.ajouter_ligne(gauche, haut, droite, haut)
        ligne_droite = self.ajouter_ligne(droite, haut, droite, bas)
        ligne_bas = self.ajouter_ligne(droite, bas, gauche, bas)
        ligne_gauche = self.ajouter_ligne(gauche, bas, gauche, haut)
        fil_base = Fil(self.main_window, [ligne_haut, ligne_droite, ligne_bas, ligne_gauche])

        nb_points_x = round((droite - gauche) / self.taille_grid) + 1
        nb_points_y = round((bas - haut) / self.taille_grid) + 1

        self.mat_i0 = haut
        self.mat_j0 = gauche
        matrice_points = np.zeros((nb_points_y, nb_points_x))

        # lignes verticales
        for k in range(nb_points_y):
            y = haut + k * self.taille_grid

            mat_i, mat_j = self.pos_to_mat(droite, y)
            matrice_points[mat_i, mat_j] = 1

            mat_i, mat_j = self.pos_to_mat(gauche, y)
            matrice_points[mat_i, mat_j] = 1

        # lignes horizontales
        for k in range(nb_points_x - 2):
            x = gauche + (k + 1) * self.taille_grid

            mat_i, mat_j = self.pos_to_mat(x, haut)
            matrice_points[mat_i, mat_j] = 1

            mat_i, mat_j = self.pos_to_mat(x, bas)
            matrice_points[mat_i, mat_j] = 1

        return fil_base, matrice_points

    def verifier_collision_fil(self, pos):
        x, y = self.pos_selon_grid(pos)
        pos_i, pos_j = self.pos_to_mat(x, y)

        max_i = self.mat_points.shape[0] - 1
        max_j = self.mat_points.shape[1] - 1

        if QPointF(x, y) == self.dernier_point:
            return None
        elif pos_i <= max_i and pos_i >= 0 and pos_j <= max_j and pos_j >= 0:
            return round(self.mat_points[pos_i, pos_j])
        else:
            return 0

    def clic_gauche_fil(self, pos):
        def mettre_index_mat(debut_ligne, fin_ligne):

            diff_x = fin_ligne.x() - debut_ligne.x()
            diff_y = fin_ligne.y() - debut_ligne.y()
            if abs(diff_x) > abs(diff_y):
                sens_x = 1
                if diff_x < 0:
                    sens_x = -1
                sens_y = 0
            else:
                sens_y = 1
                if diff_y < 0:
                    sens_y = -1
                sens_x = 0

            nb_points = round((diff_x * sens_x + diff_y * sens_y) / self.taille_grid)
            for k in range(nb_points):
                debut_ligne = self.lignes[-1].line().p1()
                fin_ligne = self.lignes[-1].line().p2()

                pos_x = debut_ligne.x() + (k + 1) * self.taille_grid * sens_x
                pos_y = debut_ligne.y() + (k + 1) * self.taille_grid * sens_y
                i, j = self.pos_to_mat(pos_x, pos_y)
                i, j = self.agrandir_matrice(i, j)
                self.mat_points[i, j] = len(self.fils) + 1

        touche = self.verifier_collision_fil(pos)

        if not self.dessine:
            if touche != 0:
                self.dessine = True
                x, y = self.pos_selon_grid(pos)
                ligne = self.ajouter_ligne(x, y, x, y)
                self.lignes.append(ligne)
                self.dernier_point = QPointF(x, y)

                i, j = self.pos_to_mat(x, y)
                self.mat_points[i, j] = len(self.fils) + 1
                self.touche = touche
                self.points_avant_pivot.append(QPointF(x, y))

        elif self.fil_complet:
            debut_ligne = self.lignes[-1].line().p1()
            fin_ligne = self.lignes[-1].line().p2()
            mettre_index_mat(debut_ligne, fin_ligne)

            # Ajouter noeud a premier et dernier point

            nouveau_fil = Fil(self.main_window, self.lignes)
            self.fils.append(nouveau_fil)
            self.lignes = []
            self.points_avant_pivot = []
            self.points_avant_pivot = []
            self.dessine = False

            # TODO Ajouter noeuds
        else:
            debut_ligne = self.lignes[-1].line().p1()
            fin_ligne = self.lignes[-1].line().p2()
            mettre_index_mat(debut_ligne, fin_ligne)
            ligne = self.ajouter_ligne(fin_ligne.x(), fin_ligne.y(), fin_ligne.x(), fin_ligne.y())

            self.points_avant_pivot += self.points_apres_pivot
            self.points_apres_pivot = []
            self.lignes.append(ligne)
            self.dernier_point = QPointF(fin_ligne.x(), fin_ligne.y())
            self.continuer_dessin(pos)

    def clic_droit_fil(self):
        if self.dessine:
            for ligne in self.lignes:

                pos_ligne_x, pos_ligne_y = ligne.line().p2().x(), ligne.line().p2().y()
                mat_i, mat_j = self.pos_to_mat(pos_ligne_x, pos_ligne_y)
                self.mat_points[mat_i, mat_j] = 0
                self.removeItem(ligne)

            points = self.points_avant_pivot + self.points_apres_pivot
            for point in points:
                i, j = self.pos_to_mat(point.x(), point.y())
                if point == points[0]:
                    self.mat_points[i, j] = self.touche
                else:
                    self.mat_points[i, j] = 0

            self.rapetisser_matrice()
            self.dessine = False
            self.lignes = []

    def agrandir_matrice(self, i, j):
        def agrandir(i_ajout, j_ajout, position, axe):
            matrice_ajout = np.zeros((i_ajout, j_ajout))
            self.mat_points = np.insert(self.mat_points, position, matrice_ajout.flatten(), axis=axe)

        mat_size_i, mat_size_j = self.mat_points.shape
        if j < 0:
            agrandir(mat_size_i, 1, 0, 1)
            self.mat_j0 -= self.taille_grid
            return i, j + 1

        elif j > mat_size_j - 1:
            agrandir(mat_size_i, 1, mat_size_j, 1)

        elif i < 0:
            agrandir(1, mat_size_j, 0, 0)
            self.mat_i0 -= self.taille_grid
            return i + 1, j

        elif i > mat_size_i - 1:
            agrandir(1, mat_size_j, mat_size_i, 0)

        return i, j

    def rapetisser_matrice(self):
        len_i = self.mat_points.shape[0]
        len_j = self.mat_points.shape[1]

        for i in reversed(range(len_i)):
            ligne_vide = True
            for j in range(len_j):
                if self.mat_points[i, j] != 0:
                    ligne_vide = False
                    break
            if ligne_vide:
                self.mat_points = np.delete(self.mat_points, i, 0)
                len_i -= 1
            else:
                break

        for i in range(len_i):
            ligne_vide = True
            for j in range(len_j):
                if self.mat_points[0, j] != 0:
                    ligne_vide = False
                    break
            if ligne_vide:
                self.mat_points = np.delete(self.mat_points, 0, 0)
                self.mat_i0 += self.taille_grid
                len_i -= 1
            else:
                break

        for j in reversed(range(len_j)):
            colonne_vide = True
            for i in range(len_i):
                if self.mat_points[i, j] != 0:
                    colonne_vide = False
                    break
            if colonne_vide:
                self.mat_points = np.delete(self.mat_points, j, 1)
                len_j -= 1
            else:
                break

        for j in range(len_j):
            colonne_vide = True
            for i in range(len_i):
                if self.mat_points[i, 0] != 0:
                    colonne_vide = False
                    break
            if colonne_vide:
                self.mat_points = np.delete(self.mat_points, 0, 1)
                self.mat_j0 += self.taille_grid
            else:
                break

    def continuer_dessin(self, pos):
        collision = self.verifier_collision_fil(pos)

        if collision is None:
            pass

        else:
            curs_x, curs_y = self.pos_selon_grid(pos)

            ligne = self.lignes[-1]
            pivot = ligne.line().p1()

            diff_x = curs_x - pivot.x()
            diff_y = curs_y - pivot.y()

            if abs(diff_x) > abs(diff_y):
                sens_x = 1
                if diff_x < 0:
                    sens_x = -1
                sens_y = 0
                x = curs_x
                y = pivot.y()

            else:
                sens_y = 1
                if diff_y < 0:
                    sens_y = -1
                sens_x = 0
                x = pivot.x()
                y = curs_y

            dernier_point = ligne.line().p2()
            if QPointF(x, y) != dernier_point:
                self.fil_complet = False

                ligne_p2_x = pivot.x() + self.taille_grid * sens_x
                ligne_p2_y = pivot.y() + self.taille_grid * sens_y

                ligne_i, ligne_j = self.pos_to_mat(ligne_p2_x, ligne_p2_y)

                while True:
                    ligne_i, ligne_j = self.agrandir_matrice(ligne_i, ligne_j)
                    mat_num = self.mat_points[ligne_i, ligne_j]

                    if mat_num != 0:

                        if mat_num == len(self.fils) + 1:
                            ligne_p2_x -= self.taille_grid * sens_x
                            ligne_p2_y -= self.taille_grid * sens_y
                        else:
                            self.fil_complet = True
                        break

                    if ligne_p2_x == x and ligne_p2_y == y:
                        self.points_apres_pivot.append(QPointF(ligne_p2_x, ligne_p2_y))
                        break

                    ligne_i, ligne_j = self.agrandir_matrice(ligne_i, ligne_j)
                    ligne_i += sens_y
                    ligne_j += sens_x
                    self.points_apres_pivot.append(QPointF(ligne_p2_x, ligne_p2_y))
                    ligne_p2_x += self.taille_grid * sens_x
                    ligne_p2_y += self.taille_grid * sens_y

                ligne.setLine(QLineF(pivot.x(), pivot.y(), ligne_p2_x, ligne_p2_y))

    def mat_to_pos(self, i, j):
        x = (j * self.taille_grid) + self.mat_j0
        y = (i * self.taille_grid) + self.mat_i0

        return x, y

    def pos_to_mat(self, x, y):
        mat_i = round((y - self.mat_i0) / self.taille_grid)
        mat_j = round((x - self.mat_j0) / self.taille_grid)

        return mat_i, mat_j

    def pos_selon_grid(self, pos):
        x = round(pos.x() / self.taille_grid) * self.taille_grid
        x = max(min(x, math.floor(self.scene_size.width() / self.taille_grid) * self.taille_grid), 0)
        y = round(pos.y() / self.taille_grid) * self.taille_grid
        y = max(min(y, math.floor(self.scene_size.height() / self.taille_grid) * self.taille_grid), 0)

        return x, y


class GraphicsView(QGraphicsView):
    def __init__(self, scene, main_window):
        super().__init__(scene)
        self.scene = scene
        self.viewport().setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.scene.clic_gauche_fil(event.position())

        if event.button() == Qt.RightButton:
            self.scene.clic_droit_fil()

    def mouseMoveEvent(self, event):
        if self.scene.dessine:
            self.scene.continuer_dessin(event.position())

    """
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.main_window.dessine:
            self.main_window.confirmer_fil()
            self.main_window.points = []
            self.main_window.lignes = []
    """