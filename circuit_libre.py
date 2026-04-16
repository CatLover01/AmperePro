from PySide6.QtCore import QSize, QPointF, QRect, QFile, QTextStream, QLineF, QRectF
from PySide6.QtGui import QColorConstants, QPen, Qt, QBrush, QAction, QIcon, QPixmap, QColor
from PySide6.QtWidgets import (QGraphicsScene, QGraphicsView, QPushButton, QDialog,
                               QHBoxLayout, QToolBar, QLabel, QGraphicsPixmapItem, QGraphicsRectItem)
import math
import numpy as np
import datetime

from a_propos import AProposWindow
from docs import DocumentationWindow
from Composantes import toolbar_composantes
from sauvegarde import Sauvegarde, CircuitLibre


class Noeud:
    def __init__(self):
        self.voltage = 0
        self.info_voisins = []

    def ajouter_info(self, fil, noeud_voisin, main_window):
        voisin_index = main_window.noeuds.index(noeud_voisin)
        self.info_voisins.append([fil, voisin_index])

    def enlever_info_fil(self, fil):
        for k in range(len(self.info_voisins)):
            if self.info_voisins[k][0] == fil:
                del self.info_voisins[k]
                break


class Fil:
    def __init__(self, main_window, points):
        self.main_window = main_window
        self.points = points
        self.noeuds = None

        # self.resistance, self.tension = self.calculs()
        self.composantes = []

        self.tension = 0
        self.resistance = 0

    def calculs(self):
        res = 0
        tension = 0
        for composante in self.composantes:
            if hasattr(composante, 'resistance'):
                res += composante.resistance
            if hasattr(composante, 'tension'):
                tension += composante.tension
        return res, tension

    def ajouter_noeud(self, pos: QPointF, noeud: Noeud):
        index_point = self.points.index(pos)
        points_avant = self.points[:index_point]
        points_apres = self.points[index_point + 1:]

        if self.noeuds is None:
            self.points = points_apres + points_avant
            self.noeuds = [noeud, noeud]
        else:
            comp_avant = []
            comp_apres = []
            for i in range(len(self.composantes)):
                pos_comp = self.composantes[i].point_debut
                index_comp_points = self.points.index(pos_comp)

                if index_point < index_comp_points:
                    comp_avant = self.composantes[:i]
                    comp_apres = self.composantes[i:]
                    break

            nouveau_fil = Fil(self.main_window, points_apres)
            nouveau_fil.noeuds = [noeud, self.noeuds[1]]
            nouveau_fil.composantes = comp_apres
            self.main_window.fils.append(nouveau_fil)

            for point_apres in points_apres:
                i, j = self.main_window.pos_to_mat(point_apres.x(), point_apres.y())
                self.main_window.mat_points[i, j] = len(self.main_window.fils)

            self.noeuds[0].enlever_info_fil(self)
            self.noeuds[0].ajouter_info(self, noeud, self.main_window)

            if self.noeuds[0] != self.noeuds[1]:
                self.noeuds[1].enlever_info_fil(self)
            self.noeuds[1].ajouter_info(nouveau_fil, noeud, self.main_window)

            noeud.ajouter_info(self, self.noeuds[0], self.main_window)
            noeud.ajouter_info(self, self.noeuds[1], self.main_window)

            self.composantes = comp_avant
            self.noeuds = [self.noeuds[0], noeud]
            self.points = points_avant


