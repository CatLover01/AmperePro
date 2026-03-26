from PySide6.QtCore import QSize, QPointF, QRect, QFile, QTextStream
from PySide6.QtGui import QColorConstants, QPen, Qt, QBrush, QAction, QIcon
from PySide6.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsView, QPushButton, QDialog, QHBoxLayout
import math
import numpy as np
import Composantes
from a_propos import AProposWindow
from docs import DocumentationWindow


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

        self.fenetre_doc = DocumentationWindow()
        self.fenetre_a_propos = AProposWindow()

        self.largeur = self.scene_size.width()
        self.hauteur = self.scene_size.height()
        # La distance entre chaque ligne dans le grid
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

        #Menubar
        barre_menu = self.menuBar()
        menu_options = barre_menu.addMenu("Options")
        menu_naviguer = barre_menu.addMenu("Naviguer")
        menu_infos = barre_menu.addMenu("Aide")

        #sauvegarder
        sauvegarder_action = QAction("Sauvegarder", self)
        sauvegarder_action.setShortcut("Ctrl+S")
        sauvegarder_action.setIcon(QIcon("images/menubar/disquette.png"))
        menu_options.addAction(sauvegarder_action)
        sauvegarder_action.triggered.connect(self.sauvegarder_triggered)

        #rollback
        annuler_action = QAction("RollBack", self)
        annuler_action.setShortcut("Ctrl+R")
        annuler_action.setIcon(QIcon("images/menubar/rollback.png"))
        menu_options.addAction(annuler_action)

        #Quitter
        quitter_action = QAction("Quitter", self)
        quitter_action.setShortcut("Ctrl+Q")
        quitter_action.triggered.connect(self.quitter_triggered)
        menu_naviguer.addAction(quitter_action)

        #retour au menu principal
        retour_action = QAction("Menu Principal", self)
        retour_action.setShortcut("Ctrl+M")
        retour_action.setIcon(QIcon("images/menubar/menu_principal.png"))
        retour_action.triggered.connect(self.retour_menu_triggered)
        menu_naviguer.addAction(retour_action)

        #à propos
        a_propos_action = QAction("À propos", self)
        a_propos_action.setShortcut("Ctrl+A")
        a_propos_action.setIcon(QIcon("images/menubar/a_propos.png"))
        a_propos_action.triggered.connect(self.ouvrir_a_propos)
        menu_infos.addAction(a_propos_action)

        #documentation
        documentation_action = QAction("En savoir plus", self)
        documentation_action.setShortcut("Ctrl+D")
        documentation_action.setIcon(QIcon("images/menubar/docu.png"))
        documentation_action.triggered.connect(self.ouvrir_docu)
        menu_infos.addAction(documentation_action)

    def sauvegarder_triggered(self):
        #TODO: implémenter code pour enregistrer circuit dans bd
        pass

    def retour_menu_triggered(self):
        avertissement = QDialog()
        avertissement.setWindowTitle("Voulez-vous Sauvegarder?")
        avertissement.setModal(True)

        layout_dialogue = QHBoxLayout()
        avertissement.setLayout(layout_dialogue)

        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(avertissement.close)

        bouton_sauvegarder_et_quitter = QPushButton("Sauvegarder et Quitter")
        bouton_sauvegarder_et_quitter.clicked.connect(lambda: self.sauvegarder_et_menu(avertissement))

        bouton_quitter_sans_sauvegarder = QPushButton("quitter sans sauvegarder")
        bouton_quitter_sans_sauvegarder.clicked.connect(lambda: self.menu_sans_sauvegarder(avertissement))

        layout_dialogue.addWidget(bouton_sauvegarder_et_quitter)
        layout_dialogue.addWidget(bouton_quitter_sans_sauvegarder)
        layout_dialogue.addWidget(bouton_annuler)

        avertissement.exec()

    def quitter_triggered(self):
        avertissement = QDialog()
        avertissement.setWindowTitle("Voulez-vous Sauvegarder?")
        avertissement.setModal(True)

        layout_dialogue = QHBoxLayout()
        avertissement.setLayout(layout_dialogue)

        #comme si on avait jamais souhaité quitter
        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(avertissement.close)

        bouton_sauvegarder_et_quitter = QPushButton("Sauvegarder et Quitter")
        bouton_sauvegarder_et_quitter.clicked.connect(lambda: self.sauvegarder_et_quitter(avertissement))

        #ferme les deux fenêtres (dialogue et principale)
        bouton_quitter_sans_sauvegarder = QPushButton("quitter sans sauvegarder")
        bouton_quitter_sans_sauvegarder.clicked.connect(avertissement.close)
        bouton_quitter_sans_sauvegarder.clicked.connect(self.close)

        layout_dialogue.addWidget(bouton_sauvegarder_et_quitter)
        layout_dialogue.addWidget(bouton_quitter_sans_sauvegarder)
        layout_dialogue.addWidget(bouton_annuler)
        avertissement.exec()

    def retour_menu(self):
        # TODO: faire en sorte que l'on revienne au menu principal
        pass

    def sauvegarder_et_menu(self, dialog):
        #ferme QDialog, sauvegarde et retourne au menu principal
        dialog.close()
        self.sauvegarder_triggered()
        self.retour_menu()

    def menu_sans_sauvegarder(self, dialog):
        dialog.close()
        self.retour_menu()

    def sauvegarder_et_quitter(self, dialog):
        # sauvegarde le circuit et ferme tout
        self.close()
        dialog.close()
        self.sauvegarder_triggered()

    def ouvrir_a_propos(self):
        # ouverture du stylesheet
        style_propos = QFile("StyleSheet/StylePropos.qss")
        if style_propos.open(QFile.OpenModeFlag.ReadOnly):
            stream = QTextStream(style_propos)
            self.fenetre_a_propos.setStyleSheet(stream.readAll())
            style_propos.close()

        self.fenetre_a_propos.show()

    def ouvrir_docu(self):
        # ouverture du Stylesheet
        style_docu = QFile("StyleSheet/StyleDocumentation.qss")
        if style_docu.open(QFile.OpenModeFlag.ReadOnly):
            stream_docu = QTextStream(style_docu)
            self.fenetre_doc.setStyleSheet(stream_docu.readAll())
            style_docu.close()

            self.fenetre_doc.show()

    # première méthode non liée au menu à propos
    def dessiner_fond_grid(self):
        self.scene.setBackgroundBrush(QColorConstants.White)
        self.scene.setSceneRect(0, 0, self.largeur, self.hauteur)

        largeur_crayon = 1

        pen = QPen()
        pen.setWidthF(largeur_crayon)
        pen.setColor(QColorConstants.Gray)

        # Lignes horizontales
        for i in range(math.ceil(self.hauteur / self.taille_grid) + 1):
            x1 = 0
            x2 = self.largeur
            y = i * self.taille_grid

            self.scene.addLine(x1, y, x2, y, pen)

        # Lignes verticales
        for i in range(math.ceil(self.largeur / self.taille_grid) + 1):
            y1 = 0
            y2 = self.hauteur
            x = i * self.taille_grid

            self.scene.addLine(x, y1, x, y2, pen)

    def ajouter_ligne(self, xi, yi, x, y):
        pen = QPen(QColorConstants.Black)
        largeur_crayon = 3
        pen.setWidthF(largeur_crayon)
        ligne = self.scene.addLine(xi, yi, x, y, pen)

        return ligne

    def dessiner_circuit_base(self, largeur_circuit, hauteur_circuit):
        gauche = self.largeur / 2 - largeur_circuit / 2
        droite = self.largeur / 2 + largeur_circuit / 2
        haut = self.hauteur / 2 - hauteur_circuit / 2
        bas = self.hauteur / 2 + hauteur_circuit / 2

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

            # TODO débuter le dessin

    def pos_i_j(self, x, y):
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


app = QApplication()
window = Window()
window.show()
app.exec()