class Circuit(QGraphicsScene):
    def __init__(self, mainwindow, id: str, mat: list | None):
        super().__init__()
        self.main_window = mainwindow
        self.scene_size = QSize(500, 500)
        self.graphics_view = GraphicsView(self, mainwindow)
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
        self.noeuds = []
        self.points_avant_pivot = []
        self.fil_touche_depart = None
        self.fil_complet = False

        # if mat is None:
        # matrice devrait être initialiser, sinon on utilise elle passer par paramètre
        fil_base, self.mat_points = self.dessiner_circuit_base(largeur_fil_base, hauteur_fil_base)
        self.fils = [fil_base]

        self.save = Sauvegarde()
        self.id = id

        # listes pour le rollback
        self.ajouts = []
        self.jetes = []
        # les ajouts seront 1, les jetés seront 2, composantes modifiées seront 3
        self.operations = []

        self.allouer_fermeture = "oui"

        # pour les composantes
        self.toolbar = None
        self.selection = None
        self.composante_selectionnee = None
        self.image_composante = None
        self.couleur_recouvre = None
        self.accepter_modification = True
        self.accepter_positionnement = False
        self.zones_surbrillance = []
        self.composantes = []
        self.nombre_de_rotations = 0

        # Menubar
        self.barre_menu = self.main_window.menuBar()
        self.menu_options = self.barre_menu.addMenu("Options")
        self.menu_naviguer = self.barre_menu.addMenu("Naviguer")

        # sauvegarder
        sauvegarder_action = QAction("Sauvegarder", self)
        sauvegarder_action.setShortcut("Ctrl+S")
        sauvegarder_action.setIcon(QIcon("images/menubar/disquette.png"))
        self.menu_options.addAction(sauvegarder_action)
        sauvegarder_action.triggered.connect(self.sauvegarder_triggered)

        # rollback
        self._annuler_action = QAction("RollBack", self)
        self._annuler_action.setShortcut("Ctrl+Z")
        self._annuler_action.setIcon(QIcon("images/menubar/rollback.png"))
        self._annuler_action.triggered.connect(self.rollback_triggered)
        self._annuler_action.setEnabled(False)
        self.menu_options.addAction(self._annuler_action)

        # Quitter
        quitter_action = QAction("Quitter", self)
        quitter_action.setShortcut("Ctrl+Q")
        quitter_action.triggered.connect(self.main_window.close)
        self.menu_naviguer.addAction(quitter_action)

    def sauvegarder_triggered(self):
        self.save.modifie_circuit(self.id, self.mat_points.tolist())

    def rollback_possible(self):
        # à partir du moment où un élément est dans opérations, on peut rollback
        if self.operations:
            self._annuler_action.setEnabled(True)
        else:
            # si on a rollback toutes les opérations, on ne peut plus le faire
            self._annuler_action.setEnabled(False)

    def rollback_triggered(self):
        dernier = self.operations[-1]
        if dernier == 1:
            dernier_ajout = self.ajouts[-1]
            if dernier_ajout == "fil":
                dernier_fil = self.fils.pop()
                dernier_fil.enlever_lignes()
                valeur_fil_retire = np.max(self.mat_points)
                self.mat_points[self.mat_points == valeur_fil_retire] = 0
                # TODO : mettre à jour la vérification de collisions pour fils après qu'un ait été retiré
            else:
                # enlever la dernière composante du dessin (donc les 3 dernières infos ajoutées)
                longueur = len(self.composantes)
                # on retire tout ce qui est lié à ce qui est enlevé de self.composantes
                self.composantes.pop(longueur-1)
                image_composante_supprimee = self.composantes.pop(longueur - 2)
                self.composantes.pop(longueur - 3)

                # on retire de la scène l'image de la composante
                self.removeItem(image_composante_supprimee)
                # le dernier ajout est donc une composante

            self.ajouts.pop()

        elif dernier == 2:
            dernier_jete = self.jetes[-1]
            if dernier_jete == "fil":
                # replacer le fil enlevé
                pass
            else:
                # replacer la dernière composante
                pass

            self.jetes.pop()

        else:
            # annuler la plus récente modification à une composante.
            pass

        self.operations.remove(dernier)
        self.rollback_possible()

    def quitter_triggered(self):
        avertissement = QDialog()
        # on ne peut pas cliquer sur le "x" du QDialog (ainsi on gère à 100% le clsoe event)
        avertissement.setWindowFlags(avertissement.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
        avertissement.setWindowTitle("Voulez-vous Sauvegarder?")
        avertissement.setModal(True)

        layout_dialogue = QHBoxLayout()
        avertissement.setLayout(layout_dialogue)

        # comme si on n'avait jamais souhaité quitter
        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(avertissement.close)
        bouton_annuler.clicked.connect(self.refuser_fermeture)

        bouton_sauvegarder_et_quitter_total = QPushButton("Sauvegarder et Quitter")
        bouton_sauvegarder_et_quitter_total.clicked.connect(lambda: self.sauvegarder_et_quitter(avertissement))

        # ferme les deux fenêtres (dialogue et principale)
        bouton_quitter_sans_sauvegarder = QPushButton("quitter sans sauvegarder")
        bouton_quitter_sans_sauvegarder.clicked.connect(avertissement.close)
        layout_dialogue.addWidget(bouton_sauvegarder_et_quitter_total)
        layout_dialogue.addWidget(bouton_quitter_sans_sauvegarder)
        layout_dialogue.addWidget(bouton_annuler)
        avertissement.exec()

        return self.allouer_fermeture

    def sauvegarder_et_quitter(self, dialog):
        # sauvegarde le circuit et ferme tout
        dialog.close()
        self.sauvegarder_triggered()
        self.main_window.close()

    def refuser_fermeture(self):
        self.allouer_fermeture = "non"

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

        nb_points_x = round((droite - gauche) / self.taille_grid) + 1
        nb_points_y = round((bas - haut) / self.taille_grid) + 1

        self.mat_i0 = haut
        self.mat_j0 = gauche
        matrice_points = np.zeros((nb_points_y, nb_points_x))

        points_droite = []
        points_gauche = []
        # lignes verticales
        for k in range(nb_points_y):
            y = haut + k * self.taille_grid

            mat_i, mat_j = self.pos_to_mat(droite, y)
            matrice_points[mat_i, mat_j] = 1
            points_droite.append(QPointF(droite, y))

            mat_i, mat_j = self.pos_to_mat(gauche, y)
            matrice_points[mat_i, mat_j] = 1
            points_gauche.append(QPointF(gauche, y))

        points_haut = []
        points_bas = []
        # lignes horizontales
        for k in range(nb_points_x - 2):
            x = gauche + (k + 1) * self.taille_grid

            mat_i, mat_j = self.pos_to_mat(x, haut)
            matrice_points[mat_i, mat_j] = 1
            points_haut.append(QPointF(x, haut))

            mat_i, mat_j = self.pos_to_mat(x, bas)
            matrice_points[mat_i, mat_j] = 1
            points_bas.append(QPointF(x, bas))

        points_bas.reverse()
        points_gauche.reverse()
        points = points_haut + points_droite + points_bas + points_gauche
        fil_base = Fil(self, points)

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
        def get_points_ligne(debut_ligne, fin_ligne):
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

            points = []
            for k in range(nb_points):
                pos_x = debut_ligne.x() + (k + 1) * self.taille_grid * sens_x
                pos_y = debut_ligne.y() + (k + 1) * self.taille_grid * sens_y
                points.append(QPointF(pos_x, pos_y))

            return points

        def mettre_index_mat(ligne, index_fil):
            debut_ligne = ligne.line().p1()
            fin_ligne = ligne.line().p2()
            points = get_points_ligne(debut_ligne, fin_ligne)

            i_fin, j_fin = self.pos_to_mat(points[-1].x(), points[-1].y())
            self.agrandir_matrice(i_fin, j_fin)

            for point in points:
                i, j = self.pos_to_mat(point.x(), point.y())
                if self.mat_points[i, j] == 0:
                    self.mat_points[i, j] = index_fil

            return debut_ligne, fin_ligne, points

        fil_touche = self.verifier_collision_fil(pos)

        if not self.dessine:
            if fil_touche != 0:
                self.dessine = True
                x, y = self.pos_selon_grid(pos)
                ligne = self.ajouter_ligne(x, y, x, y)
                self.lignes.append(ligne)
                self.dernier_point = QPointF(x, y)

                self.fil_touche_depart = fil_touche
                self.points_avant_pivot.append(QPointF(x, y))

        elif self.fil_complet:
            debut_ligne, fin_ligne, points_apres_pivot = mettre_index_mat(self.lignes[-1], len(self.fils) + 1)

            # Ajouter noeud a premier et dernier point
            points = self.points_avant_pivot + points_apres_pivot

            noeud_debut = Noeud()
            self.noeuds.append(noeud_debut)
            noeud_fin = Noeud()
            self.noeuds.append(noeud_fin)

            nouveau_fil = Fil(self, points[1:-1])
            self.fils.append(nouveau_fil)
            nouveau_fil.noeuds = [noeud_debut, noeud_fin]
            noeud_debut.ajouter_info(nouveau_fil, noeud_fin, self)
            noeud_fin.ajouter_info(nouveau_fil, noeud_debut, self)

            fil_noeud1 = self.fils[self.fil_touche_depart - 1]
            fil_noeud1.ajouter_noeud(points[0], noeud_debut)
            # ajouter les noeuds à la matrice (à ij avoir ref aux noeuds)

            fil_noeud2 = self.fils[self.verifier_collision_fil(fin_ligne) - 1]
            fil_noeud2.ajouter_noeud(fin_ligne, noeud_fin)

            self.rapetisser_matrice()

            self.lignes = []
            self.points_avant_pivot = []
            self.dessine = False

        else:
            debut_ligne, fin_ligne, points_apres_pivot = mettre_index_mat(self.lignes[-1], len(self.fils) + 1)
            ligne = self.ajouter_ligne(fin_ligne.x(), fin_ligne.y(), fin_ligne.x(), fin_ligne.y())

            self.points_avant_pivot += points_apres_pivot
            self.lignes.append(ligne)
            self.dernier_point = QPointF(fin_ligne.x(), fin_ligne.y())
            self.continuer_dessin(pos)
            self.ajouts.append("fil")
            self.operations.append(1)
            self.rollback_possible()

    def calculer_voltage(self):
        mat_A = np.zeros((len(self.noeuds) - 1, len(self.noeuds) - 1))
        mat_B = np.zeros((len(self.noeuds) - 1, 1))

        noeud_zero = self.noeuds[-1]
        noeud_zero.voltage = 0
        for i in range(len(self.noeuds) - 1):
            j_noeud = i
            for info in self.noeuds[i].info_voisins:
                j_voisin = info[1]
                fil = info[0]

                mat_A[i, j_noeud] += 1 / fil.resistance
                mat_B[i, 0] -= fil.tension / fil.resistance
                if self.noeuds[j_voisin] != noeud_zero:
                    mat_A[i, j_voisin] -= 1 / fil.resistance

        mat_X = np.linalg.solve(mat_A, mat_B)
        for i in range(len(mat_X)):
            self.noeuds[i].voltage = mat_X[i][0]

    def clic_droit_fil(self):
        if self.dessine:
            for ligne in self.lignes:
                self.removeItem(ligne)

            for point in self.points_avant_pivot:
                i, j = self.pos_to_mat(point.x(), point.y())
                if point == self.points_avant_pivot[0]:
                    self.mat_points[i, j] = self.fil_touche_depart
                else:
                    self.mat_points[i, j] = 0

            self.points_avant_pivot = []
            self.rapetisser_matrice()

            self.dessine = False
            self.lignes = []

    def agrandir_matrice(self, i, j):
        def agrandir(i_ajout, j_ajout, position, axe):
            matrice_ajout = np.zeros((i_ajout, j_ajout))
            if position == 0:
                matrices = (matrice_ajout, self.mat_points)
            else:
                matrices = (self.mat_points, matrice_ajout)

            self.mat_points = np.concatenate(matrices, axis=axe)

        mat_size_i, mat_size_j = self.mat_points.shape
        if j < 0:
            agrandir(mat_size_i, abs(j), 0, 1)
            self.mat_j0 -= self.taille_grid * abs(j)
            return i, j + 1

        elif j > mat_size_j - 1:
            agrandir(mat_size_i, j - mat_size_j + 1, 1, 1)

        elif i < 0:
            agrandir(abs(i), mat_size_j, 0, 0)
            self.mat_i0 -= self.taille_grid * abs(i)
            return i + 1, j

        elif i > mat_size_i - 1:
            agrandir(i - mat_size_i + 1, mat_size_j, 1, 0)

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
                    if ligne_i < 0 or ligne_j < 0:
                        mat_num = 0
                    else:
                        try:
                            mat_num = self.mat_points[ligne_i, ligne_j]
                        except IndexError:
                            mat_num = 0

                    if mat_num != 0:

                        if mat_num == len(self.fils) + 1:
                            ligne_p2_x -= self.taille_grid * sens_x
                            ligne_p2_y -= self.taille_grid * sens_y
                        else:
                            self.fil_complet = True

                        break

                    if ligne_p2_x == x and ligne_p2_y == y:
                        break

                    ligne_i += sens_y
                    ligne_j += sens_x
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

    def creer_toolbar(self):
        self.toolbar = QToolBar()
        # ne permet pas à l'utilisateur de cacher la toolbar.
        self.toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

        class ToolbarButton(QPushButton):
            def __init__(self, nom: str):
                super().__init__()
                self.nom = nom

            def enterEvent(self, event):
                self.setToolTip(self.nom)

        # Ajoute le bouton main à la toolbar
        main_icone = QIcon("images/toolbar/main.png")
        main_bouton = ToolbarButton("Main")
        main_bouton.setIcon(main_icone)
        main_bouton.setIconSize(QSize(45, 45))
        main_bouton.clicked.connect(self.main_click)
        self.toolbar.addWidget(main_bouton)
        
        # ajoute le bouton poubelle à la toolbar
        poubelle_icone = QIcon("images/toolbar/poubelle.webp")
        poubelle_bouton = ToolbarButton("Main")
        poubelle_bouton.setIcon(poubelle_icone)
        poubelle_bouton.setIconSize(QSize(45, 45))
        poubelle_bouton.clicked.connect(self.poubelle_click)
        self.toolbar.addWidget(poubelle_bouton)

        # ajoute le bouton fil à la toolbar
        fil_icone = QIcon("images/toolbar/fil.webp")
        fil_bouton = ToolbarButton("Fil")
        fil_bouton.setIcon(fil_icone)
        fil_bouton.setIconSize(QSize(45, 45))
        fil = "fil"
        fil_bouton.clicked.connect(self.fil_click)
        self.toolbar.addWidget(fil_bouton)

        # Ajouter un bouton dans la toolbar pour chaque composante
        for composante in toolbar_composantes.values():
            bouton = ToolbarButton(composante.nom)
            bouton.setIcon(QIcon(composante.image_toolbar))
            bouton.setIconSize(QSize(45, 45))
            bouton.clicked.connect(lambda _, c=composante: self.composante_toolbar_clicked(c))
            self.toolbar.addWidget(bouton)

        self.main_window.addToolBar(self.toolbar)

    def supprimer_toolbar(self):
        self.main_window.removeToolBar(self.toolbar)
        self.toolbar.deleteLater()
        self.toolbar = None

    def main_click(self):
        self.selection = "main"
        
    def clic_gauche_main(self):
        pass
    
    def poubelle_click(self):
        self.selection = "poubelle"

        if hasattr(self, "zones_surbrillance"):
            for item in self.zones_surbrillance:
                self.removeItem(item)

        emplacements_composantes = self.composantes[2::3]
        # on indique "l'aire" de chaques composantes
        for emplacement in emplacements_composantes:
            # on doit passer du point central au coin supérieur gauche
            coin_sup_gauche_x = emplacement.x() - self.taille_grid
            coin_sup_gauche_y = emplacement.y() - self.taille_grid
            zone_surbrillance = QGraphicsRectItem(coin_sup_gauche_x, coin_sup_gauche_y, self.taille_grid * 2,
                                                  self.taille_grid * 2)
            zone_surbrillance.setOpacity(0.3)
            zone_surbrillance.setZValue(2)
            zone_surbrillance.setBrush(QColor(218, 44, 44))
            self.addItem(zone_surbrillance)
            self.zones_surbrillance.append(zone_surbrillance)

    def composante_toolbar_clicked(self, composante):
        if composante in toolbar_composantes.values():
            self.selection = "composante"
            self.composante_selectionnee = composante

            if self.image_composante is not None:
                self.removeItem(self.image_composante)
                self.image_composante = None

            pixmap = QPixmap(self.composante_selectionnee.image_circuit)
            pixmap_scalise = pixmap.scaled(self.taille_grid * 2, self.taille_grid * 2)
            self.image_composante = QGraphicsPixmapItem(pixmap_scalise)
            self.image_composante.setPos(self.taille_grid, self.taille_grid)
            self.image_composante.setOffset(-self.taille_grid, -self.taille_grid)
            self.addItem(self.image_composante)
            self.accepter_modification = True

            perimetre = self.image_composante.boundingRect()
            self.couleur_recouvre = QGraphicsRectItem(perimetre, self.image_composante)
            self.couleur_recouvre.setOpacity(0.3)
            self.couleur_recouvre.setZValue(1)
            self.couleur_recouvre.setBrush(QColor(218, 44, 44))
            self.addItem(self.couleur_recouvre)

    def fil_click(self):
        self.selection = "fil"
        if self.image_composante is not None:
            self.removeItem(self.image_composante)
            self.image_composante = None
        self.nombre_de_rotations = 0

    def inserer_composante(self, composante):
        if self.image_composante:
            position = self.image_composante.scenePos()
            # on enleve la surbrillance
            self.removeItem(self.couleur_recouvre)
            self.couleur_recouvre = None
            # on ajoute le type de composante, son image sur la scène et sa position à self.composantes
            self.composantes.append(composante)
            self.composantes.append(self.image_composante)
            self.composantes.append(position)
            # on reset les variables liées à l'ajout de composantes
            self.accepter_modification = False
            self.image_composante = None
            # on update les infos liées à l'ajout pour le rollback
            self.operations.append(1)
            self.ajouts.append("composante")
            self.nombre_de_rotations = 0
            self.rollback_possible()


    def clic_droit_composante(self):
        self.image_composante.setRotation(self.image_composante.rotation() - 90)
        self.nombre_de_rotations += 1

    def sens_composante(self):
        sens = self.nombre_de_rotations % 4
        # de base l'image "pointe" à droite. 1 clic droit et elle pointe en haut, 2 à gauche, 3 en bas et 4 on redémarre
        if sens == 0:
            return "droite"
        elif sens == 1:
            return "haut"
        elif sens == 2:
            return"gauche"
        else:
            return "bas"

    def valider_position(self):
        position = self.image_composante.scenePos()
        sens = self.sens_composante()
        x = position.x()
        y = position.y()
        verdict = self.deja_occupe(position)

        # chacune de ces collisions = 0 si elle n'existe pas (donc si aucun fil n'est présent à l'endroit vérifié).
        collision_centre = self.verifier_collision_fil(position)
        collision_droite = self.verifier_collision_fil(QPointF(x + self.taille_grid, y))
        collision_gauche = self.verifier_collision_fil(QPointF(x - self.taille_grid, y))
        collision_haut = self.verifier_collision_fil(QPointF(x, y + self.taille_grid))
        collision_bas = self.verifier_collision_fil(QPointF(x, y - self.taille_grid))

        if collision_centre == 0 or verdict == "refuser":
            # on ne peut pas mettre une composante dans le vide. si elle ne touche aucun fil (collision_centre = 0),
            # on ignore. La composante ne peut pas non plus toucher plus d'un fil, d'où les 4 autres conditions
            self.accepter_positionnement = False

        else:
            if sens == "droite" or sens == "gauche":
                # si la composante est à l'horizontal, on veut qu'il y ait un fil à droite et à gauche d'elle, mais
                # pas directement en haut ou en bas
                if collision_droite == 0 or collision_gauche == 0 or collision_haut != 0 or collision_bas != 0:
                    self.accepter_positionnement = False
                else:
                    self.accepter_positionnement = True

            else:
                # raisonnement inverse pour la verticale
                if collision_haut == 0 or collision_bas == 0 or collision_droite != 0 or collision_gauche != 0:
                    self.accepter_positionnement = False
                else:
                    self.accepter_positionnement = True

        self.couleur_image()

    def deja_occupe(self, position):
        # on veut la position des composantes déjà installées. Elle est données aux index impairs de self.composantess
        refusees= self.composantes[2::3]

        positions_refusees = []
        for i in refusees:
            x_position = i.x()
            y_position = i.y()

            # on ne veut pas ajouter une composante dans le "carré" d'une autre
            positions_refusees.append(QPointF(x_position, y_position))
            positions_refusees.append(QPointF(x_position + self.taille_grid, y_position))
            positions_refusees.append(QPointF(x_position - self.taille_grid, y_position))
            positions_refusees.append(QPointF(x_position, y_position + self.taille_grid))
            positions_refusees.append(QPointF(x_position, y_position - self.taille_grid))

            # il ne peut pas y avoir 2 composantes "back à back" sur le même fil"
            if self.sens_composante() == "droite" or self.sens_composante() == "gauche":
                positions_refusees.append(QPointF(x_position + 2 * self.taille_grid, y_position))
                positions_refusees.append(QPointF(x_position - 2 * self.taille_grid, y_position))

            else:
                positions_refusees.append(QPointF(x_position, y_position + 2 * self.taille_grid))
                positions_refusees.append(QPointF(x_position , y_position - 2 * self.taille_grid))

        verdict = "accepter"
        if QPointF(position.x(), position.y()) in positions_refusees:
            verdict = "refuser"

        return verdict

    def couleur_image(self):
        # vert si on peut placer la composante, rouge sinon
        if not self.accepter_positionnement:
            self.couleur_recouvre.setBrush(QColor(218, 44, 44))
        else:
            self.couleur_recouvre.setBrush(QColor(44, 246, 44))

    def jeter_composante(self, position):
        a_jeter = None
        for zone in self.zones_surbrillance:
            position_curseur_traduite = zone.mapFromScene(position)
            if zone.contains(position_curseur_traduite):
                a_jeter = zone
                break

        if a_jeter:
            point_a_trouver = a_jeter.mapToScene(a_jeter.rect().center())

            index = 0
            for element in self.composantes:
                if point_a_trouver == element:
                    break
                index +=1

            # on retire tout ce qui est lié à ce qui est enlevé de self.composantes
            position_supprimee = self.composantes.pop(index)
            image_composante_supprimee = self.composantes.pop(index-1)
            composante_supprimee = self.composantes.pop(index-2)

            # on retire de la scène l'image de la composante et le carré rouge associé
            self.removeItem(image_composante_supprimee)
            self.removeItem(a_jeter)

            # on note ce qu'on vient d'enlever pour le rollback
            self.operations.append(2)
            self.jetes.append(composante_supprimee)
            self.jetes.append(image_composante_supprimee)
            self.jetes.append(position_supprimee)

        
    def deplacer_composante(self, position):
        x,y = self.pos_selon_grid(position)
        pos_max_x = self.scene_size.width() - self.taille_grid
        pos_max_y = self.scene_size.height() - self.taille_grid
        # évite que la composante soit à moitié sortie de la grid
        if x < self.taille_grid:
            x = self.taille_grid
        if y < self.taille_grid:
            y = self.taille_grid
        if x > pos_max_x:
            x = pos_max_x
        if y > pos_max_y:
            y = pos_max_y
        self.image_composante.setPos(x,y)


class GraphicsView(QGraphicsView):

    def __init__(self, scene, main_window):
        super().__init__(scene)
        self.scene = scene
        self.viewport().setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.scene.selection == "fil":
                self.scene.clic_gauche_fil(event.position())

            elif self.scene.selection == "main":
                pass
                #TODO: si on souhaite utiliser la main, connecter cela à def clic_gauche_main

            elif self.scene.selection == "composante" and self.scene.accepter_positionnement == True:
                self.scene.inserer_composante(self.scene.composante_selectionnee)
                
            elif self.scene.selection == "poubelle":
                self.scene.jeter_composante(event.position())

        if event.button() == Qt.RightButton:
            if self.scene.selection == "fil":
                self.scene.clic_droit_fil()
            if self.scene.selection == "composante" and self.scene.accepter_modification == True:
                self.scene.clic_droit_composante()
                self.scene.valider_position()

    def mouseMoveEvent(self, event):
        if self.scene.selection == "fil" and self.scene.dessine:
            self.scene.continuer_dessin(event.position())
        elif self.scene.selection == "composante" and self.scene.accepter_modification == True:
            position_scene = self.mapToScene(event.position().toPoint())
            self.scene.deplacer_composante(position_scene)
            self.scene.valider_position()


class LoisPhysiques:
    @staticmethod
    def loi_ohm(resistance, tension):
        intensite = tension / resistance
        return intensite

    @staticmethod
    def resistance_serie(*args):
        res_eq = 0
        for arg in args:
            res_eq += arg
        return res_eq

    @staticmethod
    def resistance_parallele(*args):
        res_eq = 0
        for arg in args:
            res_eq += 1 / arg
        return 1 / res_eq
